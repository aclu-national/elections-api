import flask, json, os, re, sys, arrow, requests, psycopg2, urllib, traceback
import mapbox as mapbox_api

api_key = os.getenv('GOOGLE_API_KEY', None)
postgres_dsn = os.getenv('POSTGRES_DSN', 'dbname=elections')
features = {
	'google_geocode': int(os.getenv('ENABLE_FEATURE_GOOGLE_GEOCODE', 0)),
	'polling_place_distance': int(os.getenv('ENABLE_FEATURE_POLLING_PLACE_DISTANCE', 0))
}

def setup():

	db = psycopg2.connect(postgres_dsn)
	cur = db.cursor()

	cur.execute('''
		CREATE TABLE IF NOT EXISTS google_civic_info (
			name VARCHAR(255) PRIMARY KEY,
			value TEXT,
			updated TIMESTAMP
		)
	''')
	db.commit()

def cache_get(name, ttl):

	utc = arrow.utcnow()
	expires = utc.shift(seconds=-ttl).format('YYYY-MM-DD HH:mm:ss')

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT value, updated
		FROM google_civic_info
		WHERE name = %s
		  AND updated > %s
	''', (name, expires))

	rsp = cur.fetchone()
	if rsp:
		return (rsp[0], rsp[1])
	else:
		return (None, None)

def cache_set(name, value):

	utc = arrow.utcnow()
	updated = utc.format('YYYY-MM-DD HH:mm:ss')

	cur = flask.g.db.cursor()

	cur.execute('''
		DELETE FROM google_civic_info
		WHERE name = %s
	''', (name,))

	cur.execute('''
		INSERT INTO google_civic_info
		(name, value, updated)
		VALUES (%s, %s, %s)
	''', (name, value, updated))

	flask.g.db.commit()

def get_elections():

	ttl = 60 * 60
	(cached, updated) = cache_get('elections', ttl)

	if cached:
		rsp = json.loads(cached)
	else:
		url = "https://www.googleapis.com/civicinfo/v2/elections?key=%s" % api_key
		rsp = requests.get(url)
		if rsp.status_code == 200:
			cache_set('elections', rsp.text)
		rsp = rsp.json()

	return rsp['elections']

def get_available_elections(ocd_ids):
	elections = get_elections()
	available = []
	for el in elections:

		election_id = el["id"]
		ocd_id = el['ocdDivisionId']

		# VIP Test Election
		if election_id == "2000":
			continue

		if ocd_id in available:
			continue

		if ocd_id in ocd_ids:
			available.append(ocd_id)
		elif election_id == "6000" and election_available(6000, ocd_ids):
			available.append(ocd_id)
	return available

def get_election_id(ocd_id):

	# just use the 2018 Midterms
	return "6000"

	elections = get_elections()
	for el in elections:
		if ocd_id.startswith(el['ocdDivisionId']) and el['id'] != "2000":
			return el['id']
	return None

def get_polling_places(ocd_id, address):

	cur = flask.g.db.cursor()
	election_id = get_election_id(ocd_id)

	if not election_id:
		return None

	rsp = get_voter_info(election_id, address)

	focus = {
		'lat': None,
		'lng': None
	}

	cache_key = "polling_places_focus:%s" % address
	ttl = 60 * 60 * 24
	(cached, updated) = cache_get(cache_key, ttl)

	if cached:
		focus = json.loads(cached)
		focus['_cache'] = 'hit'
		focus['_cache_generated'] = arrow.get(updated).to('US/Eastern').format('YYYY-MM-DD HH:mm:ss')
	else:
		if features['google_geocode']:
			focus = google_geocode(address)
		else:
			focus = mapbox_api.geocode(address)

		if focus:
			focus_json = json.dumps(focus)
			focus['_cache'] = 'miss'
			cache_set(cache_key, focus_json)

	rsp['focus'] = focus

	for key in ['pollingLocations', 'earlyVoteSites', 'dropOffLocations']:

		if key in rsp:

			if not features['polling_place_distance']:
				rsp[key] = rsp[key][:5] # only return the first 5 locations

			for location in rsp[key]:
				if location['address']['line1'] == "":
					continue
				zip = location['address']['zip']

				if len(zip) > 5:
					zip = zip[:5]

				address = '%s, %s, %s %s' % (
					location['address']['line1'],
					location['address']['city'],
					location['address']['state'],
					zip
				)

				cache_key = "polling_place:%s" % address
				ttl = 60 * 60 * 24
				(cached, updated) = cache_get(cache_key, ttl)

				if cached:
					geocoded = json.loads(cached)
					geocoded['_cache'] = 'hit'
					geocoded['_cache_generated'] = arrow.get(updated).to('US/Eastern').format('YYYY-MM-DD HH:mm:ss')
				else:
					if features['google_geocode']:
						geocoded = google_geocode(address)
					else:
						geocoded = mapbox_api.geocode(address, focus['lat'], focus['lng'])

					if geocoded:
						geocoded_json = json.dumps(geocoded)
						cache_set(cache_key, geocoded_json)
						geocoded['_cache'] = 'miss'

				if geocoded:
					location['geocoded'] = geocoded

					if features['polling_place_distance']:
						cur.execute('''
							SELECT st_distance(
								ST_Transform('SRID=4326;POINT({lng1} {lat1})'::geometry, 3857),
								ST_Transform('SRID=4326;POINT({lng2} {lat2})'::geometry, 3857)
							)
						'''.format(
							lat1=focus['lat'],
							lng1=focus['lng'],
							lat2=geocoded['lat'],
							lng2=geocoded['lng']
						))

						row = cur.fetchone()
						location['geocoded']['distance'] = row[0]

	return rsp


def get_voter_info(election_id, address):

	cache_key = "voter_info:%s:%s" % (election_id, address)
	ttl = 60 * 60
	(cached, updated) = cache_get(cache_key, ttl)

	if cached:
		rsp = json.loads(cached)
		rsp['_cache'] = 'hit'
		rsp['_cache_generated'] = arrow.get(updated).to('US/Eastern').format('YYYY-MM-DD HH:mm:ss')
	else:
		query = urllib.urlencode({
			'key': api_key,
			'electionId': election_id,
			'address': address
		})
		url = "https://www.googleapis.com/civicinfo/v2/voterinfo?%s" % query
		url += "&fields=dropOffLocations,earlyVoteSites,pollingLocations"
		rsp = requests.get(url)
		if rsp.status_code == 200:
			cache_set(cache_key, rsp.text)
		rsp = rsp.json()
		rsp['_cache'] = 'miss'

	return rsp

def election_available(election_id, ocd_ids):
	# TODO: respond according to https://docs.google.com/spreadsheets/d/11XD-WNjtNo3QMrGhDsiZH9qZ4N8RYmfpszJOZ_qH1g8/edit#gid=0
	return True

def google_geocode(address):

	# Takes an address string and returns a dict with lat/lng properties or
	# None. (20181029/dphiffer)

	address = address.encode("utf-8")
	query = urllib.quote_plus(address)
	url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (query, api_key)
	rsp = requests.get(url)

	if rsp.status_code != 200:
		return None

	try:
		rsp = rsp.json()
		result = rsp['results'][0]
		return result['geometry']['location']
	except:
		print("ERROR could not geocode %s" % address)
		print(traceback.format_exc())
		return None
