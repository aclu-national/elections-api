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
RUN apt update && apt -y install jq

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/local/aclu/elections-api/requirements.txt
RUN pip install -r requirements.txt

# smartcrop + dependencies
RUN apt update && apt -y install libopencv-dev
RUN pip install git+https://chromium.googlesource.com/external/gyp
RUN npm install -g opencv --unsafe-perm=true
RUN npm install -g smartcrop-cli --unsafe-perm=true

# install non-server python dependencies
RUN pip install area==1.1.1
RUN pip install unicodecsv==0.14.1
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-geojson.git
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-utils.git
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes.git
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-meta.git
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-uri.git
RUN pip install git+https://github.com/whosonfirst/py-mapzen-whosonfirst-sources.git
RUN pip install shapely==1.7.0
RUN pip install geojson==2.5.0
RUN pip install atomicwrites==1.3.0