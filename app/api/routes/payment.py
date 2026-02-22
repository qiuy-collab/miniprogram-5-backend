from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.auth.deps import get_current_user_id
from app.schemas.payment import (
    PrepareWechatPaymentRequest,
    PrepareWechatPaymentResponse,
    SubmitPaymentRequest,
    SubmitPaymentResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/payments/submit", response_model=SubmitPaymentResponse)
def submit_payment(payload: SubmitPaymentRequest, user_id: str = Depends(get_current_user_id)):
    return PaymentService.submit_payment(user_id, payload.payMethod, payload.checkoutCreatedAt)


@router.post("/payments/wechat/prepare", response_model=PrepareWechatPaymentResponse)
def prepare_wechat_payment(
    payload: PrepareWechatPaymentRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    return PaymentService.prepare_wechat_payment(user_id, payload.checkoutCreatedAt, client_ip)


@router.post("/payments/wechat/notify")
async def wechat_notify(request: Request):
    xml_text = (await request.body()).decode("utf-8", errors="ignore")
    response_xml = PaymentService.handle_wechat_notify(xml_text)
    return Response(content=response_xml, media_type="application/xml")
