FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install -y gcc libmagic1 libmagic-dev \
    && apt-get clean

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

ENV PATH "$PATH:/app/scripts"

RUN useradd -m -d /app -s /bin/bash app \
    && chown -R app:app /app/* && chmod +x /app/scripts/*

USER app

CMD ["./scripts/run.sh"]