FROM python:3.11-alpine3.18

WORKDIR /app
COPY . .

RUN apk add build-base libffi-dev
RUN pip3 install -r requirements.txt
ENV DJANGO_SETTINGS_MODULE config.settings

CMD ["/bin/sh", "docker-entrypoint.sh"]