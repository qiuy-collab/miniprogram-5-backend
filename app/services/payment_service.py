import hashlib
import secrets
import uuid
from decimal import Decimal, InvalidOperation
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.errors.codes import ErrorCode
from app.errors.exceptions import AppError
from app.repositories.checkout_repository import CheckoutRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.wechat_repository import WechatRepository
from app.services.utils import now_ms


class PaymentService:
    @staticmethod
    def prepare_wechat_payment(user_id: str, checkout_created_at: int, client_ip: str) -> dict:
        if not settings.wechat_mch_id or not settings.wechat_mch_key or not settings.wechat_pay_notify_url:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "微信支付配置未完成", 503)

        try:
            with SessionLocal() as db:
                checkout_repo = CheckoutRepository(db)
                product_repo = ProductRepository(db)
                wechat_repo = WechatRepository(db)

                session = PaymentService._get_checkout_session(checkout_repo, user_id, checkout_created_at)
                item_rows = checkout_repo.list_items(user_id)
                if not item_rows:
                    raise AppError(ErrorCode.E_CHECKOUT_SESSION_MISSING, "结算会话已失效", 409)

                product_ids = [str(i.product_id) for i in item_rows]
                products = product_repo.list_by_ids(product_ids)
                product_map = {str(p.id): p for p in products}
                if len(product_map) != len(set(product_ids)):
                    raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "部分商品不存在", 404)

                openid_row = wechat_repo.get_identity_by_user_id(user_id)
                if not openid_row:
                    raise AppError(ErrorCode.E_SESSION_UNAVAILABLE, "登录状态已失效", 401)
                openid = openid_row.openid

            total_fee = PaymentService._calc_total_fee(item_rows, product_map)
            out_trade_no = PaymentService._build_out_trade_no(user_id, checkout_created_at)
            nonce_str = secrets.token_hex(16)
            params = {
                "appid": settings.wechat_app_id,
                "mch_id": settings.wechat_mch_id,
                "nonce_str": nonce_str,
                "body": settings.wechat_pay_body,
                "out_trade_no": out_trade_no,
                "total_fee": str(total_fee),
                "spbill_create_ip": client_ip or "127.0.0.1",
                "notify_url": settings.wechat_pay_notify_url,
                "trade_type": "JSAPI",
                "openid": openid,
            }
            params["sign"] = PaymentService._sign_wechat(params, settings.wechat_mch_key)

            unified_order_xml = PaymentService._dict_to_xml(params)
            req = Request(
                "https://api.mch.weixin.qq.com/pay/unifiedorder",
                data=unified_order_xml.encode("utf-8"),
                headers={"Content-Type": "text/xml"},
                method="POST",
            )
            with urlopen(req, timeout=8) as response:
                body = response.read().decode("utf-8")
            response_data = PaymentService._xml_to_dict(body)

            if response_data.get("return_code") != "SUCCESS":
                raise AppError(
                    ErrorCode.E_SERVICE_UNAVAILABLE,
                    response_data.get("return_msg", "微信支付下单失败"),
                    503,
                )
            if response_data.get("result_code") != "SUCCESS":
                raise AppError(
                    ErrorCode.E_SERVICE_UNAVAILABLE,
                    response_data.get("err_code_des", "微信支付下单失败"),
                    503,
                )

            prepay_id = response_data.get("prepay_id", "")
            if not prepay_id:
                raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "微信支付下单失败", 503)

            with SessionLocal() as db:
                WechatRepository(db).upsert_payment_prepare(
                    out_trade_no=out_trade_no,
                    user_id=user_id,
                    checkout_created_at=checkout_created_at,
                    created_at=now_ms(),
                )
                db.commit()

            client_nonce = secrets.token_hex(16)
            time_stamp = str(int(now_ms() / 1000))
            pay_package = f"prepay_id={prepay_id}"
            client_params = {
                "appId": settings.wechat_app_id,
                "timeStamp": time_stamp,
                "nonceStr": client_nonce,
                "package": pay_package,
                "signType": "MD5",
            }
            pay_sign = PaymentService._sign_wechat(client_params, settings.wechat_mch_key)

            return {
                "timeStamp": time_stamp,
                "nonceStr": client_nonce,
                "package": pay_package,
                "signType": "MD5",
                "paySign": pay_sign,
            }
        except AppError:
            raise
        except SQLAlchemyError:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "微信支付服务暂不可用", 503)
        except Exception:
            raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "微信支付服务暂不可用", 503)

    @staticmethod
    def handle_wechat_notify(xml_text: str) -> str:
        try:
            payload = PaymentService._xml_to_dict(xml_text)
        except Exception:
            return PaymentService._notify_xml("FAIL", "XML_PARSE_ERROR")

        if payload.get("return_code") != "SUCCESS" or payload.get("result_code") != "SUCCESS":
            return PaymentService._notify_xml("FAIL", "PAYMENT_NOT_SUCCESS")

        if not settings.wechat_mch_key:
            return PaymentService._notify_xml("FAIL", "MCH_KEY_MISSING")

        sign = payload.get("sign", "")
        if not sign:
            return PaymentService._notify_xml("FAIL", "SIGN_MISSING")

        verify_payload = dict(payload)
        verify_payload.pop("sign", None)
        expected = PaymentService._sign_wechat(verify_payload, settings.wechat_mch_key)
        if expected != sign:
            return PaymentService._notify_xml("FAIL", "SIGN_INVALID")

        out_trade_no = str(payload.get("out_trade_no", "")).strip()
        if not out_trade_no:
            return PaymentService._notify_xml("FAIL", "OUT_TRADE_NO_MISSING")

        try:
            with SessionLocal() as db:
                mapping = WechatRepository(db).get_payment_prepare(out_trade_no)
            if not mapping:
                return PaymentService._notify_xml("FAIL", "TRADE_NOT_FOUND")

            user_id = str(mapping.user_id)
            checkout_created_at = int(mapping.checkout_created_at)
            PaymentService.submit_payment(user_id, "wechat", checkout_created_at)
            return PaymentService._notify_xml("SUCCESS", "OK")
        except Exception:
            return PaymentService._notify_xml("FAIL", "PROCESS_FAILED")

    @staticmethod
    def submit_payment(user_id: str, pay_method: str, checkout_created_at: int) -> dict:
        try:
            with SessionLocal() as db:
                payment_repo = PaymentRepository(db)
                checkout_repo = CheckoutRepository(db)
                favorite_repo = FavoriteRepository(db)

                existing = payment_repo.get_by_user_and_checkout(user_id, checkout_created_at)
                if existing:
                    return {
                        "paid": bool(existing.paid),
                        "source": existing.source,
                        "paidProductIds": [str(pid) for pid in existing.paid_product_ids],
                    }

                session = PaymentService._get_checkout_session(checkout_repo, user_id, checkout_created_at)
                item_rows = checkout_repo.list_items(user_id)
                if not item_rows:
                    raise AppError(ErrorCode.E_CHECKOUT_SESSION_MISSING, "结算会话已失效", 409)

                paid_product_ids = [str(i.product_id) for i in item_rows]
                payment_repo.create(
                    user_id=user_id,
                    checkout_created_at=checkout_created_at,
                    pay_method=pay_method,
                    source=session.source,
                    paid=True,
                    paid_product_ids=paid_product_ids,
                    created_at=now_ms(),
                )

                if session.source == "favorites":
                    favorite_repo.batch_delete_by_product_ids(user_id, paid_product_ids)

                checkout_repo.delete_session(user_id)
                db.commit()

                return {
                    "paid": True,
                    "source": session.source,
                    "paidProductIds": paid_product_ids,
                }
        except AppError:
            raise
        except (IntegrityError, SQLAlchemyError):
            try:
                with SessionLocal() as db:
                    existing = PaymentRepository(db).get_by_user_and_checkout(user_id, checkout_created_at)
                if existing:
                    return {
                        "paid": bool(existing.paid),
                        "source": existing.source,
                        "paidProductIds": [str(pid) for pid in existing.paid_product_ids],
                    }
            except SQLAlchemyError:
                pass
            raise AppError(ErrorCode.E_WRITE_FAILED, "支付确认失败", 500)

    @staticmethod
    def _get_checkout_session(checkout_repo: CheckoutRepository, user_id: str, checkout_created_at: int):
        session = checkout_repo.get_session(user_id)
        if not session:
            raise AppError(ErrorCode.E_CHECKOUT_SESSION_MISSING, "结算会话不存在", 409)

        if int(session.created_at) != int(checkout_created_at):
            raise AppError(ErrorCode.E_CHECKOUT_SESSION_MISSING, "结算会话已失效", 409)
        return session

    @staticmethod
    def _calc_total_fee(item_rows: list, product_map: dict[str, object]) -> int:
        total = Decimal("0")
        for row in item_rows:
            count = int(row.count)
            product = product_map.get(str(row.product_id))
            if not product:
                raise AppError(ErrorCode.E_RESOURCE_NOT_FOUND, "部分商品不存在", 404)
            price_value = str(product.price)
            try:
                unit_price = Decimal(price_value)
            except InvalidOperation:
                raise AppError(ErrorCode.E_SERVICE_UNAVAILABLE, "商品价格数据异常", 503)
            total += unit_price * count

        if total <= 0:
            raise AppError(ErrorCode.E_STATE_CONFLICT, "支付金额无效", 409)
        return int(total * 100)

    @staticmethod
    def _build_out_trade_no(user_id: str, checkout_created_at: int) -> str:
        return f"{checkout_created_at}{user_id.replace('-', '')[:12]}"[:32]

    @staticmethod
    def _sign_wechat(params: dict, mch_key: str) -> str:
        pairs = []
        for key in sorted(params.keys()):
            value = params.get(key)
            if value is None or value == "":
                continue
            pairs.append(f"{key}={value}")
        sign_str = "&".join(pairs) + f"&key={mch_key}"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    @staticmethod
    def _dict_to_xml(payload: dict) -> str:
        pieces = ["<xml>"]
        for key, value in payload.items():
            pieces.append(f"<{key}><![CDATA[{value}]]></{key}>")
        pieces.append("</xml>")
        return "".join(pieces)

    @staticmethod
    def _notify_xml(return_code: str, return_msg: str) -> str:
        return (
            "<xml>"
            f"<return_code><![CDATA[{return_code}]]></return_code>"
            f"<return_msg><![CDATA[{return_msg}]]></return_msg>"
            "</xml>"
        )

    @staticmethod
    def _xml_to_dict(xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        result = {}
        for child in root:
            result[child.tag] = child.text or ""
        return result
