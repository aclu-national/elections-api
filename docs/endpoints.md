## API Endpoints (v2)

All endpoints expect an HTTP GET request and respond in JSON format. The base URL for API requests is `https://elections.api.aclu.org`.

### `/v2/apple_wallet`

*Get an Apple Wallet pkpass based on polling place info.*

Arguments:
* `address`: The polling place address
* `hours`: The polling place hours
* `lat`: Latitude
* `lng`: Longitude

### `/v2/calendar`

*Get an election calendar for a given state.*

Arguments:
* `format`: Response format (optional; json or ics).
* `state`: The state to load (e.g., ny).

### `/v2/congress`

*Congress election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v2/congress/district`

*Congressional district lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v2/congress/legislators`

*Index of all congressional legislators.*

Arguments:
* `id`: Numeric part of aclu_id (optional; returns a single match).
* `include`: Fields to include (optional; include=name)
* `session`: Congressional session (optional; defaults to 116)
* `url_slug`: State and name URL slug (optional; returns a single match).

### `/v2/congress/scores`

*Index of congressional legislator scores.*

Arguments:
* `session`: Congressional session (optional; defaults to 116)

### `/v2/county`

*County election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v2/geoip`

*Get an approximate lat/lng location based on IPv4.*

Arguments:
* `ip`: The IPv4 address to look up (optional; e.g., 38.109.115.130)
* `legislators`: Use the resulting location to do a point-in-polygon congress_legislators lookup. (optional; set to 1 to include)
* `pip`: Use the resulting location to do a point-in-polygon lookup. (optional; set to 1 to include state-level pip results)

### `/v2/google_civic_info`

*Lookup Google Civic Info for an election.*

Arguments:
* `address`: Address search string.
* `ocd_id`: An Open Civic Data ID for the election.

### `/v2/pip`

*Point in polygon election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `id`: Hyphen-separated list of numeric IDs (alternative to lat/lng)
* `lat`: Latitude
* `lng`: Longitude
* `state`: Instead of lat/lng or id, specify a state (e.g., state=ny)

### `/v2/state`

*State election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude

### `/v2/state_leg`

*State legislature election lookup by location.*

Arguments:
* `geometry`: Include GeoJSON geometries with districts (optional; geometry=1)
* `lat`: Latitude
* `lng`: Longitude
