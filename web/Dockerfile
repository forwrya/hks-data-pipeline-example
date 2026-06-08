FROM node:latest AS angular-build

COPY ./anomaly-detection-frontend/angular.json /app/
COPY ./anomaly-detection-frontend/package.json /app/
COPY ./anomaly-detection-frontend/package-lock.json /app/
COPY ./anomaly-detection-frontend/tsconfig*.json /app/

WORKDIR /app

RUN npm install

COPY ./anomaly-detection-frontend/public/ /app/public/
COPY ./anomaly-detection-frontend/src/ /app/src/

RUN npm run build

FROM nginx:latest

COPY --from=angular-build /app/dist/anomaly-detection-frontend/browser/ /usr/share/nginx/html/
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80