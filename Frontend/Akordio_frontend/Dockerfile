# Build stage - npm and others
FROM node:lts-alpine AS build-stage

# Set working directory
WORKDIR /frontend

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy everything else and build frontend
COPY . .
RUN npm run build

# Production stage - only nginx
FROM nginx:stable-alpine AS production-stage

# Copy only build to nginx publication dir
COPY --from=build-stage /frontend/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose frontend on port 80
EXPOSE 80

# Put nginx in the foreground for docker
CMD ["nginx", "-g", "daemon off;"]