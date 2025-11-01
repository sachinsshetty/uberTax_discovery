# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Declare build arg and set as env for Vite to access
ARG VITE_DWANI_API_BASE_URL
ENV VITE_DWANI_API_BASE_URL=$VITE_DWANI_API_BASE_URL

COPY package*.json ./
RUN npm ci 
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