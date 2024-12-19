# Use x86_64 architecture with Python 3.11 slim image
FROM --platform=linux/x86_64 python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"
ENV POETRY_VERSION=1.7.0
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV CHROME_DRIVER="/usr/local/bin/chromedriver"

# Set the working directory
WORKDIR /app

# Install system dependencies including Chromium and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    wget \
    unzip \
    gnupg \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    lsb-release \
    xdg-utils \
    chromium && rm -rf /var/lib/apt/lists/*

# Create a symbolic link for Google Chrome
RUN ln -s /usr/bin/chromium /usr/bin/google-chrome

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \ 
wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \ 
unzip chromedriver_linux64.zip -d /usr/local/bin/ && \ 
chmod +x /usr/local/bin/chromedriver && \ 
rm chromedriver_linux64.zip

# Run commands to find and print the paths to the Chrome and ChromeDriver binaries
RUN which google-chrome && echo "Chrome path printed successfully." && which chromedriver && echo "ChromeDriver path printed successfully."

# Verify Chromium installation
RUN chromium --version

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 && echo "System dependencies and Poetry installed successfully."

# Ensure Poetry installs dependencies globally
RUN poetry config virtualenvs.create false && echo "Poetry configuration set successfully."

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
