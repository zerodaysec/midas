FROM ubuntu:24.04

MAINTAINER "jon@zer0day.net"

RUN apt-get update -y && \
    apt-get install -y python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

COPY ./app/* /app

WORKDIR /app

RUN pip install -r /app/requirements.txt
