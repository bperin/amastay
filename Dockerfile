# Use the official Selenium Standalone Chrome image
FROM selenium/standalone-chrome:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"
ENV POETRY_VERSION=1.7.0
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV ENV=production

# Set the working directory
WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 && echo "Poetry installed successfully."

# Ensure Poetry installs dependencies globally
RUN poetry config virtualenvs.create false && echo "Poetry configured to install dependencies globally."

# Copy only the dependency specification to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry install --no-dev --no-interaction && echo "Python dependencies installed successfully."

# Copy the rest of the application
COPY . .

# (Optional) Create a non-root user for better security
RUN useradd -m scraper
USER scraper

# Expose the port
EXPOSE 80

# Run the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]
