# FILE: Dockerfile
# --- THIS IS THE FINAL, SIMPLEST VERSION ---

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (ffmpeg is for other features, good to keep)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements and install the simple, stable dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- ALL BROKEN NLP COMMANDS ARE GONE ---

# Copy your application code
COPY ./app .

# Expose port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]