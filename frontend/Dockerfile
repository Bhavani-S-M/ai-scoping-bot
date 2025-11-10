#frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install && npm install mermaid react-mermaid

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Run in development mode with hot reload
CMD ["npm", "run", "dev"]
