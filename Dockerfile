# Change to ARM64 architecture
FROM --platform=linux/arm64 python:3.11-slim

# Set environment variables for Python and Poetry
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"
ENV POETRY_VERSION=1.7.0
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set the working directory
WORKDIR /app

# Copy .env file first
COPY .env .env

# Copy the rest of the application
COPY . .

# Load env vars from .env
ENV $(cat .env | xargs)

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y curl build-essential && curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry installs dependencies globally
RUN poetry config virtualenvs.create false

# Copy the pyproject.toml file
COPY pyproject.toml ./

# Install dependencies using Poetry
RUN poetry install --no-dev --no-interaction

# Expose the port the app runs on
EXPOSE 80

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
