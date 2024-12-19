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

# Install system dependencies and Poetry in one line with logging
RUN apt-get update && apt-get install -y curl build-essential wget unzip chromium chromium-driver && curl -sSL https://install.python-poetry.org | python3 && echo "System dependencies and Poetry installed successfully."

# Ensure Poetry installs dependencies globally
RUN poetry config virtualenvs.create false && echo "Poetry configuration set successfully."

# Copy and install dependencies
COPY pyproject.toml ./
RUN poetry install --no-dev --no-interaction && echo "Python dependencies installed successfully."

# Expose the port
EXPOSE 80

# Run the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]
