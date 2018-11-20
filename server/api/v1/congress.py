import flask, json, os, re, sys, arrow, us

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

def get_district_by_coords(lat, lng, session=None):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, start_session, end_session, state, district_num, area'

	if include_geometry == '1':
		columns += ', boundary_simple'

	if not session:
		filter = 'ORDER BY start_session DESC'
	else:
		filter = 'AND start_session >= %d AND end_session <= %d' % (session, session)

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM congress_districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
		{filter}
		LIMIT 1
	'''.format(columns=columns, lng=lng, lat=lat, filter=filter))

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
				'state_full': us.states.lookup(state).name,
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
				'state_full': us.states.lookup(state).name,
				'district_num': district_num,
				'area': area,
				'at_large': at_large,
				'non_voting': non_voting
			}

			if include_geometry == '1':
				district['geometry'] = row[9]

	cur.close()
	return district

def get_all_legislators(include=None):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE end_date >= CURRENT_DATE
		ORDER BY end_date DESC
	''')

	return get_legislators(cur, "total", include)

def get_legislators_by_state(state, session_num=115):

	sessions = get_sessions()
	session = sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE end_date >= CURRENT_DATE
		  AND state = %s
		ORDER BY end_date DESC
	''', (state,))

	return get_legislators(cur)

def get_legislators_by_district(state, district_num):

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

def get_legislators_by_url_slug(url_slug, include):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT t.id, t.aclu_id, t.start_date, t.end_date, t.type, t.state, t.district_num, t.party
		FROM congress_legislator_terms AS t,
		     congress_legislators AS l
		WHERE l.url_slug = %s
		  AND l.aclu_id = t.aclu_id
		  AND t.end_date >= CURRENT_DATE
		ORDER BY t.end_date DESC
	''', (url_slug,))

	return get_legislators(cur, "all", include)

def get_legislators_by_id(id, include):

	id = int(id)

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT t.id, t.aclu_id, t.start_date, t.end_date, t.type, t.state, t.district_num, t.party
		FROM congress_legislator_terms AS t,
		     congress_legislators AS l
		WHERE l.aclu_id LIKE '%congress_legislator:{id}'
		  AND l.aclu_id = t.aclu_id
		  AND t.end_date >= CURRENT_DATE
		ORDER BY t.end_date DESC
	'''.format(id=id))

	return get_legislators(cur, 'all', include)

def get_legislators(cur, score_filter="total", include=None):

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
					'state_full': us.states.lookup(row[5]).name,
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
		SELECT aclu_id, url_slug, first_name, last_name, full_name, nickname, birthday, gender
		FROM congress_legislators
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			legislators[aclu_id]['url_slug'] = row[1]
			legislators[aclu_id]['name'] = {
				'first_name': row[2],
				'last_name': row[3],
				'full_name': row[4],
				'nickname': row[5]
			}
			legislators[aclu_id]['name']['full_name'] = normalize_full_name(legislators[aclu_id]['name'])
			legislators[aclu_id]['bio'] = {
				'birthday': arrow.get(row[6]).format('YYYY-MM-DD'),
				'gender': row[7]
			}

	if include == "name":
		legislator_list = []
		for aclu_id in legislators:
			legislator_list.append({
				'name': legislators[aclu_id]['name']['full_name'],
				'url_slug': legislators[aclu_id]['url_slug']
			})
		cur.close()
		return legislator_list

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
					elif url_root == 'http://elections-stg.api.aclu.org/':
						url_root = 'https://elections-stg.api.aclu.org/'
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

		sql_filter = ''
		if score_filter == "total":
			sql_filter = "AND name = 'total'"

		cur.execute('''
			SELECT aclu_id, legislator_id, position, name, value
			FROM congress_legislator_scores
			WHERE legislator_id IN ({aclu_ids})
			{filter}
		'''.format(aclu_ids=aclu_id_list, filter=sql_filter), aclu_id_values)

		rs = cur.fetchall()
		if rs:
			for row in rs:
				aclu_id = row[0]
				legislator_id = row[1]
				position = row[2]
				name = row[3]
				value = row[4]

				if name == 'total':
					legislators[legislator_id]['total_score'] = value
				else:

					if not 'scores' in legislators[legislator_id]:
						legislators[legislator_id]['scores'] = []

					score = {
						'aclu_id': aclu_id,
						'aclu_position': position,
						'name': name,
						'status': 'unknown',
						'score': None,
						'vote': None
					}
					if value == '1' or value == '0':
						score['status'] = 'voted'
						score['score'] = True if value == '1' else False
						if position == 'supported' and value == '1':
							score['vote'] = True
						else:
							score['vote'] = False
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

	# HELLO quick warning here: these next two vars are hardcoded, and we are
	# going to need to make them ~less~ hardecoded.
	# (20180716/dphiffer)

	curr_session = 115
	redistricted = ['pa']

	curr_district = get_district_by_coords(lat, lng, curr_session)

	if curr_district and curr_district['state'] in redistricted:
		next_district = get_district_by_coords(lat, lng)
	else:
		next_district = curr_district

	if not curr_district:
		rsp = {
			'ok': False,
			'error': 'No congressional district found.'
		}
	else:
		legislators = get_legislators_by_district(curr_district["state"], curr_district["district_num"])
		rsp = {
			'ok': True,
			'district': curr_district,
			'next_district': next_district,
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

def normalize_full_name(name):
	if name["nickname"] and name["nickname"] not in name["full_name"]:
		nicknamed = "%s \"%s\"" % (name["first_name"], name["nickname"])
		normalized = name["full_name"].replace(name["first_name"], nicknamed)
		name["full_name"] = normalized
	return name["full_name"]
