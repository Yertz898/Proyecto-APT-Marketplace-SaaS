FROM node:24-slim

WORKDIR /app

# package.json primero: instalar dependencias solo cuando cambien.
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
