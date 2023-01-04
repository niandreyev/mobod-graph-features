FROM python:3.7.16-slim

WORKDIR /app
COPY main.py requirements.txt /app/
RUN pip install -r /app/requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./graphfs /app/graphfs