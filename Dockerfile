FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIPENV_VENV_IN_PROJECT=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv


COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

COPY . /app/
COPY env /app/env


RUN chmod +x /app/.deploy/bash/entrypoint.sh

EXPOSE 8000

