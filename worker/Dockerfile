# syntax=docker/dockerfile:1
FROM python:3.11-alpine AS builder
WORKDIR /build
RUN apk update && apk upgrade --no-cache
RUN pip install --no-cache-dir "pip==24.3.1" "setuptools==75.8.0" "wheel==0.45.1"
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine AS runtime
WORKDIR /app
RUN apk update && apk upgrade --no-cache && \
    addgroup -S appgroup && adduser -S -G appgroup -H appuser
RUN pip install --no-cache-dir "pip==24.3.1" "setuptools==75.8.0" "wheel==0.45.1"
COPY --from=builder /install /usr/local
COPY worker.py healthcheck.py ./
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD ["python", "healthcheck.py"]
CMD ["python", "worker.py"]
