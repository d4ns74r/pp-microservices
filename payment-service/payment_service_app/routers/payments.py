from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from payment_service_app.db import get_db
from payment_service_app.models import Transaction
from payment_service_app.schemas import PaymentRequest, PaymentResponse
from payment_service_app.kafka_producer import kafka_producer

router = APIRouter(prefix="/payment", tags=["payments"])

@router.post("/deposit", response_model=PaymentResponse)
async def deposit(request: PaymentRequest, db: AsyncSession = Depends(get_db)):
    transaction = Transaction(user_id=request.user_id, type="deposit", amount=request.amount)
    db.add(transaction)
    await db.commit()

    await kafka_producer.send_message(
        topic="payment_notifications",
        message={"event": "deposit", "user_id": request.user_id, "amount": request.amount}
    )
    return {"message": f"Deposited {request.amount:.2f} to user {request.user_id}"}

@router.post("/withdrawal", response_model=PaymentResponse)
async def withdrawal(request: PaymentRequest, db: AsyncSession = Depends(get_db)):
    transaction = Transaction(user_id=request.user_id, type="withdrawal", amount=request.amount)
    db.add(transaction)
    await db.commit()

    await kafka_producer.send_message(
        topic="payment_notifications",
        message={"event": "withdrawal", "user_id": request.user_id, "amount": request.amount}
    )
    return {"message": f"Withdrew {request.amount:.2f} from user {request.user_id}"}
