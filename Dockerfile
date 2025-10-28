FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install all required system dependencies in one shot
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        poppler-utils \
        tesseract-ocr \
        libmagic1 \
        curl \
        apt-transport-https \
        lsb-release \
        gnupg && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY app ./app
COPY data_ingestion ./data_ingestion

# Install Azure CLI (for runtime access if required)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Expose app port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
