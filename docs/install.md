[*ACLU Elections API*](https://github.com/aclu-national/elections-api)

# How to install

The Elections API is meant to be a public reference for others doing work on US elections.

## Dependencies

* [Python 2.7](https://www.python.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [PostGIS](http://postgis.net/)
* [Flask](http://flask.pocoo.org/)
* [Gunicorn](http://gunicorn.org/)
* [nginx](https://www.nginx.com/)

## Services

The API relies on other upstream services and expects some API keys to be defined as environment variables.

* [Google Civic Info API](https://developers.google.com/civic-information/): `GOOGLE_API_KEY`
* [Mapbox Geocoding API](https://www.mapbox.com/api-documentation/#endpoints): `MAPBOX_API_KEY`
* [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/start): `GOOGLE_API_KEY` (optional; only used for polling places)
* [ipstack](https://ipstack.com/): `IPSTACK_API_KEY` (optional; defaults to Maxmind)

## Running the server locally

Here are the steps to run the server locally for development purposes.

For now you _must_ run everything from the `/usr/local/aclu` directory.

```
$ sudo mkdir -p /usr/local/aclu
$ sudo chown $(whoami) /usr/local/aclu
$ cd /usr/local/aclu
$ git clone https://github.com/aclu-national/elections-api.git
```

Next we will install the required Python modules. Note that you may need to go on a side quest here to loosen the appropriate directory file permissions, or use `sudo` to install the packages.

```
$ cd elections-api
$ pip install -r server/requirements.txt
```

The folder structure of the API code includes `sources` and `data` subdirectories. The `sources` data generally feeds into `data`, creating more stable records with ACLU-assigned stable IDs. Some data sources need to be downloaded before we can index the database. The Congressional sessions data (mostly for start/end dates) is one that we'll need to download first.

```
$ cd sources/
$ make congress_sessions
```

Now we can setup the PostgreSQL database.

```
$ createdb elections
$ psql elections -c "CREATE EXTENSION postgis";
$ cd ../
$ make
```

The indexing will take a while to run.

Finally, we can start up the server.

```
$ cd server/
$ export GOOGLE_API_KEY="..."
$ export MAPBOX_API_KEY="..."
$ python server.py
```

## Ubuntu server setup

The API server is designed to run on Ubuntu 16.04.

```
$ sudo mkdir -p /usr/local/aclu
$ sudo chown $USER:$USER /usr/local/aclu
$ cd /usr/local/aclu
```
If you work at the ACLU and have access to the private repo included as a submodule in the project, run:
```
$ git clone --recurse-submodules git@github.com:aclu-national/elections-api.git
```
Otherwise
```
$ git clone https://github.com/aclu-national/elections-api.git
```

```
$ cd elections-api
$ sudo ./scripts/setup_ubuntu.sh
```

The config file `server/gunicorn.py` has environment variables and feature flags that you will need to edit.
