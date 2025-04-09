# ===== BASE =====
FROM python:3.12-slim AS base
WORKDIR /app

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
