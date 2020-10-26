FROM python:3.8-alpine3.12 AS builder

RUN apk add --no-cache \
    bash=5.0.17-r0 \
    gcc=9.3.0-r2 \
    postgresql-dev=12.4-r0\
    musl-dev=1.1.24-r9 \
    python3-dev=3.8.5-r0

COPY setup.py setup.py

COPY requirements.txt requirements.txt

RUN pip install -e ./



FROM python:3.8-alpine3.12

RUN apk add --no-cache \
    bash=5.0.17-r0 \
    postgresql=12.4-r0 \
    docker=19.03.12-r0

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages

COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV PYTHONPATH=/usr/app

WORKDIR /usr/app
