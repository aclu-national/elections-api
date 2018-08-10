__import__('pkg_resources').declare_namespace(__name__)

import flask, json, os, re, sys, arrow, us
import helpers
import congress as congress_api
import state as state_api
import county as county_api
import state_leg as state_leg_api
import elections as elections_api
import google_civic_info as google_civic_info_api
import mapbox as mapbox_api
from copy import deepcopy
from ics import Calendar, Event
import maxminddb

api = flask.Blueprint('api', __name__)

google_civic_info_api.setup()

@api.route("/")
def index():
	return flask.jsonify({
		'ok': False,
		'error': 'Please pick a valid endpoint.',
		'valid_endpoints': {
			'/v1/pip': {
				'description': 'Point in polygon election lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'id': 'Hyphen-separated list of numeric IDs (alternative to lat/lng)',
					'scores': 'Congress legislator score filter (optional; scores=all)',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/state': {
				'description': 'State election lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/congress': {
				'description': 'Congress election lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'scores': 'Congress legislator score filter (optional; scores=all)',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/congress/district': {
				'description': 'Congressional district lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/congress/scores': {
				'description': 'Index of congressional legislator scores.',
				'args': {}
			},
			'/v1/congress/legislators': {
				'description': 'Index of all congressional legislators.',
				'args': {
					'id': 'Numeric part of aclu_id (optional; returns a single match).',
					'url_slug': 'State and name URL slug (optional; returns a single match).'
				}
			},
			'/v1/county': {
				'description': 'County election lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/state_leg': {
				'description': 'State legislature election lookup by location.',
				'args': {
					'lat': 'Latitude',
					'lng': 'Longitude',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)'
				}
			},
			'/v1/google_civic_info': {
				'description': 'Lookup Google Civic Info for an election.',
				'args': {
					'ocd_id': 'An Open Civic Data ID for the election.',
					'address': 'Address search string.'
				}
			},
			'/v1/calendar': {
				'description': 'Get an election calendar for a given state.',
				'args': {
					'state': 'The state to load (e.g., ny).',
					'format': 'Response format (optional; json or ics).'
				}
			},
			'/v1/geoip': {
				'description': 'Get an approximate lat/lng location based on IPv4.',
				'args': {
					'ip': 'The IPv4 address to look up (e.g., 38.109.115.130)'
				}
			}
		}
	})

@api.route("/pip")
def pip():

	req = helpers.get_spatial_request()
	areas = []
	calendar_url = None

	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	if 'lat' in req and 'lng' in req:
		lat = req['lat']
		lng = req['lng']

		congress = congress_api.get_congress_by_coords(lat, lng)
		if (congress["ok"]):
			del congress["ok"]
			state = state_api.get_state_by_abbrev(congress['district']['state'])
		else:
			state = state_api.get_state_by_coords(lat, lng)

		county = county_api.get_county_by_coords(lat, lng)
		state_legs = state_leg.get_state_legs_by_coords(lat, lng)

	else:
		congress = None
		state = None
		if 'congress_district' in req:
			congress = congress_api.get_congress_by_id(req['congress_district'])
			if (congress["ok"]):
				del congress["ok"]
				state = state_api.get_state_by_abbrev(congress['district']['state'])

		if congress and 'next_congress_district' in req:
			next_congress = congress_api.get_congress_by_id(req['next_congress_district'])
			congress['next_district'] = next_congress['district']

		if not state and 'state' in req:
			state = state_api.get_state_by_id(req['state'])

		county = None
		if 'county' in req:
			county = county_api.get_county_by_id(req['county'])

		state_legs = []
		if 'state_leg' in req:
			state_legs = state_leg.get_state_legs_by_ids(req['state_leg'])

	if state:
		areas.append(state)
		api_url = os.getenv('API_URL', '')
		calendar_url = "%s/v1/calendar?state=%s&format=ics" % (api_url, state['state'])

	if county:
		areas.append(county)

	if len(state_legs) > 0:
		areas = areas + state_legs

	if congress and 'next_district' in congress:
		areas_plus_curr_congress = deepcopy(areas)
		if 'district' in congress:
			areas_plus_curr_congress.append(congress['district'])
			areas_plus_curr_congress.append(congress['next_district'])
		areas.append(congress['next_district'])
	elif congress and 'district' in congress:
		if 'district' in congress:
			areas.append(congress['district'])
		areas_plus_curr_congress = deepcopy(areas)
	else:
		areas_plus_curr_congress = deepcopy(areas)

	ocd_ids = helpers.get_ocd_ids(areas)

	aclu_ids = flask.request.args.get('id', None)
	if not aclu_ids:
		aclu_ids = helpers.get_aclu_ids(areas_plus_curr_congress)

	elections = elections_api.get_elections_by_ocd_ids(ocd_ids)
	available = google_civic_info_api.get_available_elections(ocd_ids)

	rsp = {
		'ok': True,
		'id': aclu_ids,
		'elections': elections,
		'google_civic_info': available,
		'calendar_url': calendar_url,
		'state': state,
		'congress': congress,
		'county': county,
		'state_leg': state_legs
	}

	include_geometry = flask.request.args.get('geometry', False)
	if include_geometry == '1':

		rsp['geometry'] = {}

		if state:
			ocd_id = state['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': state['name'],
				'type': 'state',
				'geometry': state['geometry']
			}
			del state['geometry']

		if congress and 'next_district' in congress:
			ocd_id = congress['next_district']['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': congress['next_district']['name'],
				'type': 'congress',
				'geometry': congress['next_district']['geometry']
			}
			del congress['next_district']['geometry']
			if congress and 'district' in congress and 'geometry' in congress['district']:
				del congress['district']['geometry']
		elif congress and 'district' in congress:
			ocd_id = congress['district']['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': congress['district']['name'],
				'type': 'congress',
				'geometry': congress['district']['geometry']
			}
			del congress['district']['geometry']

		if county:
			ocd_id = county['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': county['name'],
				'type': 'county',
				'geometry': county['geometry']
			}
			del county['geometry']

		for leg in state_legs:
			ocd_id = leg['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': leg['name'],
				'type': 'state_leg',
				'geometry': leg['geometry']
			}
			del leg['geometry']

	return flask.jsonify(rsp)

@api.route("/state")
def state():
	req = helpers.get_spatial_request()

	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = state_api.get_state_by_coords(lat, lng)
	if rsp == None:
		return flask.jsonify({
			'ok': False,
			'error': 'No state found.'
		})

	legislators = congress_api.get_legislators_by_state(rsp['state'])

	return flask.jsonify({
		'ok': True,
		'state': rsp,
		'congress': {
			'legislators': legislators
		}
	})

@api.route("/congress")
def congress():
	req = helpers.get_spatial_request()
	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = congress_api.get_congress_by_coords(lat, lng)
	return flask.jsonify({
		'ok': True,
		'congress': rsp
	})

@api.route("/congress/district")
def congress_district():
	req = helpers.get_spatial_request()

	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	district = congress_api.get_district_by_coords(lat, lng)

	return flask.jsonify({
		'ok': True,
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
		'ok': True,
		'congress_scores': scores
	})

@api.route("/congress/legislators")
def congress_legislators():

	id = flask.request.args.get('id', None)
	url_slug = flask.request.args.get('url_slug', None)

	if id:
		legislators = congress_api.get_legislators_by_id(id)
	elif url_slug:
		legislators = congress_api.get_legislators_by_url_slug(url_slug)
	else:
		legislators = congress_api.get_all_legislators()

	return flask.jsonify({
		'ok': True,
		'congress_legislators': legislators
	})

@api.route("/county")
def pip_county():
	req = helpers.get_spatial_request()

	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = county_api.get_county_by_coords(lat, lng)
	if rsp == None:
		return flask.jsonify({
			'ok': False,
			'error': 'No county found.'
		})

	return flask.jsonify({
		'ok': True,
		'county': rsp
	})

@api.route("/state_leg")
def pip_state_leg():
	req = helpers.get_spatial_request()

	if type(req) == str:
		return flask.jsonify({
			'ok': False,
			'error': req
		})

	lat = req['lat']
	lng = req['lng']

	rsp = state_leg_api.get_state_legs_by_coords(lat, lng)
	if len(rsp) == 0:
		return flask.jsonify({
			'ok': False,
			'error': 'No state legislation found.'
		})

	return flask.jsonify({
		'ok': True,
		'state_leg': rsp
	})

@api.route("/google_civic_info")
def google_civic_info():

	ocd_id = flask.request.args.get('ocd_id', None)
	address = flask.request.args.get('address', None)

	if not ocd_id or not address:
		elections = google_civic_info_api.get_elections()
		available = []
		for election in elections:
			if election['id'] != "2000": # test election
				available.append({
					'ocd_id': election['ocdDivisionId'],
					'name': election['name']
				})
		return flask.jsonify({
			'ok': True,
			'elections': available
		})

	election_id = google_civic_info_api.get_election_id(ocd_id)

	if not election_id:
		return flask.jsonify({
			'ok': False,
			'error': "Sorry, no election found for ocd_id '%s'." % ocd_id
		})

	rsp = google_civic_info_api.get_voter_info(election_id, address)

	if 'pollingLocations' in rsp:
		for location in rsp['pollingLocations']:
			if location['address']['line1'] == "":
				continue
			address = '%s, %s, %s %s' % (
				location['address']['line1'],
				location['address']['city'],
				location['address']['state'],
				location['address']['zip']
			)

			geocoded = mapbox_api.geocode(address)

			if 'features' in geocoded and len(geocoded['features']) > 0:
				location['geocoded'] = {
					'lat': geocoded['features'][0]['center'][1],
					'lng': geocoded['features'][0]['center'][0]
				}

	return flask.jsonify({
		'ok': True,
		'google_civic_info': rsp
	})

@api.route("/calendar")
def calendar():

	global elections

	state = flask.request.args.get('state', None)
	format = flask.request.args.get('format', 'json')

	if not state:
		return flask.jsonify({
			'ok': False,
			'error': "Please include a 'state' arg."
		})

	ocd_ids = ['ocd-division/country:us/state:%s' % state]
	rsp = elections.get_elections_by_ocd_ids(ocd_ids)

	if not 'calendar' in rsp:
		return flask.jsonify({
			'ok': False,
			'error': 'Calendar data not found.'
		})

	if format == 'ics':

		human_readable = {
			'registration_online_deadline': 'online registration deadline',
			'election_date': 'election day',
			'vbm_start': 'vote by mail starts',
			'vbm_end': 'vote by mail ends',
			'early_vote_start': 'early voting starts',
			'early_vote_end': 'early voting ends'
		}

		state_name = us.states.lookup(state).name

		c = Calendar()
		c.name = "%s Elections" % state_name

		for election in rsp['calendar']:
			for name, date in election['dates'].iteritems():
				e = Event()

				if name in human_readable:
					name = human_readable[name]

				type = election['type']
				if name == 'election day' or name == 'primary election day':
					name = name.upper()
				elif type == 'primary':
					name = "Primary election: %s" % name
				else:
					name = "Election: %s" % name

				name = name.replace('_', ' ')

				e.name = name
				e.begin = date
				e.make_all_day()
				c.events.add(e)

		rsp = flask.Response(c, mimetype='text/calendar')
		rsp.headers['Content-Disposition'] = 'inline; filename="Elections.ics"'
		return rsp
	else:
		return flask.jsonify({
			'ok': True,
			'calendar': rsp['calendar']
		})

@api.route("/geoip")
def geoip():

	ip = flask.request.args.get('ip', None)

	if not ip:
		return flask.jsonify({
			'ok': False,
			'error': "Please include an 'ip' arg."
		})

	script = os.path.realpath(sys.argv[0])
	server_dir = os.path.dirname(script)
	root_dir = os.path.dirname(server_dir)

	db_path = '%s/sources/maxmind/geolite2_city.mmdb' % root_dir
	reader = maxminddb.open_database(db_path)

	rsp = reader.get(ip)

	if not rsp or not 'location' in rsp:
		return flask.jsonify({
			'ok': False,
			'error': 'Could not locate that ip address.'
		})

	return flask.jsonify({
		'ok': True,
		'location': rsp['location']
	})
