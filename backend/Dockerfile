# backend/Dockerfile
FROM python:3.10-slim-bullseye

WORKDIR /app

# Install dependencies required by confluent-kafka and some standard C libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    python3-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Optimize layer caching by copying requirements first
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend directory
COPY backend/ /app/backend/

# Set PYTHONPATH so absolute imports like 'backend.api...' work
ENV PYTHONPATH=/app

EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
