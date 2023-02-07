# elections-api

An API for retrieving locally-relevant structured data about US elections.

## Origins

This API was originally created for [ACLU Voter](https://www.aclu.org/voter/) and was subsequently used by [Vote Smart Justice](https://www.votesmartjustice.org/). Is currently used by [https://github.com/aclu-national/scorecards/](scorecards).

## Calling the API

The `pip` ([point-in-polygon](https://en.wikipedia.org/wiki/Point_in_polygon)) endpoint provides most of the details available from the API.

```
$ curl -s 'https://elections.api.aclu.org/v2/pip?lat=40.7023699&lng=-74.012632' | python -mjson.tool
```

Output: [example-output.json](example-output.json)
Documentation: [API endpoints](/docs/endpoints.md)

## Documentation

* [API endpoints](/docs/endpoints.md)
* [How to install](/docs/install.md)
* [Care and maintenance](/docs/maintenance.md)
* [Common tasks](docs/tasks.md)

## See also

Related private ACLU repositories:

* [voter-apple-wallet](https://github.com/aclu-national/voter-apple-wallet)
* [elections-api-private](https://github.com/aclu-national/elections-api-private)

## Data sources

* [Census TIGER/Line](https://www.census.gov/geo/maps-data/data/tiger-line.html)
* [The Unified Judicial System of Pennsylvania](http://www.pacourts.us/news-and-statistics/cases-of-public-interest/league-of-women-voters-et-al-v-the-commonwealth-of-pennsylvania-et-al-159-mm-2017)
* [@unitedstates](https://github.com/unitedstates/congress-legislators)
* [Ballotpedia](https://ballotpedia.org/Main_Page) (not available for public release)
