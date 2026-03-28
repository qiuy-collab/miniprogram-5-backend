from typing import Literal

from pydantic import BaseModel


PayMethod = Literal["wechat", "alipay"]


class SubmitPaymentRequest(BaseModel):
    payMethod: PayMethod
    checkoutCreatedAt: int


class SubmitPaymentResponse(BaseModel):
    paid: bool
    source: Literal["favorites", "product"]
    paidProductIds: list[str]


class PrepareWechatPaymentRequest(BaseModel):
    checkoutCreatedAt: int


class PrepareWechatPaymentResponse(BaseModel):
    timeStamp: str
    nonceStr: str
    package: str
    signType: Literal["MD5"]
    paySign: str


class AdminPaymentItem(BaseModel):
    id: str
    user_id: str
    checkout_created_at: int
    pay_method: PayMethod
    source: Literal["favorites", "product"]
    paid: bool
    paid_product_ids: list[str]
    created_at: int


class AdminListPaymentsResponse(BaseModel):
    records: list[AdminPaymentItem]


class AdminGetPaymentDetailResponse(BaseModel):
    record: AdminPaymentItem
