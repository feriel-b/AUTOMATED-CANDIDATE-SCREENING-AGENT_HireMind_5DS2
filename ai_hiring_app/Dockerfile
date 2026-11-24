# 1. Use an official Python runtime as a parent image
# Using 'slim' is a good practice for smaller image sizes
FROM python:3.10-slim

# 2. Install system dependencies required for audio processing and ML libraries
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy the dependency file and install dependencies first
# This is a key optimization. Docker caches layers. As long as requirements.txt
# doesn't change, Docker won't re-run this slow step.
COPY requirements.txt .

# Upgrade pip first and configure retries and timeouts for large packages
RUN pip install --upgrade pip && \
    pip config set global.timeout 1000 && \
    pip config set global.retries 5

# Install PyTorch CPU wheels from the official PyTorch index (faster/more reliable)
# See: https://pytorch.org/get-started/locally/
RUN pip install --no-cache-dir --default-timeout=1000 \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.1.2+cpu torchaudio==2.1.2+cpu

# Install remaining dependencies without touching already-installed torch packages
RUN PIP_NO_CACHE_DIR=1 pip install --default-timeout=1000 \
    --upgrade-strategy only-if-needed -r requirements.txt

# 5. (Optional) spaCy model download skipped at build time to avoid network/DNS failures
# You can download at runtime if needed: `python -m spacy download en_core_web_sm`

# 6. Copy the rest of your application code into the container
COPY ./app /app

# 7. Expose the port the app runs on
EXPOSE 8000

# 8. Define the command to run your app when the container starts
# We use 0.0.0.0 to make the server accessible from outside the container
# Note: --reload is disabled in Docker to avoid infinite reload loops with bind mounts on Windows/Mac
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]