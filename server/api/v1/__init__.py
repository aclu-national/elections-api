__import__('pkg_resources').declare_namespace(__name__)

import flask, json, os, re, sys, arrow, us

sys.path.insert(1, os.path.dirname(__file__))

import helpers
import congress as congress_api
import state as state_api
import county as county_api
import state_leg as state_leg_api
import elections as elections_api
import google_civic_info as google_civic_info_api
import mapbox as mapbox_api
import geoip as geoip_api
import apple_wallet as apple_wallet_api
from copy import deepcopy
from ics import Calendar, Event

api = flask.Blueprint('api_v1', __name__)

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
					'state': 'Instead of lat/lng or id, specify a state (e.g., state=ny)',
					'geometry': 'Include GeoJSON geometries with districts (optional; geometry=1)',
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
					'url_slug': 'State and name URL slug (optional; returns a single match).',
					'include': 'Fields to include (optional; include=name)'
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
					'ip': 'The IPv4 address to look up (optional; e.g., 38.109.115.130)',
					'pip': 'Use the resulting location to do a point-in-polygon lookup. (optional; set to 1 to include state-level pip results)',
					'legislators': 'Use the resulting location to do a point-in-polygon congress_legislators lookup. (optional; set to 1 to include)'
				}
			},
			'/v1/apple_wallet': {
				'description': 'Get an Apple Wallet pkpass based on polling place info.',
				'args': {
					'address': 'The polling place address',
					'hours': 'The polling place hours',
					'lat': 'Latitude',
					'lng': 'Longitude'
				}
			}
		}
	})

@api.route("/pip")
def pip(req=None):

	if not req:
		req = helpers.get_spatial_request()

	areas = []
	calendar_url = None
	state_only_congress = None

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

	if 'include' in req:
		if not 'congress' in req['include']:
			if 'state' in req['include']:
				state_only_congress = deepcopy(congress)
			congress = None
		if not 'state' in req['include']:
			state = None
		if not 'county' in req['include']:
			county = None
		if not 'state_leg' in req['include']:
			state_legs = []

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

	if state_only_congress:
		congress = state_only_congress
		congress['legislators'] = congress_api.get_legislators_by_state(state['state'])
		congress['district'] = None
		congress['next_district'] = None

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

		if congress and 'next_district' in congress and congress['next_district']:
			ocd_id = congress['next_district']['ocd_id']
			rsp['geometry'][ocd_id] = {
				'name': congress['next_district']['name'],
				'type': 'congress',
				'geometry': congress['next_district']['geometry']
			}
			del congress['next_district']['geometry']
			if congress and 'district' in congress and 'geometry' in congress['district']:
				del congress['district']['geometry']
		elif congress and 'district' in congress and congress['district']:
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
		       amendment, title, bill_summary, description, committee, link
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
				'bill': row[5],
				'bill_status': row[4], # stored in the db as vote_type
				'amendment': row[6],
				'title': row[7],
				'summary': row[8],
				'description': row[9],
				'committee': row[10],
				'link': row[11]
			})

	return flask.jsonify({
		'ok': True,
		'congress_scores': scores
	})

@api.route("/congress/legislators")
def congress_legislators():

	id = flask.request.args.get('id', None)
	url_slug = flask.request.args.get('url_slug', None)
	include = flask.request.args.get('include', None)

	if id:
		legislators = congress_api.get_legislators_by_id(id, include)
	elif url_slug:
		legislators = congress_api.get_legislators_by_url_slug(url_slug, include)
	else:
		legislators = congress_api.get_all_legislators(include)

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

	rsp = google_civic_info_api.get_polling_places(ocd_id, address)
	if not rsp:
		return flask.jsonify({
			'ok': False,
			'error': 'Could not get polling places.'
		})

	rsp_json = json.dumps({
		'ok': True,
		'google_civic_info': rsp
	}, sort_keys=True)

	rsp = flask.make_response(rsp_json)
	rsp.headers['Content-Type'] = 'application/json'
	rsp.headers['Cache-Control'] = 'no-cache'
	return rsp

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
			for name, date in election['dates'].items():
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

	ip = flask.request.args.get('ip', helpers.get_remote_ip())
	rsp = geoip_api.get_coords(ip)

	if not rsp or not 'ok' in rsp:
		rsp_json = json.dumps({
			'ok': False,
			'ip': ip,
			'error': 'Could not locate that ip address.'
		})
	elif not rsp['ok']:
		rsp_json = json.dumps(rsp)
	else:

		pip_filter = flask.request.args.get('pip', None)
		legislator_filter = flask.request.args.get('legislators', None)

		if pip_filter == '1' or legislator_filter == '1':
			try:
				pip_rsp = pip({
					'lat': rsp['location']['latitude'],
					'lng': rsp['location']['longitude'],
					'include': ['state']
				})
				if pip_filter == '1':
					rsp['pip'] = json.loads(pip_rsp.data)
				if legislator_filter == '1':
					pip_data = json.loads(pip_rsp.data)
					rsp['congress_legislators'] = pip_data['congress']['legislators']
			except:
				print("error doing pip on geoip")

		rsp_json = json.dumps(rsp)

	rsp = flask.make_response(rsp_json)
	rsp.headers['Content-Type'] = 'application/json'
	rsp.headers['Cache-Control'] = 'no-cache'
	return rsp

@api.route("/apple_wallet")
def apple_wallet():

	if not os.getenv('ENABLE_FEATURE_APPLE_WALLET', False):
		return flask.jsonify({
			'ok': False,
			'error': 'This feature is disabled.'
		})

	address = flask.request.args.get('address', None)
	hours = flask.request.args.get('hours', None)
	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if not address or not hours or not lat or not lng:
		return flask.jsonify({
			'ok': False,
			'error': "Please include 'address', 'hours', 'lat', 'lng' args."
		})

	path = apple_wallet_api.get_pass(address, hours, lat, lng)
	file = open(path, 'r')

	rsp = flask.Response(file, mimetype='application/vnd.apple.pkpass')
	rsp.headers['Content-Disposition'] = 'inline; filename="aclu_voter.pkpass"'
	return rsp
