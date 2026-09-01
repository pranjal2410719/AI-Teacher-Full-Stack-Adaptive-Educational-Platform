FROM node:18-alpine

WORKDIR /app

# Copy package configuration
COPY package*.json ./

# Install dependencies
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy frontend source code
COPY . .

# Build production assets
RUN npm run build

# Expose Vite preview port
EXPOSE 3000

# Start Vite preview server for production hosting
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
