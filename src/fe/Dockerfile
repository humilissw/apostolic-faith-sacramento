# ---- Build stage ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json bun.lock ./
RUN npm install -g bun 2>/dev/null || true
RUN corepack enable && bun install --frozen-lockfile 2>/dev/null || npm ci
RUN rm -rf node_modules/.cache

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npx next build

# ---- Production stage ----
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/out /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
