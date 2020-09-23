[*ACLU Elections API*](https://github.com/aclu-national/elections-api)

## API Endpoints (v2)

All endpoints expect an HTTP GET request and respond in JSON format. The base URL for API requests is `https://elections.api.aclu.org`.

### `/v2/apple_wallet`

*Get an Apple Wallet pkpass based on polling place info.*

Arguments:
* `address`: The polling place address
* `hours`: The polling place hours
* `lat`: Latitude
* `lng`: Longitude

[Old V1 lookup](https://elections-stg.api.aclu.org/v1/apple_wallet?address=30%20Rockefeller%20Plaza%2C%20New%20York%2C%20NY%2010111&hours=6am-9pm&lat=40.7591837&lng=-73.9818335) (V2 version is returning an invalid pass as of 04/2020)

### `/v2/calendar`

*Get an election calendar for a given state.*

Arguments:
* `format`: Response format (optional; json or ics).
* `state`: The state to load (e.g., ny).

[Example lookup](https://elections.api.aclu.org/v2/calendar?state=ca) | [Example response](./responses/v2-calendar.js)

### `/v2/congress`

*Congress election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

[Example lookup](https://elections.api.aclu.org/v2/congress?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-congress.js)

### `/v2/congress/district`

*Congressional district lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

[Example lookup](https://elections.api.aclu.org/v2/congress/district?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-congress-district.js) | [Example response with geometry](./responses/v2-congress-district-with-geometry.js)

### `/v2/congress/legislators`

*Index of all congressional legislators.*

Arguments:
* `id`: Numeric part of aclu_id (optional; returns a single match).
* `include`: Fields to include (optional; include=name)
* `session`: Congressional session (optional; defaults to 116)
* `url_slug`: State and name URL slug (optional; returns a single match).

[Example lookup](https://elections.api.aclu.org/v2/congress/legislators?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-congress-legislators.js)

### `/v2/congress/scores`

*Index of congressional legislator scores.*

Arguments:
* `session`: Congressional session (optional; defaults to 116)

[Example lookup](https://elections.api.aclu.org/v2/congress/scores?session=116) | [Example response](./responses/v2-congress-scores.js)

### `/v2/county`

*County election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

[Example lookup](https://elections.api.aclu.org/v2/county?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-county.js)

### `/v2/geoip`

*Get an approximate lat/lng location based on IPv4.*

Arguments:
* `ip`: The IPv4 address to look up (optional; e.g., 38.109.115.130)
* `legislators`: Use the resulting location to do a point-in-polygon congress_legislators lookup. (optional; set to 1 to include)
* `pip`: Use the resulting location to do a point-in-polygon lookup. (optional; set to 1 to include state-level pip results)

[Example lookup](https://elections.api.aclu.org/v2/geoip) | [Example response](./responses/v2-geoip.js)

### `/v2/google_civic_info`

*Look up [Google Civic Info](https://developers.google.com/civic-information) for an election. Information is only available and returned during an election.*

Arguments:
* `address`: Address search string.
* `ocd_id`: An Open Civic Data ID for the election.

[Example lookup](https://elections.api.aclu.org/v2/google_civic_info?ocd_id=ocd-division%2Fcountry%3Aus%2Fstate%3Aga&address=878%20Peachtree%20Street%20Northeast%2C%20Atlanta%2C%20GA%2030309)

### `/v2/pip`

*Point in polygon election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `id`: Hyphen-separated list of numeric IDs (alternative to lat/lng)
* `lat`: Latitude
* `lng`: Longitude
* `state`: Instead of lat/lng or id, specify a state (e.g., state=ny)

[Example lookup](https://elections.api.aclu.org/v2/pip?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-pip.js)

### `/v2/state`

*State election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude
* `state`: Instead of lat/lng or id, specify a state (e.g., state=ny)

[Example lookup](https://elections.api.aclu.org/v2/state?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-state.js)

### `/v2/state_leg`

*State legislature election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

[Example lookup](https://elections.api.aclu.org/v2/state_leg?lat=40.7023587&lng=-74.0124621) | [Example response](./responses/v2-state_leg.js)

