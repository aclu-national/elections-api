# elections-api

US elections data API.

## Summary

An API for retrieving locally-relevant structured data about US elections.

```
$ curl -s https://elections.api.aclu.org/v1/pip?lat=40.7023699&lng=-74.012632
```

Output: [example-output.json](example-output.json)

## Endpoints

All endpoints expect an HTTP GET request and respond in JSON format. The base URL for API requests is `https://elections.api.aclu.org`.

### `/v1/apple_wallet`

*Get an Apple Wallet pkpass based on polling place info.*

Arguments:
* `address`: The polling place address
* `hours`: The polling place hours
* `lat`: Latitude
* `lng`: Longitude

### `/v1/calendar`

*Get an election calendar for a given state.*

Arguments:
* `format`: Response format (optional; json or ics).
* `state`: The state to load (e.g., ny).

### `/v1/congress`

*Congress election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v1/congress/district`

*Congressional district lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v1/congress/legislators`

*Index of all congressional legislators.*

Arguments:
* `id`: Numeric part of aclu_id (optional; returns a single match).
* `include`: Fields to include (optional; include=name)
* `url_slug`: State and name URL slug (optional; returns a single match).

### `/v1/congress/scores`

*Index of congressional legislator scores.*

No arguments.

### `/v1/county`

*County election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v1/geoip`

*Get an approximate lat/lng location based on IPv4.*

Arguments:
* `ip`: The IPv4 address to look up (optional; e.g., 38.109.115.130)
* `legislators`: Use the resulting location to do a point-in-polygon congress_legislators lookup. (optional; set to 1 to include)
* `pip`: Use the resulting location to do a point-in-polygon lookup. (optional; set to 1 to include state-level pip results)

### `/v1/google_civic_info`

*Lookup Google Civic Info for an election.*

Arguments:
* `address`: Address search string.
* `ocd_id`: An Open Civic Data ID for the election.

### `/v1/pip`

*Point in polygon election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `id`: Hyphen-separated list of numeric IDs (alternative to lat/lng)
* `lat`: Latitude
* `lng`: Longitude
* `state`: Instead of lat/lng or id, specify a state (e.g., state=ny)

### `/v1/state`

*State election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v1/state_leg`

*State legislature election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

You can also load `/v1` for a structured summary of the endpoints.

## Data and sources

You can browse the included `data` and `sources` folders. Each has a `Makefile` for downloading, processing, and indexing source data.

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

Here are the steps to run the server locally for development purposes. For now you _must_ run everything from the `/usr/local/aclu` directory.

```
$ cd elections-api
$ createdb elections
$ make
$ cd server/
$ pip install -r requirements.txt
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

## Reindexing the data

Whenever updates are made to the data, PostGIS needs to be reindexed. This can take several minutes, so you'll want to be careful to only reindex machines that are out of the load balancer rotation.

```
$ cd /usr/local/aclu/elections-api
$ make
```

You can also reindex selected database tables.

```
$ make elections
```

## Restarting the server

When the API server code changes, the application server needs to be restarted after `git pull`ing the changes. Be sure to create a CloudFront invalidation for the new results to take effect.

```
$ sudo service elections restart
```

## Restarting Ubuntu

When you ssh into the box and get a message like *** System restart required *** just reboot ubuntu

```
$ sudo reboot
```

## Load testing the server

Here's how you can use [`siege`](https://www.joedog.org/siege-home/) to simulate 50 concurrent requests using a list of 1,000 random lat/lng lookups within the U.S.A.

```
$ export SIEGE_SCHEME="http"
$ export SIEGE_HOST="localhost:5000"
$ siege -c 50 -t 15S -f server/test_urls.txt -i
```

## See also

* [voter-apple-wallet](https://github.com/aclu-national/voter-apple-wallet)

## Data sources

* [Census TIGER/Line](https://www.census.gov/geo/maps-data/data/tiger-line.html)
* [The Unified Judicial System of Pennsylvania](http://www.pacourts.us/news-and-statistics/cases-of-public-interest/league-of-women-voters-et-al-v-the-commonwealth-of-pennsylvania-et-al-159-mm-2017)
* [@unitedstates](https://github.com/unitedstates/congress-legislators)
* [Ballotpedia](https://ballotpedia.org/Main_Page) (not available for public release)
