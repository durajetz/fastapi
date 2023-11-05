FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN pip install -r /app/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /app/

ENV PATH "$PATH:/app/scripts"

RUN useradd -m -d /app -s /bin/bash app \
    && chown -R app:app /app/* && chmod +x /app/scripts/*

USER app

CMD ["./scripts/run.sh"]