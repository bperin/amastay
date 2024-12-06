# Use multi-stage build
FROM --platform=linux/arm64 python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies and Poetry in one layer
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && curl -sSL https://install.python-poetry.org | python3 - && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-root

# Final stage
FROM --platform=linux/arm64 python:3.11-slim

# Copy environment and Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /opt/poetry /opt/poetry

# Set environment variables
ENV PYTHONPATH="/app" \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PATH="/opt/poetry/bin:$PATH"

# Copy application code
WORKDIR /app
COPY . .

# Copy and load env vars
COPY .env .env
ENV $(cat .env | xargs)

EXPOSE 80
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
