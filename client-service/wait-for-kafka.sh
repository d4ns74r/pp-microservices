#!/bin/bash

# Ожидаем 20 секунд перед запуском приложения
echo "Waiting for Kafka to be ready..."
sleep 30

# Запускаем приложение
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
