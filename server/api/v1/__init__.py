__import__('pkg_resources').declare_namespace(__name__)

import flask, json, os, re, sys, arrow

api = flask.Blueprint('api', __name__)

def get_races_by_ocd_id(ocd_id, year = '2018'):

	races = {}
	election_dates = [
		'primary_date',
		'primary_runoff_date',
		'general_date',
		'general_runoff_date'
	]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT name, year, type, primary_date, primary_runoff_date,
		       general_date, general_runoff_date
		FROM election_races
		WHERE ocd_id = %s
		  AND year = %s
	''', (ocd_id, year))

	rs = cur.fetchall()

	if rs:
		for row in rs:

			elections = {
				'primary_date': row[3],
				'primary_runoff_date': row[4],
				'general_date': row[5],
				'general_runoff_date': row[6]
			}

			for date in election_dates:
				if elections[date]:
					date_formatted = arrow.get(elections[date]).format('YYYY-MM-DD')
					if not date_formatted in races:
						races[date_formatted] = []
					races[date_formatted].append({
						'name': row[0],
						'election': re.sub('_date$', '', date),
						'type': row[2].lower()
					})

	return races

def get_state_by_coords(lat, lng):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT aclu_id, geoid, ocd_id, name, state, area_land, area_water
		FROM states
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:
			state = {
				'aclu_id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'area_land': row[5],
				'area_water': row[6]
			}

	cur.close()
	return state

def get_state_by_abbrev(abbrev):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT aclu_id, geoid, ocd_id, name, state, area_land, area_water
		FROM states
		WHERE state = '{state}'
	'''.format(state=abbrev))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:
			state = {
				'aclu_id': row[0],
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

	columns = 'aclu_id, geoid, ocd_id, name, start_session, end_session, state, district_num, area'
	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM congress_districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
		  AND (district_num > 0 OR at_large_only = 'Y')
		  AND start_session <= {session_num}
		  AND end_session >= {session_num}
	'''.format(columns=columns, lat=lat, lng=lng, session_num=session_num))

	rs = cur.fetchall()
	district = None

	if rs:
		for row in rs:

			aclu_id = row[0]
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
				'aclu_id': aclu_id,
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
		SELECT aclu_id, geoid, ocd_id, name, start_session, end_session, state, district_num, area
		FROM congress_districts
		WHERE id = {id}
	'''.format(id=id))

	rs = cur.fetchall()
	district = None

	if rs:
		for row in rs:

			aclu_id = row[0]
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
				'aclu_id': aclu_id,
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
		SELECT aclu_id, geoid, ocd_id, name, state, area_land, area_water
		FROM counties
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state = None

	if rs:
		for row in rs:

			county = {
				'aclu_id': row[0],
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
		SELECT aclu_id, geoid, ocd_id, name, state, chamber, district_num, area_land, area_water
		FROM state_leg
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	state_legs = {}

	if rs:
		for row in rs:

			chamber = row[5]

			state_legs[chamber] = {
				'aclu_id': row[0],
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
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
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
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
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
	aclu_ids = []
	term_ids = []

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[1]
			legislators[aclu_id] = {
				'term': {
					'start_date': arrow.get(row[2]).format('YYYY-MM-DD'),
					'end_date': arrow.get(row[3]).format('YYYY-MM-DD'),
					'type': row[4],
					'state': row[5],
					'party': row[7]
				}
			}
			if row[4] == 'rep':
				legislators[aclu_id]['term']['district_num'] = row[6]
			aclu_ids.append(aclu_id)
			term_ids.append(str(row[0]))

	if len(aclu_ids) == 0:
		return {}

	aclu_ids = "'" + "', '".join(aclu_ids) + "'"
	term_ids = ", ".join(term_ids)

	cur.execute('''
		SELECT aclu_id, first_name, last_name, full_name, birthday, gender
		FROM congress_legislators
		WHERE aclu_id IN ({aclu_ids})
		ORDER BY last_name, first_name
	'''.format(aclu_ids=aclu_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			legislators[aclu_id]['name'] = {
				'first_name': row[1],
				'last_name': row[2],
				'full_name': row[3]
			}
			legislators[aclu_id]['bio'] = {
				'birthday': arrow.get(row[4]).format('YYYY-MM-DD'),
				'gender': row[5]
			}

	cur.execute('''
		SELECT aclu_id, detail_name, detail_value
		FROM congress_legislator_term_details
		WHERE term_id IN ({term_ids})
	'''.format(term_ids=term_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			key = row[1]
			value = row[2]
			if key == 'class' or key == 'state_rank':
				legislators[aclu_id]['term'][key] = value
			else:
				if not 'contact' in legislators[aclu_id]:
					legislators[aclu_id]['contact'] = {}
				legislators[aclu_id]['contact'][key] = value

	cur.execute('''
		SELECT aclu_id, concordance_name, concordance_value
		FROM congress_legislator_concordances
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			key = row[1]
			value = row[2]
			if not 'id' in legislators[aclu_id]:
				legislators[aclu_id]['id'] = {}
			legislators[aclu_id]['id'][key] = value
			if key == 'bioguide':
				path = 'congress_photos/%s.jpg' % value
				abs_path = '/usr/local/aclu/elections-api/data/%s' % path
				if os.path.isfile(abs_path):
					url_root = flask.request.url_root
					if re.search('elb\.amazonaws\.com', url_root):
						url_root = 'https://elections.api.aclu.org/'
					legislators[aclu_id]['photo'] = "%s%s" % (url_root, path)

	cur.execute('''
		SELECT aclu_id, social_media_name, social_media_value
		FROM congress_legislator_social_media
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			key = row[1]
			value = row[2]
			if not 'social' in legislators[aclu_id]:
				legislators[aclu_id]['social'] = {}
			legislators[aclu_id]['social'][key] = value

	score_filter = flask.request.args.get('scores', 'voted')

	cur.execute('''
		SELECT aclu_id, legislator_id, position, name, value
		FROM congress_legislator_scores
		WHERE legislator_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_ids))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			legislator_id = row[1]
			position = row[2]
			name = row[3]
			value = row[4]

			if not 'scores' in legislators[legislator_id]:
				legislators[legislator_id]['scores'] = []

			if name == 'total':
				legislators[legislator_id]['total_score'] = value
			else:
				score = {
					'aclu_id': aclu_id,
					'aclu_position': position,
					'name': name,
					'status': 'unknown'
				}
				if value == '1' or value == '0':
					score['vote'] = int(value)
					score['status'] = 'voted'
				elif value == 'Missed':
					score['status'] = 'missed'
				elif value == 'Not yet in office':
					score['status'] = 'not_in_office'
				elif value == 'Not on committee':
					score['status'] = 'not_on_committee'

				if score_filter == 'all' or score_filter == score['status']:
					legislators[legislator_id]['scores'].append(score)

	cur.close()

	legislator_list = []
	for aclu_id in legislators:
		legislator_list.append(legislators[aclu_id])

	return legislator_list

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

@api.route("/")
def index():
	return flask.jsonify({
		'ok': 0,
		'error': 'Please pick a valid endpoint.',
		'valid_endpoints': {
			'/v1/pip': {
				'lat': 'Latitude',
				'lng': 'Longitude',
				'scores': 'Congress legislator score filter (optional)'
			},
			'/v1/state': {
				'lat': 'Latitude',
				'lng': 'Longitude'
			},
			'/v1/congress': {
				'lat': 'Latitude',
				'lng': 'Longitude',
				'scores': 'Congress legislator score filter (optional)'
			},
			'/v1/congress/district': {
				'lat': 'Latitude',
				'lng': 'Longitude'
			},
			'/v1/congress/scores': {},
			'/v1/county': {
				'lat': 'Latitude',
				'lng': 'Longitude'
			},
			'/v1/state_leg': {
				'lat': 'Latitude',
				'lng': 'Longitude'
			}
		}
	})

@api.route("/pip")
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

@api.route("/state")
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
		'congress': {
			'legislators': legislators
		}
	})

@api.route("/congress")
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

@api.route("/congress/district")
def congress_district():
	req = get_lat_lng()

	if type(req) == str:
		return flask.jsonify({
			'ok': 0,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	district = get_district_by_coords(lat, lng)

	return flask.jsonify({
		'ok': 1,
		'district': district
	})

@api.route("/congress/scores")
def congress_scores():

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT aclu_id, vote_context, roll_call, vote_date, vote_type, bill,
		       amendment, title, description, committee, link
		FROM congress_legislator_score_index
		ORDER BY aclu_id
	''')

	scores = []

	rs = cur.fetchall()
	if rs:
		for row in rs:
			scores.append({
				'aclu_id': row[0],
				'vote_context': row[1],
				'roll_call': row[2],
				'vote_date': arrow.get(row[3]).format('YYYY-MM-DD'),
				'vote_type': row[4],
				'bill': row[5],
				'amendment': row[6],
				'title': row[7],
				'description': row[8],
				'committee': row[9],
				'link': row[10]
			})

	return flask.jsonify({
		'ok': 1,
		'congress_scores': scores
	})

@api.route("/county")
def pip_county():
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

@api.route("/state_leg")
def pip_state_leg():
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
