# pull official base image
FROM python:2.7

# set work directory
WORKDIR /usr/local/aclu/elections-api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt update \
    # psycopg2 dependencies
    && apt -y install libghc-hdbc-postgresql-dev gcc python2-dev musl-dev make curl postgis \
      fail2ban ufw htop emacs24-nox \
      build-essential gdal-bin unzip nodejs npm \
      # data/make dependencies
      jq \
      # smartcrop dependencies
      libopencv-dev

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/local/aclu/elections-api/requirements.txt
COPY ./dev-requirements.txt /usr/local/aclu/elections-api/dev-requirements.txt
RUN pip install -r requirements.txt -r dev-requirements.txt

# install node dependencies
RUN npm install -g mapshaper opencv --unsafe-perm=true smartcrop-cli --unsafe-perm=true