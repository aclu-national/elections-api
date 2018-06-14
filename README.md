# elections-api

US elections data API.

## Endpoints

All endpoints support `GET` requests and respond in JSON format.

```
curl https://elections.api.aclu.org/pip?lat=40.7023699&lng=-74.012632 | jq .
```

### Point in polygon

You can query the Elections API by location using one of the following endpoints:

* `/pip` - point in polygon lookup for __all__ records
* `/pip_state` - point in polygon lookup for __state__ records
* `/pip_congress` - point in polygon lookup for __congressional district__ records
* `/pip_county` - point in polygon lookup for __county__ records
* `/pip_state_leg` - point in polygon lookup for __state legislature__ records

__Required arguments__  
* `lat` - latitude
* `lng` - longitude

__Optional arguments__
* `scores` - congressional legislator score filter, defaults to `voted`. Set to `all` to get all scores, including those where the legislators did not vote. Only applies to `/pip` and `/pip_congress`.

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
