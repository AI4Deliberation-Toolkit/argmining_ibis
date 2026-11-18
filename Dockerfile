FROM python:3.14
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/

COPY . /home/argmining_ibis
WORKDIR /home/argmining_ibis

ENV UV_NO_DEV=1
RUN uv sync --locked

RUN apt-get update
RUN apt-get install -y valkey-server

RUN chmod +x boot.sh  


ENTRYPOINT ["./boot.sh"]  
