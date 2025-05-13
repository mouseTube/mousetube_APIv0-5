FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    mariadb-client \
    libmariadb-dev \
    libffi-dev \
    build-essential \
    pkg-config \
    curl \
    bash \
    dos2unix \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz \
    | tar xz -C /usr/local/bin --strip-components=1 uv-x86_64-unknown-linux-gnu/uv

RUN uv --version

WORKDIR /app

COPY . .

RUN uv pip install -e . --system

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && dos2unix /entrypoint.sh

ENTRYPOINT ["bash", "/entrypoint.sh"]
