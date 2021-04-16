# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.9
MAINTAINER Denis Spirit <spirits25@mail.ru>

ENV PORT=8000
ENV HOST=0.0.0.0
ENV MAX_REQUESTS=10
ENV WORKERS=1
WORKDIR /opt/project

ADD requirements.txt /opt/project/

RUN pip install -r requirements.txt

ADD billing /opt/project

CMD exec gunicorn --pythonpath /opt/project/ --bind $HOST:$PORT --max-requests $MAX_REQUESTS --workers=$WORKERS --reload billing.wsgi
