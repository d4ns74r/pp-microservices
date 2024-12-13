FROM python:3.10-slim

WORKDIR /payment_service_app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "payment_service_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



