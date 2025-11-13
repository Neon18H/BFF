FROM python:3.11-slim as base
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.3
WORKDIR /app

RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false

COPY pyproject.toml /app/
RUN poetry install --no-interaction --no-ansi

COPY app /app/app
COPY migrations /app/migrations
COPY tools /app/tools

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

