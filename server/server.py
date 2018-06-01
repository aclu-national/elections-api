#!/usr/bin/env python

import flask, flask_cors, json, os, psycopg2, re, sys, arrow

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.before_request
def init():
	db_connect()
	setup_sessions()

def db_connect():
	default_dsn = 'dbname=elections'
	db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
	flask.g.db = psycopg2.connect(db_dsn)

def setup_sessions():
	flask.g.sessions = {}
	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, start_date, end_date
		FROM sessions
		ORDER BY id DESC
	''')

	rs = cur.fetchall()
	results = []
	if rs:
		for row in rs:
			id = row[0]
			flask.g.sessions[id] = {
				"start_date": str(row[1]),
				"end_date": str(row[2])
			}

def get_state_by_coords(lat, lng):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, geoid, ocd_id, name, state, area_land, area_water
		FROM states
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:

			state = {
				'id': row[0],
				'name': row[1],
				'state': row[2],
				'area_land': row[3],
				'area_water': row[4],
				'fips_id': row[5]
			}

	cur.close()
	return state

def get_state_by_abbrev(abbrev):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, geoid, ocd_id, name, state, area_land, area_water
		FROM states
		WHERE state = '{state}'
	'''.format(state=abbrev))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:

			state = {
				'id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'area_land': row[5],
				'area_water': row[6]
			}

	cur.close()
	return state

def get_district_by_coords(lat, lng, session_num=115):

	columns = 'id, geoid, ocd_id, name, start_session, end_session, state, district_num, area'
	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
		  AND (district_num > 0 OR at_large_only = 'Y')
		  AND start_session <= {session_num}
		  AND end_session >= {session_num}
	'''.format(columns=columns, lat=lat, lng=lng, session_num=session_num))

	rs = cur.fetchall()
	district = None

	if rs:
		for row in rs:

			id = row[0]
			geoid = row[1]
			ocd_id = row[2]
			name = row[3]
			start_session = row[4]
			end_session = row[5]
			state = row[6]
			district_num = row[7]
			area = row[8]

			at_large = (district_num == 0)
			non_voting = (district_num == 98)

			district = {
				'id': id,
				'geoid': geoid,
				'ocd_id': ocd_id,
				'name': name,
				'start_session': start_session,
				'end_session': end_session,
				'start_date': flask.g.sessions[start_session]['start_date'],
				'end_date': flask.g.sessions[end_session]['end_date'],
				'state': state,
				'district_num': district_num,
				'area': area,
				'at_large': at_large,
				'non_voting': non_voting
			}

	cur.close()
	return district

def get_district_by_id(id):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, geoid, ocd_id, name, start_session, end_session, state, district_num, area
		FROM districts
		WHERE id = {id}
	'''.format(id=id))

	rs = cur.fetchall()
	district = None

	if rs:
		for row in rs:

			id = row[0]
			geoid = row[1]
			ocd_id = row[2]
			name = row[3]
			start_session = row[4]
			end_session = row[5]
			state = row[6]
			district_num = row[7]
			area = row[8]

			at_large = (district_num == 0)
			non_voting = (district_num == 98)

			district = {
				'id': id,
				'geoid': geoid,
				'ocd_id': ocd_id,
				'name': name,
				'start_session': start_session,
				'end_session': end_session,
				'start_date': flask.g.sessions[start_session]['start_date'],
				'end_date': flask.g.sessions[end_session]['end_date'],
				'state': state,
				'district_num': district_num,
				'area': area,
				'at_large': at_large,
				'non_voting': non_voting
			}

	cur.close()
	return district

def get_county_by_coords(lat, lng):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, geoid, ocd_id, name, state, area_land, area_water
		FROM counties
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:

			county = {
				'id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'area_land': row[5],
				'area_water': row[6]
			}

	cur.close()
	return county

def get_state_legs_by_coords(lat, lng):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, geoid, ocd_id, name, state, chamber, district_num, area_land, area_water
		FROM state_leg
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state_legs = {}

	if rs:
		for row in rs:

			chamber = row[5]

			state_legs[chamber] = {
				'id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'chamber': chamber,
				'district_num': row[6],
				'area_land': row[7],
				'area_water': row[8]
			}

	cur.close()
	return state_legs

