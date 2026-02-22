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
