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

# Create entrypoint script
RUN echo '#!/bin/bash\n\
STREAMLIT_PORT="${PORT:-8501}"\n\
streamlit run --server.port $STREAMLIT_PORT --server.address 0.0.0.0 app.py' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
