# ---- Compilación ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Vite lee las variables VITE_* del entorno al compilar
ARG VITE_AUTH_API_URL
ARG VITE_SOLICITUDES_API_URL
ARG VITE_PAGE_SIZE
ENV VITE_AUTH_API_URL=$VITE_AUTH_API_URL \
    VITE_SOLICITUDES_API_URL=$VITE_SOLICITUDES_API_URL \
    VITE_PAGE_SIZE=$VITE_PAGE_SIZE
RUN npm run build

# ---- Servidor estático ----
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
