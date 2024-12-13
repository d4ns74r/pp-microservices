from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Client as DBClient
from app.logger import logger
from app.kafka_producer import producer  # Импорт Kafka продюсера
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreate(BaseModel):
    name: str
    email: EmailStr


class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


@router.post("/", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating client with name: {client.name} and email: {client.email}")
    try:
        db_client = DBClient(name=client.name, email=client.email)
        db.add(db_client)
        await db.commit()
        await db.refresh(db_client)
        logger.info(f"Client created successfully: {db_client.id}")

        # Отправка события в Kafka
        try:
            await producer.send(
                topic="client-events",
                message={
                    "event": "client_created",
                    "data": {"id": db_client.id, "name": db_client.name, "email": db_client.email}
                }
            )
            logger.info(f"Kafka message sent for client ID {db_client.id}")
        except Exception as kafka_error:
            logger.error(f"Failed to send Kafka message: {str(kafka_error)}")

        return db_client
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=List[ClientResponse])
async def get_clients(db: AsyncSession = Depends(get_db)):
    logger.info("Fetching all clients")
    try:
        result = await db.execute(select(DBClient))
        clients = result.scalars().all()
        logger.info(f"Retrieved {len(clients)} clients")
        return clients
    except Exception as e:
        logger.error(f"Error fetching clients: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
