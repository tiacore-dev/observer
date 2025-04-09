# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    ca-certificates \
    ffmpeg \
    libavcodec-extra \
    && update-ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== TESTING =====
FROM base AS test
RUN pip install --no-cache-dir pytest
COPY . .

# ===== FINAL =====
FROM base AS prod
COPY . .

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
