# syntax=docker/dockerfile:1
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-slim
WORKDIR /app
RUN groupadd --system appgroup && useradd --system --gid appgroup appuser
COPY --from=builder /app/node_modules ./node_modules
COPY app.js healthcheck.js package.json ./
COPY views ./views
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD ["node", "healthcheck.js"]
CMD ["node", "app.js"]
