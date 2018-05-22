#!/bin/bash

# Before running this:
#
# sudo mkdir /usr/local/aclu
# sudo chown ubuntu:ubuntu /usr/local/aclu
# cd /usr/local/aclu
# git clone git@github.com:aclu-national/election-data.git
# cd election-data
# sudo scripts/setup_ubuntu.sh

if [ "$EUID" -ne 0 ]
  then echo "Please run with admin privs: sudo ./setup_ubuntu.sh"
  exit
fi

PROJECT="election-data"
PROJECT_PATH="/usr/local/aclu/$PROJECT"
POSTGRES_VERSION="9.5"
POSTGRES_MAIN="/etc/postgresql/$POSTGRES_VERSION/main"

apt update
apt upgrade -y

apt install -y fail2ban ufw htop emacs24-nox postgresql postgresql-contrib \
               build-essential gdal-bin python python-pip python-gevent nginx

ufw allow 5000
ufw allow 80
ufw allow 22
yes | ufw enable

add-apt-repository -y ppa:ubuntugis/ubuntugis-unstabled

apt update
apt install -y postgis

pip install --upgrade pip
pip install flask flask_cors psycopg2-binary gunicorn bs4 urllib3 certifi arrow

if [ -f "$POSTGRES_MAIN/postgresql.conf" ] ; then
	mv "$POSTGRES_MAIN/postgresql.conf" "$POSTGRES_MAIN/postgresql.conf.bak"
fi

cp "$PROJECT_PATH/server/postgresql.conf" "$POSTGRES_MAIN/postgresql.conf"
sed -i -e 's/\(local\s*all\s*postgres\s*\)peer/\1trust/' "$POSTGRES_MAIN/pg_hba.conf"

service postgresql restart

sudo -u postgres createuser --superuser ubuntu
sudo -u postgres createdb elections
sudo -u postgres psql -d elections -c "CREATE EXTENSION postgis;"

cd "$PROJECT_PATH"
make

cp "$PROJECT_PATH/server/elections.service" /etc/systemd/system/
cp "$PROJECT_PATH/server/elections.socket" /etc/systemd/system/
systemctl enable elections.service
service elections start

rm /etc/nginx/sites-enabled/default
ln -s "$PROJECT_PATH/server/nginx.conf" /etc/nginx/sites-enabled/elections.api.aclu.org
sudo service nginx restart

echo "done"
