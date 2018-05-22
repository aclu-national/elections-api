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

def get_district_by_coords(lat, lng, session_num=115):

	columns = 'id, name, start_session, end_session, state, district_num, area'
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

			start_session = row[2]
			end_session = row[3]
			district_num = row[5]

			at_large = (district_num == 0)
			non_voting = (district_num == 98)

			district = {
				'id': row[0],
				'name': row[1],
				'start_session': start_session,
				'end_session': end_session,
				'start_date': flask.g.sessions[start_session]['start_date'],
				'end_date': flask.g.sessions[end_session]['end_date'],
				'state': row[4],
				'district_num': district_num,
				'area': row[6],
				'at_large': at_large,
				'non_voting': non_voting
			}

	cur.close()
	return district

def get_district_by_id(id):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, name, start_session, end_session, state, district_num, area
		FROM districts
		WHERE id = {id}
	'''.format(id=id))

	rs = cur.fetchall()
	district = None

	if rs:
		for row in rs:
			start_session = row[2]
			end_session = row[3]
			district_num = row[5]

			at_large = (district_num == 0)
			non_voting = (district_num == 98)

			district = {
				'id': row[0],
				'start_session': start_session,
				'end_session': end_session,
				'start_date': flask.g.sessions[start_session]['start_date'],
				'end_date': flask.g.sessions[end_session]['end_date'],
				'state': row[4],
				'district_num': district_num,
				'area': row[6],
				'at_large': at_large,
				'non_voting': non_voting
			}

	cur.close()
	return district

def get_legislators(state, district_num, session_num=115):

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

@app.route("/")
def hello():
	return "Hello, you probably want to use: /pip, /district, or /session"

@app.route("/pip")
def pip():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include 'lat' and 'lng' args."

	if not re.match('^-?\d+(\.\d+)?', lat):
		return "Please include a numeric 'lat'."

	if not re.match('^-?\d+(\.\d+)?', lng):
		return "Please include a numeric 'lng'."

	district = get_district_by_coords(lat, lng)

	if not district:
		rsp = {
			'ok': 0,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators(district["state"], district["district_num"])
		rsp = {
			'ok': 1,
			'district': district,
			'legislators': legislators
		}

	return flask.jsonify(rsp)

@app.route("/district")
def district():

	id = flask.request.args.get('id', None)

	if id == None:
		return "Please include 'id' arg."

	if not re.match('^\d+$', id):
		return "Please specify one numeric 'id' arg."

	district = get_district_by_id(id)

	if not district:
		rsp = {
			'ok': 0,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators(district["state"], district["district_num"])
		rsp = {
			'ok': 1,
			'district': district,
			'legislators': legislators
		}

	return flask.jsonify(rsp)

@app.route("/sessions")
def sessions():
	rsp = {
		'ok': 1,
		'results': flask.g.sessions
	}
	return flask.jsonify(rsp)

if __name__ == '__main__':
	port = os.getenv('PORT', 5000)
	port = int(port)
	app.run(host='0.0.0.0', port=port)
