FROM python:alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    mariadb-client \
    libffi-dev \
    build-base \
    pkgconfig \
    bash

WORKDIR /app

COPY . .
RUN if [ -f ./exported_data.json ]; then cp ./exported_data.json /app/exported_data.json; fi

RUN pip install --upgrade pip
RUN pip install -e .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]