def get_legislators_by_state(state, session_num=115):

	session = flask.g.sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, bioguide, start_date, end_date, type, state, district_num, party
		FROM legislator_terms
		WHERE end_date >= CURRENT_DATE
		  AND state = '{state}'
		  AND type = 'sen'
		ORDER BY end_date DESC
	'''.format(state=state))

	return get_legislators(cur)

def get_legislators_by_district(state, district_num, session_num=115):

	session = flask.g.sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, bioguide, start_date, end_date, type, state, district_num, party
		FROM legislator_terms
		WHERE end_date >= CURRENT_DATE
		  AND state = '{state}'
		  AND (
			district_num IS NULL OR
			district_num = {district_num}
		  )
		ORDER BY end_date DESC
	'''.format(state=state, district_num=district_num))

	return get_legislators(cur)

def get_legislators(cur):

	legislators = {}
	bioguides = []
	term_ids = []

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = str(row[1])
			legislators[bioguide] = {
				'term': {
					'start_date': arrow.get(row[2]).format('YYYY-MM-DD'),
					'end_date': arrow.get(row[3]).format('YYYY-MM-DD'),
					'type': row[4],
					'state': row[5],
					'party': row[7]
				}
			}
			if row[4] == 'rep':
				legislators[bioguide]['term']['district_num'] = row[6]
			bioguides.append(bioguide)
			term_ids.append(str(row[0]))

	if len(bioguides) == 0:
		return {}

	bioguides = "'" + "', '".join(bioguides) + "'"
	term_ids = ", ".join(term_ids)

	cur.execute('''
		SELECT bioguide, first_name, last_name, full_name, birthday, gender
		FROM legislators
		WHERE bioguide IN ({bioguides})
		ORDER BY last_name, first_name
	'''.format(bioguides=bioguides))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = row[0]
			legislators[bioguide]['name'] = {
				'first_name': row[1],
				'last_name': row[2],
				'full_name': row[3]
			}
			legislators[bioguide]['bio'] = {
				'birthday': arrow.get(row[4]).format('YYYY-MM-DD'),
				'gender': row[5]
			}

	cur.execute('''
		SELECT bioguide, detail_name, detail_value
		FROM legislator_term_details
		WHERE term_id IN ({term_ids})
	'''.format(term_ids=term_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = row[0]
			key = row[1]
			value = row[2]
			if key == 'class' or key == 'state_rank':
				legislators[bioguide]['term'][key] = value
			else:
				if not 'contact' in legislators[bioguide]:
					legislators[bioguide]['contact'] = {}
				legislators[bioguide]['contact'][key] = value

	cur.execute('''
		SELECT bioguide, concordance_name, concordance_value
		FROM legislator_concordances
		WHERE bioguide IN ({bioguides})
	'''.format(bioguides=bioguides))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = row[0]
			key = row[1]
			value = row[2]
			if not 'id' in legislators[bioguide]:
				legislators[bioguide]['id'] = {}
			legislators[bioguide]['id'][key] = value

	cur.execute('''
		SELECT bioguide, social_media_name, social_media_value
		FROM legislator_social_media
		WHERE bioguide IN ({bioguides})
	'''.format(bioguides=bioguides))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = row[0]
			key = row[1]
			value = row[2]
			if not 'social' in legislators[bioguide]:
				legislators[bioguide]['social'] = {}
			legislators[bioguide]['social'][key] = value

	cur.execute('''
		SELECT bioguide, category, subcategory, position, name, value
		FROM legislator_scores
		WHERE bioguide IN ({bioguides})
	'''.format(bioguides=bioguides))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			bioguide = row[0]
			category = row[1].strip()
			subcategory = row[2].strip()
			position = row[3]
			name = row[4]
			value = row[5]

			if not 'scores' in legislators[bioguide]:
				legislators[bioguide]['scores'] = {}

			if category == '':
				if not 'summary' in legislators[bioguide]['scores']:
					legislators[bioguide]['scores']['summary'] = []
				legislators[bioguide]['scores']['summary'].append({
					'name': position,
					'value': value
				})
			else:

				if not category in legislators[bioguide]['scores']:
					legislators[bioguide]['scores'][category] = {}

				if not subcategory in legislators[bioguide]['scores'][category]:
					legislators[bioguide]['scores'][category][subcategory] = []

				legislators[bioguide]['scores'][category][subcategory].append({
					'name': name,
					'position': position,
					'value': value
				})

	cur.close()
	return legislators

def get_lat_lng():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include 'lat' and 'lng' args."

	if not re.match('^-?\d+(\.\d+)?', lat):
		return "Please include a numeric 'lat'."

	if not re.match('^-?\d+(\.\d+)?', lng):
		return "Please include a numeric 'lng'."

	return {
		'lat': lat,
		'lng': lng
	}

def get_congress(lat, lng):

	district = get_district_by_coords(lat, lng)

	if not district:
		rsp = {
			'ok': 0,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators_by_district(district["state"], district["district_num"])
		rsp = {
			'ok': 1,
			'district': district,
			'legislators': legislators
		}

	return rsp

@app.route("/")
def hello():
	return '''
<pre>Hello, you probably want to use:

	<a href="/pip">/pip</a>
	<a href="/pip_state">/pip_state</a>
	<a href="/pip_congress">/pip_congress</a>
	<a href="/pip_county">/pip_county</a>
	<a href="/pip_state_leg">/pip_state_leg</a>
	<a href="/congress_district">/congress_district</a></pre>
	'''

@app.route("/pip")
def pip():
	req = get_lat_lng()
	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	congress = get_congress(lat, lng)
	if (congress["ok"] == 1):
		del congress["ok"]

	state = get_state_by_abbrev(congress['district']['state'])
	county = get_county_by_coords(lat, lng)
	state_legs = get_state_legs_by_coords(lat, lng)

	return flask.jsonify({
		'ok': 1,
		'congress': congress,
		'state': state,
		'county': county,
		'state_leg': state_legs
	})

@app.route("/pip_state")
def state():
	req = get_lat_lng()

	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = get_state_by_coords(lat, lng)
	if rsp == None:
		return flask.jsonify({
			'ok': 0,
			'error': 'No state found.'
		})

	legislators = get_legislators_by_state(rsp['state'])

	return flask.jsonify({
		'ok': 1,
		'state': rsp,
		'legislators': legislators
	})

@app.route("/pip_congress")
def congress():
	req = get_lat_lng()
	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = get_congress(lat, lng)
	return flask.jsonify({
		'ok': 1,
		'congress': rsp
	})

@app.route("/pip_county")
def county():
	req = get_lat_lng()

	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = get_county_by_coords(lat, lng)
	if rsp == None:
		return flask.jsonify({
			'ok': 0,
			'error': 'No county found.'
		})

	return flask.jsonify({
		'ok': 1,
		'county': rsp
	})

@app.route("/pip_state_leg")
def state_leg():
	req = get_lat_lng()

	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = get_state_legs_by_coords(lat, lng)
	if len(rsp) == 0:
		return flask.jsonify({
			'ok': 0,
			'error': 'No state legislation found.'
		})

	return flask.jsonify({
		'ok': 1,
		'state_leg': rsp
	})

@app.route("/congress_district")
def district():

	id = flask.request.args.get('id', None)

	if id == None:
		return flask.jsonify({
			'ok': 0,
			'error': "Please include 'id' arg."
		})

	if not re.match('^\d+$', id):
		return flask.jsonify({
			'ok': 0,
			'error': "Please specify one numeric 'id' arg."
		})

	district = get_district_by_id(id)

	if not district:
		rsp = {
			'ok': 0,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators_by_district(district["state"], district["district_num"])
		rsp = {
			'ok': 1,
			'district': district,
			'legislators': legislators
		}

	return flask.jsonify(rsp)

if __name__ == '__main__':
	port = os.getenv('PORT', 5000)
	port = int(port)
	app.run(host='0.0.0.0', port=port)
