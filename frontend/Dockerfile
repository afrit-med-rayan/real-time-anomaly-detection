# frontend/Dockerfile

# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files (from the frontend directory context)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy all frontend files (from the frontend directory context)
COPY frontend/ ./

# Build the project (Vite builds into /app/dist)
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:alpine

# Copy the build output from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 (will map to 5173 on the host via docker-compose)
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
