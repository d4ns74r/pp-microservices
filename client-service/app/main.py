from fastapi import FastAPI
from app.routers import clients

app = FastAPI()

# Подключаем роуты
app.include_router(clients.router)


# Эндпоинт для проверки работы сервиса
@app.get("/")
def read_root():
    return {"message": "Client service running"}
