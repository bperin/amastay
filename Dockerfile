# Use an ARM-compatible Python image for Apple Silicon or an amd64 image
FROM --platform=linux/arm64 python:3.9-slim

WORKDIR /app

# Copy the application code
COPY . /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Install gunicorn separately
RUN python3 -m pip install --no-cache-dir gunicorn

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=80
ENV CORES=2

# Expose both HTTP and HTTPS ports
EXPOSE 80
EXPOSE 443

# Run the application with gunicorn on both HTTP and HTTPS ports
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "app:app"]
