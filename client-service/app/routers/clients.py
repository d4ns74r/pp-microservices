from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import List
import uuid

router = APIRouter(prefix="/client", tags=["clients"])

# Временная база данных
clients_db = []


class Client(BaseModel):
    id: str
    name: str
    email: EmailStr


class ClientCreate(BaseModel):
    name: str
    email: EmailStr


@router.post("/", response_model=Client)
def create_client(client: ClientCreate):
    new_client = Client(
        id=str(uuid.uuid4()),
        name=client.name,
        email=client.email
    )
    clients_db.append(new_client)
    return new_client


@router.get("/", response_model=List[Client])
def get_clients():
    return clients_db
