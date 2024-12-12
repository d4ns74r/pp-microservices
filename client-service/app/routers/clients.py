from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Client as DBClient
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
    # Создаем объект модели
    db_client = DBClient(name=client.name, email=client.email)

    # Добавляем и сохраняем в базе данных
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)

    return db_client


@router.get("/", response_model=List[ClientResponse])
async def get_clients(db: AsyncSession = Depends(get_db)):
    # Выполняем запрос к базе данных
    result = await db.execute(select(DBClient))
    clients = result.scalars().all()
    return clients
