FROM python:3.12-slim

LABEL maintainer="kacper"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R django-user:django-user /app

USER django-user
