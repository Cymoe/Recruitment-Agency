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

# Set environment variables
ENV PORT=8501
ENV FASTAPI_PORT=8000

# Expose ports
EXPOSE 8501
EXPOSE 8000

# Create start script with proper port handling
RUN echo '#!/bin/bash\n\
PORT="${PORT:-8501}"\n\
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0' > start.sh && \
    chmod +x start.sh

# Command to run the application
CMD ["./start.sh"]
