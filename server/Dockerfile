# pull official base image
FROM python:2.7

# set work directory
WORKDIR /usr/local/aclu/elections-api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt update \
    && apt -y install libghc-hdbc-postgresql-dev gcc python2-dev musl-dev make curl postgis \
      fail2ban ufw htop emacs24-nox \
      build-essential gdal-bin unzip nodejs npm

# install data/make dependencies
RUN npm install -g mapshaper

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/local/aclu/elections-api/requirements.txt
RUN pip install -r requirements.txt