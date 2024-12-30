# syntax=docker/dockerfile:1

# Build stage
FROM --platform=$BUILDPLATFORM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"
ENV POETRY_VERSION=1.7.0
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    # Create a non-root user
    groupadd -r appuser && \
    useradd -r -g appuser appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

# Copy and install dependencies first (for better caching)
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# Copy the application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Change port to non-privileged
EXPOSE 5001

# Update command to use the new port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001", "--workers", "2", "--timeout-keep-alive", "75"]

# Only keep necessary environment variables
ENV PYTHONUNBUFFERED=1

# Don't put sensitive values here - they'll come from the environment
