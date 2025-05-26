# ---------- Stage 1: Build ----------
    FROM python:3.11-slim AS builder

    # Set working directory
    WORKDIR /app
    
    # Install build dependencies
    RUN apt-get update && apt-get install -y \
        build-essential \
        gcc \
        curl \
        libffi-dev \
        libssl-dev \
        git \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install them in a virtual environment
    COPY requirements.txt .
    RUN python -m venv /venv && \
        /venv/bin/pip install --upgrade pip && \
        /venv/bin/pip install --no-cache-dir -r requirements.txt
    
    # ---------- Stage 2: Final ----------
    FROM python:3.11-slim
    
    # Set working directory
    WORKDIR /app
    
    # Install runtime dependencies (lightweight)
    RUN apt-get update && apt-get install -y \
        libffi8 \
        libssl3 \
        libstdc++6 \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy virtual environment and app
    COPY --from=builder /venv /venv
    COPY . /app
    
    # Set environment
    ENV PATH="/venv/bin:$PATH"
    ENV PYTHONUNBUFFERED=1
    
    # Expose port
    EXPOSE 8000
    
    # Run FastAPI with uvicorn
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    