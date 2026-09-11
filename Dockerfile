FROM node:26-alpine AS frontend

WORKDIR /build/ts
COPY ts/package*.json ./
RUN npm ci
COPY ts/ ./
ENV REACT_APP_DEMO_MODE=true
ENV REACT_APP_FLASK_BASE_URL=
RUN npm run build

FROM python:3.13-slim

WORKDIR /app
ENV DEMO_MODE=true
ENV FLASK_ENV=DEVELOPMENT
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY python/ ./python/
COPY --from=frontend /build/ts/build ./python/src/app/static
COPY docker/aws-demo-entrypoint.sh /usr/local/bin/aws-demo-entrypoint
RUN chmod +x /usr/local/bin/aws-demo-entrypoint

EXPOSE 8080
CMD ["aws-demo-entrypoint"]