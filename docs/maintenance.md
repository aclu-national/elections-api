# Care and maintenance

The Elections API is designed to be have its code and data updated while it's running.

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

## Congress scores

Congressional scorecard data is not part of the public-facing release of the Elections API, so this only applies for the instance run and maintained by ACLU.

If you want to update the scores, by running `make congress_scores`, make sure to run `make congress_details` first. You can chain these together as one command: `make congress_details && make congress_scores`. The reason for this is that some the aggregate score info (e.g., total votes) is stored in the same table as the `congress_details`.

## Restarting the server

When the API server code changes, the application server needs to be restarted after `git pull`ing the changes. Be sure to also create a CloudFront invalidation for the new results to take effect.

```
$ sudo service elections restart
```

## Restarting Ubuntu

When you ssh into the box and get a message like `*** System restart required ***` just reboot ubuntu

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
