# Stage 1: Build Angular app
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline
COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine AS runner
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 443
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q --no-check-certificate -O- https://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
