# Use the official Python 3.9 image with arm64 architecture
FROM --platform=linux/arm64 python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt .

# Update pip to the latest version before installing dependencies
RUN python3 -m pip install --upgrade pip

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

COPY .env .env

# Expose port 80 for the application
EXPOSE 80

ENV FLASK_APP app.py

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]
