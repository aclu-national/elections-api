# elections-api

US elections data API.

## Summary

Structured data about your local elections.

__Point-in-polygon example:__

```
curl https://elections.api.aclu.org/v1/pip?lat=40.7023699&lng=-74.012632 | jq .
```

[example output](example-output.json)

## Endpoints

All requests are HTTP GET and respond in JSON format.

* `/v1/geoip`  
  *Get an approximate lat/lng location based on IPv4.*  
  Arguments:  
    - `pip`: Use the resulting location to do a point-in-polygon lookup. (optional; set to 1 to include state-level pip results)
    - `ip`: The IPv4 address to look up (optional; e.g., 38.109.115.130)
    - `legislators`: Use the resulting location to do a point-in-polygon congress_legislators lookup. (optional; set to 1 to include)
* `/v1/calendar`  
  *Get an election calendar for a given state.*  
  Arguments:  
    - `state`: The state to load (e.g., ny).
    - `format`: Response format (optional; json or ics).
* `/v1/state_leg`  
  *State legislature election lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude
* `/v1/google_civic_info`  
  *Lookup Google Civic Info for an election.*  
  Arguments:  
    - `ocd_id`: An Open Civic Data ID for the election.
    - `address`: Address search string.
* `/v1/congress/scores`  
  *Index of congressional legislator scores.*  
  Arguments:  
* `/v1/pip`  
  *Point in polygon election lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude
    - `id`: Hyphen-separated list of numeric IDs (alternative to lat/lng)
    - `state`: Instead of lat/lng or id, specify a state (e.g., state=ny)
* `/v1/apple_wallet`  
  *Get an Apple Wallet pkpass based on polling place info.*  
  Arguments:  
    - `hours`: The polling place hours
    - `lat`: Latitude
    - `lng`: Longitude
    - `address`: The polling place address
* `/v1/congress/legislators`  
  *Index of all congressional legislators.*  
  Arguments:  
    - `include`: Fields to include (optional; include=name)
    - `id`: Numeric part of aclu_id (optional; returns a single match).
    - `url_slug`: State and name URL slug (optional; returns a single match).
* `/v1/congress`  
  *Congress election lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude
* `/v1/county`  
  *County election lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude
* `/v1/state`  
  *State election lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude
* `/v1/congress/district`  
  *Congressional district lookup by location.*  
  Arguments:  
    - `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
    - `lat`: Latitude
    - `lng`: Longitude

You can also load `/v1` for a structured summary of the endpoints.

## Dependencies

* [PostgreSQL](https://www.postgresql.org/)
* [PostGIS](http://postgis.net/)
* [Flask](http://flask.pocoo.org/)
* [Gunicorn](http://gunicorn.org/)
* [nginx](https://www.nginx.com/)

## Setup process

The API server is designed to run on Ubuntu 16.04.

```
sudo mkdir -p /usr/local/aclu
sudo chown $USER:$USER /usr/local/aclu
cd /usr/local/aclu
git clone https://github.com/aclu-national/elections-api.git
cd elections-api
sudo ./scripts/setup_ubuntu.sh
```

There is also a private repo of data we cannot release. You can include it as a submodule if you work at the ACLU and have access to the repo.

```
git submodule init
git submodule update
```

## Reindexing the data

Whenever updates are made to the data, PostGIS needs to be reindexed. This can take several minutes, so you'll want to be careful to only reindex machines that are out of the load balancer rotation.

```
cd /usr/local/aclu/elections-api
make
```

## Restarting the server

When the API server code changes, the application server needs to be restarted after `git pull`ing the changes. Be sure to create a CloudFront invalidation for the new results to take effect.

```
sudo service elections restart
```

## Load testing the server

Here's how you can use [`siege`](https://www.joedog.org/siege-home/) to simulate 50 concurrent requests using a list of 1,000 random lat/lng lookups within the U.S.A.

```
export SIEGE_SCHEME="https"
export SIEGE_HOST="elections.api.aclu.org"
siege -c 50 -t 15S -f server/test_urls.txt -i
```

## Data sources

* [Census TIGER/Line](https://www.census.gov/geo/maps-data/data/tiger-line.html)
* [The Unified Judicial System of Pennsylvania](http://www.pacourts.us/news-and-statistics/cases-of-public-interest/league-of-women-voters-et-al-v-the-commonwealth-of-pennsylvania-et-al-159-mm-2017)
* [@unitedstates](https://github.com/unitedstates/congress-legislators)
