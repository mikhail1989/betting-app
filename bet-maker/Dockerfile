FROM python:3.10.0-alpine

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN pip install -r app/requirements.txt
