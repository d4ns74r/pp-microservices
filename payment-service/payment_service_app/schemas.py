from pydantic import BaseModel, PositiveFloat


class PaymentRequest(BaseModel):
    user_id: int
    amount: PositiveFloat


class PaymentResponse(BaseModel):
    message: str
