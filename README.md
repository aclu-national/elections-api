# elections-api

US elections data API.

## Endpoints

All endpoints support `GET` requests and respond in JSON format.

```
curl https://elections.api.aclu.org/pip?lat=40.7023699&lng=-74.012632 | jq .
```

You can query the Elections API by location using one of the following endpoints:

* `/v1/pip` - Point in polygon election lookup by location.
* `/v1/state` - State election lookup by location.
* `/v1/congress` - Congress election lookup by location.
* `/v1/congress/district` - Congressional district lookup by location.
* `/v1/congress/scores` - Index of congressional legislator scores.
* `/v1/county` - County election lookup by location.
* `/v1/state_leg` - State legislature election lookup by location.
* `/v1/blurbs` - Descriptive blurbs about various elected positions.

You can also load `/v1` for more documentation about each endpoint.

## Dependencies

* [PostgreSQL](https://www.postgresql.org/)
* [PostGIS](http://postgis.net/)
* [Flask](http://flask.pocoo.org/)
* [Gunicorn](http://gunicorn.org/)
* [nginx](https://www.nginx.com/)

## Setup process

The API server is designed to run on Ubuntu 16.04. This assumes you are SSH'd into a machine with agent forwarding.

```
sudo mkdir -p /usr/local/aclu
sudo chown $USER:$USER /usr/local/aclu
cd /usr/local/aclu
git clone git@github.com:aclu-national/elections-api.git
cd elections-api
sudo ./scripts/setup_ubuntu.sh
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

## Data sources

* [Census TIGER/Line](https://www.census.gov/geo/maps-data/data/tiger-line.html)
* [The Unified Judicial System of Pennsylvania](http://www.pacourts.us/news-and-statistics/cases-of-public-interest/league-of-women-voters-et-al-v-the-commonwealth-of-pennsylvania-et-al-159-mm-2017)
* [@unitedstates](https://github.com/unitedstates/congress-legislators)
