# syntax=docker/dockerfile:1
FROM python:3.11-alpine AS builder
WORKDIR /build
RUN apk update && apk upgrade --no-cache
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine AS runtime
WORKDIR /app
RUN apk update && apk upgrade --no-cache && \
    addgroup -S appgroup && adduser -S -G appgroup -H appuser
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY --from=builder /install /usr/local
COPY worker.py healthcheck.py ./
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD ["python", "healthcheck.py"]
CMD ["python", "worker.py"]
