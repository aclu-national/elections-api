import flask, json, os, re, sys, arrow, requests, psycopg2, urllib
import mapbox as mapbox_api

api_key = os.getenv('GOOGLE_API_KEY', None)

def setup():
	default_dsn = 'dbname=elections'
	db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
	db = psycopg2.connect(db_dsn)
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
		SELECT value
		FROM google_civic_info
		WHERE name = %s
		  AND updated > %s
	''', (name, expires))

	rsp = cur.fetchone()
	if rsp:
		return rsp[0]
	else:
		return None

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

	global api_key

	ttl = 60 * 60
	cached = cache_get('elections', ttl)

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

	election_id = get_election_id(ocd_id)

	if not election_id:
		return None

	focus_lat = None
	focus_lng = None

	cache_key = "polling_places_focus:%s" % address
	ttl = 60 * 60 * 24
	cached = cache_get(cache_key, ttl)

	if cached:
		print("CACHE HIT focus lookup")
		focus = json.loads(cached)
	else:
		print("CACHE MISS focus lookup")
		focus = mapbox_api.geocode(address)
		if focus:
			focus_json = json.dumps(focus)
			cache_set(cache_key, focus_json)

	try:
		focus_lat = focus['features'][0]['center'][1]
		focus_lng = focus['features'][0]['center'][0]
	except:
		print("could not get polling place focus")

	rsp = get_voter_info(election_id, address)

	for key in ['pollingLocations', 'earlyVoteSites', 'dropOffLocations']:

		if key in rsp:
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
				cached = cache_get(cache_key, ttl)

				if cached:
					print("CACHE HIT polling place lookup")
					geocoded = json.loads(cached)
				else:
					print("CACHE MISS polling place lookup")
					geocoded = mapbox_api.geocode(address, focus_lat, focus_lng)
					if geocoded:
						geocoded_json = json.dumps(geocoded)
						cache_set(cache_key, geocoded_json)

				if geocoded and 'features' in geocoded and len(geocoded['features']) > 0:
					location['geocoded'] = {
						'lat': geocoded['features'][0]['center'][1],
						'lng': geocoded['features'][0]['center'][0]
					}

	return rsp


def get_voter_info(election_id, address):

	global api_key

	cache_key = "voter_info:%s:%s" % (election_id, address)
	ttl = 60 * 60
	cached = cache_get(cache_key, ttl)

	if cached:
		print("CACHE HIT civic info lookup")
		rsp = json.loads(cached)
	else:
		print("CACHE MISS civic info lookup")
		query = urllib.urlencode({
			'key': api_key,
			'electionId': election_id,
			'address': address
		})
		url = "https://www.googleapis.com/civicinfo/v2/voterinfo?%s" % query
		rsp = requests.get(url)
		if rsp.status_code == 200:
			cache_set(cache_key, rsp.text)
		rsp = rsp.json()

	return rsp

def election_available(election_id, ocd_ids):
	# TODO: respond according to https://docs.google.com/spreadsheets/d/11XD-WNjtNo3QMrGhDsiZH9qZ4N8RYmfpszJOZ_qH1g8/edit#gid=0
	return True
