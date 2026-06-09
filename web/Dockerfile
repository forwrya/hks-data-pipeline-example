FROM node:latest AS angular-build

COPY ./anomaly-detection-frontend/angular.json /app/
COPY ./anomaly-detection-frontend/package.json /app/
COPY ./anomaly-detection-frontend/package-lock.json /app/
COPY ./anomaly-detection-frontend/tsconfig*.json /app/

WORKDIR /app

RUN npm install

COPY ./anomaly-detection-frontend/public/ /app/public/
COPY ./anomaly-detection-frontend/src/ /app/src/

# Substitute placeholders in production environments file
ARG FRONTEND_API_URL
RUN ls
RUN ls
RUN npm install -g envsub
RUN envsub --env FRONTEND_API_URL=${FRONTEND_API_URL} ./src/environments/environment.production.ts ./src/environments/environment.production.ts 

RUN npm run build

FROM nginx:latest

COPY --from=angular-build /app/dist/anomaly-detection-frontend/browser/ /usr/share/nginx/html/
COPY ./default.conf.template /etc/nginx/templates/

EXPOSE 80