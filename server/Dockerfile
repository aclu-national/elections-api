# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/local/aclu/elections-api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev make curl

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/local/aclu/elections-api/requirements.txt
RUN pip install -r requirements.txt