# Change to ARM64 architecture
FROM --platform=linux/arm64 python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"
ENV POETRY_VERSION=1.7.0
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the application
COPY . .

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y curl build-essential && curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry installs dependencies globally
RUN poetry config virtualenvs.create false

# Generate requirements.txt from poetry and install
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install poetry && poetry config repositories.pypi https://pypi.tuna.tsinghua.edu.cn/simple && poetry install --no-dev --no-interaction

# Expose the port
EXPOSE 80

# Run the application with Uvicorn with proper settings
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2", "--timeout-keep-alive", "75"]

# Only keep necessary environment variables
ENV PYTHONUNBUFFERED=1

# Don't put sensitive values here - they'll come from the environment
