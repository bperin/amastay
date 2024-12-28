FROM --platform=linux/arm64 python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/app" POETRY_VERSION=1.7.0 POETRY_HOME="/opt/poetry" PATH="$POETRY_HOME/bin:$PATH"

ARG CACHEBUST=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y curl build-essential --no-cache && curl -sSL https://install.python-poetry.org | python3 -

RUN poetry config virtualenvs.create false && poetry config cache-dir /dev/null

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry && poetry install --no-dev --no-interaction --no-cache

COPY . .

RUN echo "Build timestamp: $(date)" >build_timestamp

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2", "--timeout-keep-alive", "75"]
