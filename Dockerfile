FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF processing and PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads && chmod 777 uploads

# Set default environment variables
ENV PORT=8501
ENV FASTAPI_PORT=8000

# Expose ports
EXPOSE 8501
EXPOSE 8000

# Command to run the application using Python script
CMD ["python", "start.py"]
