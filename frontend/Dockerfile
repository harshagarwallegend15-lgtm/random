# Build a static React SPA, then serve it via nginx with a /api/ reverse proxy
# to the FastAPI backend (Docker service name `backend`).

FROM node:20-alpine AS builder

WORKDIR /build

# Install deps first for better layer caching
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Build
COPY . .
RUN npm run build


FROM nginx:1.27-alpine AS runtime

# Drop the default nginx config; use our SPA-friendly one with /api/ proxy
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets
COPY --from=builder /build/dist /usr/share/nginx/html

# nginx-alpine ships as root by default; we don't override USER here because
# nginx master needs root to bind :80. The worker processes run as `nginx`.

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O- http://localhost/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
