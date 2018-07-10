import flask, json, os, re, sys, arrow

def get_sessions():

	sessions = {}

	cur = flask.g.db.cursor()

	cur.execute('''
		SELECT id, start_date, end_date
		FROM congress_sessions
		ORDER BY id DESC
	''')

	rs = cur.fetchall()
	results = []
	if rs:
		for row in rs:
			id = row[0]
			sessions[id] = {
				"start_date": str(row[1]),
				"end_date": str(row[2])
			}

	return sessions

def get_district_by_coords(lat, lng, session_num=115):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, start_session, end_session, state, district_num, area'

	if include_geometry == '1':
		columns += ', boundary_simple'

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM congress_districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
		  AND (district_num > 0 OR at_large_only = 'Y')
		  AND start_session <= %s
		  AND end_session >= %s
	'''.format(columns=columns, lng=lng, lat=lat), (session_num, session_num))

	rs = cur.fetchall()
	district = None

	sessions = get_sessions()

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
				'start_date': sessions[start_session]['start_date'],
				'end_date': sessions[end_session]['end_date'],
				'state': state,
				'district_num': district_num,
				'area': area,
				'at_large': at_large,
				'non_voting': non_voting
			}

			if include_geometry == '1':
				district['geometry'] = row[9]

	cur.close()
	return district

def get_district_by_id(aclu_id):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, start_session, end_session, state, district_num, area'

	if include_geometry == '1':
		columns += ', boundary_simple'

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM congress_districts
		WHERE aclu_id = %s
	'''.format(columns=columns), (aclu_id,))

	rs = cur.fetchall()
	district = None

	sessions = get_sessions()

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
				'start_date': sessions[start_session]['start_date'],
				'end_date': sessions[end_session]['end_date'],
				'state': state,
				'district_num': district_num,
				'area': area,
				'at_large': at_large,
				'non_voting': non_voting
			}

			if include_geometry == '1':
				district['geometry'] = row[9]

	cur.close()
	return district

def get_legislators_by_state(state, session_num=115):

	sessions = get_sessions()
	session = sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE end_date >= CURRENT_DATE
		  AND state = %s
		  AND type = 'sen'
		ORDER BY end_date DESC
	''', (state,))

	return get_legislators(cur)

def get_legislators_by_district(state, district_num, session_num=115):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE end_date >= CURRENT_DATE
		  AND state = %s
		  AND (
			district_num IS NULL OR
			district_num = %s
		  )
		ORDER BY end_date DESC
	''', (state, district_num))

	return get_legislators(cur)

def get_legislators(cur):

	legislators = {}
	aclu_ids = []
	term_ids = []

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[1]
			office = 'us_representative' if row[4] == 'rep' else 'us_senator'
			legislators[aclu_id] = {
				'term': {
					'start_date': arrow.get(row[2]).format('YYYY-MM-DD'),
					'end_date': arrow.get(row[3]).format('YYYY-MM-DD'),
					'office': office,
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

	aclu_id_list = ', '.join(['%s'] * len(aclu_ids))
	aclu_id_values = tuple(aclu_ids)

	cur.execute('''
		SELECT aclu_id, first_name, last_name, full_name, birthday, gender
		FROM congress_legislators
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

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
		SELECT aclu_id, display_name, running_in_2018
		FROM congress_legislator_details
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			legislators[aclu_id]['name']['display_name'] = row[1]
			legislators[aclu_id]['running_in_2018'] = True if row[2] else False

	term_id_list = ', '.join(['%s'] * len(term_ids))
	term_id_values = tuple(term_ids)
	cur.execute('''
		SELECT aclu_id, detail_name, detail_value
		FROM congress_legislator_term_details
		WHERE term_id IN ({term_ids})
	'''.format(term_ids=term_id_list), term_id_values)

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			key = row[1]
			value = row[2]
			if key == 'class':
				legislators[aclu_id]['term'][key] = int(value)
			elif key == 'state_rank':
				legislators[aclu_id]['term'][key] = value
			else:
				if not 'contact' in legislators[aclu_id]:
					legislators[aclu_id]['contact'] = {}
				legislators[aclu_id]['contact'][key] = value

	cur.execute('''
		SELECT aclu_id, concordance_name, concordance_value
		FROM congress_legislator_concordances
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

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
					elif url_root == 'http://elections.api.aclu.org/':
						url_root = 'https://elections.api.aclu.org/'
					legislators[aclu_id]['photo'] = "%s%s" % (url_root, path)

	cur.execute('''
		SELECT aclu_id, social_media_name, social_media_value
		FROM congress_legislator_social_media
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

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
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

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
					score['vote'] = True if value == '1' else False
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

	def sort_legislators(a, b):
		if a['term']['office'] == 'us_senator' and b['term']['office'] == 'us_senator':
			if a['term']['class'] > b['term']['class']:
				return -1
			elif a['term']['class'] < b['term']['class']:
				return 1
		elif a['term']['office'] == 'us_senator' and b['term']['office'] == 'us_representative':
			return -1
		elif a['term']['office'] == 'us_representative' and b['term']['office'] == 'us_senator':
			return 1

		if a['name']['last_name'] < b['name']['last_name']:
			return -1
		elif a['name']['last_name'] > b['name']['last_name']:
			return 1
		else:
			return 0

	legislator_list.sort(cmp=sort_legislators)

	return legislator_list

def get_congress_by_coords(lat, lng):

	district = get_district_by_coords(lat, lng)

	if not district:
		rsp = {
			'ok': False,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators_by_district(district["state"], district["district_num"])
		rsp = {
			'ok': True,
			'district': district,
			'legislators': legislators
		}

	return rsp

def get_congress_by_id(aclu_id):

	district = get_district_by_id(aclu_id)

	if not district:
		rsp = {
			'ok': False,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators_by_district(district["state"], district["district_num"])
		rsp = {
			'ok': True,
			'district': district,
			'legislators': legislators
		}

	return rsp
