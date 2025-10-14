# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production=false
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine AS production
# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html
# Copy a custom nginx.conf if needed (optional; see below for example)
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]