#!/bin/bash

# Ожидаем 20 секунд перед запуском приложения
echo "Waiting for Kafka to be ready..."
sleep 20

# Запускаем приложение
echo "Starting application..."
uvicorn payment_service_app.main:app --host 0.0.0.0 --port 8000 --reload
