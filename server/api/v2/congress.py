import flask, json, os, re, sys, arrow, us

curr_session = 116

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

	# This session filter used to be:
	#
	# if not session:
	#   filter = 'AND start_session >= %d AND end_session <= %d' % (session, session)
	#
	# This new version gives us the newest district that isn't *newer* than the
	# requested session. This may have adverse consequences for things like
	# recently redistricted districts. (20190311/dphiffer)

	if session:
		filter = 'AND start_session < %d' % session

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM congress_districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
		{filter}
		ORDER BY start_session DESC
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

def get_all_legislators(include=None, session_num=curr_session):

	sessions = get_sessions()

	cur = flask.g.db.cursor()
	if session_num == 'all':
		session_115 = sessions[115]
		session_116 = sessions[116]
		cur.execute('''
			SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
			FROM congress_legislator_terms
			WHERE start_date >= '{start_date_115}' AND end_date <= '{end_date_115}'
				OR start_date <= '{start_date_115}' AND end_date >= '{end_date_115}'
				OR start_date >= '{start_date_116}' AND end_date <= '{end_date_116}'
				OR start_date <= '{start_date_116}' AND end_date >= '{end_date_116}'
			ORDER BY end_date DESC
		'''.format(start_date_115=session_115['start_date'], end_date_115=session_115['end_date'], start_date_116=session_116['start_date'], end_date_116=session_116['end_date']))
	else:
		session = sessions[session_num]
		cur.execute('''
			SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
			FROM congress_legislator_terms
			WHERE start_date >= '{start_date}' AND end_date <= '{end_date}'
					OR start_date <= '{start_date}' AND end_date >= '{end_date}'
			ORDER BY end_date DESC
		'''.format(start_date=session['start_date'], end_date=session['end_date']))

	return get_legislators(cur, "total", include, session_num)

def get_legislators_by_state(state, session_num=curr_session):

	sessions = get_sessions()
	session = sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE (
			start_date >= '{start_date}' AND end_date <= '{end_date}'
			OR start_date <= '{start_date}' AND end_date >= '{end_date}'
		)
		AND state = %s
		ORDER BY end_date DESC
	'''.format(start_date=session['start_date'], end_date=session['end_date']), (state,))

	return get_legislators(cur, "total", None, session_num)

def get_legislators_by_district(state, district_num, session_num=curr_session):

	sessions = get_sessions()
	session = sessions[session_num]

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, aclu_id, start_date, end_date, type, state, district_num, party
		FROM congress_legislator_terms
		WHERE (
			start_date >= '{start_date}' AND end_date <= '{end_date}'
			OR start_date <= '{start_date}' AND end_date >= '{end_date}'
		)
		AND state = %s
		AND (
			district_num IS NULL OR
			district_num = %s
		)
		ORDER BY end_date DESC
	'''.format(start_date=session['start_date'], end_date=session['end_date']), (state, district_num))

	return get_legislators(cur, "total", None, session_num)

def get_legislators_by_url_slug(url_slug, include, session_num=curr_session):

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT t.id, t.aclu_id, t.start_date, t.end_date, t.type, t.state, t.district_num, t.party
		FROM congress_legislator_terms AS t,
		     congress_legislators AS l
		WHERE l.url_slug = %s
		  AND l.aclu_id = t.aclu_id
		ORDER BY t.end_date DESC
		LIMIT 1
	''', (url_slug,))

	return get_legislators(cur, "all", include, session_num)

def get_legislators_by_id(id, include, session_num=curr_session):

	id = int(id)

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT t.id, t.aclu_id, t.start_date, t.end_date, t.type, t.state, t.district_num, t.party
		FROM congress_legislator_terms AS t,
		     congress_legislators AS l
		WHERE l.aclu_id LIKE '%congress_legislator:{id}'
		  AND l.aclu_id = t.aclu_id
		ORDER BY t.end_date DESC
		LIMIT 1
	'''.format(id=id))

	return get_legislators(cur, 'all', include, session_num)

def set_legislator_session_value(legislator, session_num, name, value):

	bool_types = [
		"running_in_2018",
		"running_for_president"
	]

	if name == "aclu_id":
		return

	if not 'sessions' in legislator:
		legislator['sessions'] = []

	session = None

	for s in legislator['sessions']:
		if s['session'] == session_num:
			session = s

	if not session:
		session = {
			'session': session_num
		}
		legislator['sessions'].append(session)

	if name in bool_types:
		# 0 = False
		# 1 = True
		if value == "0" or value == "1":
			value = int(value)
		value = bool(value)

	session[name] = value

def get_legislators(cur, score_filter="total", include=None, session_num=curr_session):

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
			if not aclu_id in aclu_ids:
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

	values = list(aclu_id_values)
	values = tuple(values)

	cur.execute('''
		SELECT aclu_id, session, detail_name, detail_value
		FROM congress_legislator_details
		WHERE aclu_id IN ({aclu_ids})
	'''.format(aclu_ids=aclu_id_list), values)

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]
			legislator = legislators[aclu_id]
			set_legislator_session_value(legislator, row[1], row[2], row[3])

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

	if score_filter == 'all':

		vote_dates = {}
		cur.execute('''
			SELECT aclu_id, vote_date
			FROM congress_legislator_score_index
		''')
		rs = cur.fetchall()
		if rs:
			for row in rs:
				vote_id = row[0]
				vote_dates[vote_id] = arrow.get(row[1]).format('YYYY-MM-DD')

		cur.execute('''
			SELECT aclu_id, session, legislator_id, position, name, value
			FROM congress_legislator_scores
			WHERE legislator_id IN ({aclu_ids})
		'''.format(aclu_ids=aclu_id_list), aclu_id_values)

		rs = cur.fetchall()
		if rs:
			for row in rs:
				aclu_id = row[0]
				session = row[1]
				legislator_id = row[2]
				position = row[3]
				name = row[4]
				value = row[5]

				score = {
					'aclu_id': aclu_id,
					'aclu_position': position,
					'name': name,
					'status': 'unknown',
					'vote_matches_aclu_position': None,
					'vote': None
				}

				normalized_value = value.lower()
				if normalized_value == "nay":
					value = '0'

				if value == '1' or value == '0':
					score['status'] = 'Voted'
					score['vote_matches_aclu_position'] = True if value == '1' else False

					# Hey this part is confusing! score['vote_matches_aclu_position'] is what
					# we get out of the spreadsheet (1 or 0) which is optimized
					# for calculating the total percentage.
					#
					# if vote_matches_aclu_position is 1 and aclu supported, then vote is 1
					# if vote_matches_aclu_position is 1 and aclu opposed then vote is 0
					# if vote_matches_aclu_position is 0 and aclu supported then vote is 0
					# if vote_matches_aclu_position is 0 and aclu opposed then vote is 1
					#
					# (20190110/dphiffer) with help from kateray

					if score['vote_matches_aclu_position']:
						score['vote'] = True if score['aclu_position'] == 'supported' else False
					else:
						score['vote'] = False if score['aclu_position'] == 'supported' else True

				else:

					# Okay this part is a little tweaky. We are normalizing the
					# values we get from the scorecard, which have more detailed
					# descriptions than we actually want to passs along to
					# website visitors. So we are grouping the reasons for a
					# non-vote into 3 broad categories. (dphiffer/20190314)

					did_not_vote_values = [
						"did not vote",
						"not voting",
						"missed",
						"present"
					]

					not_on_committee_values = [
						"not on committee",
						"not yet on committee"
					]

					not_in_office_values = [
						"not in office",
						"not yet in office"
					]

					if normalized_value in did_not_vote_values:
						value = "Did not vote"
					elif normalized_value in not_on_committee_values:
						value = "Not on committee"
					elif normalized_value in not_in_office_values:
						value = "Not in office"

					score['status'] = value

				for s in legislators[legislator_id]['sessions']:
					if s['session'] == session:
						if not 'scores' in s:
							s['scores'] = []
						id = score['aclu_id']
						score['vote_date'] = vote_dates[id]

						# This conditional exists to ensure we don't include
						# votes that occur after someone's term ends (e.g., they
						# pass away). (20191028/dphiffer)
						if score['vote_date'] <= legislators[legislator_id]['term']['end_date']:
							s['scores'].append(score)

	cur.execute('''
		SELECT legislator_id, session
		FROM congress_legislator_scores
		WHERE legislator_id IN ({aclu_ids})
		GROUP BY legislator_id, session
		ORDER BY session
	'''.format(aclu_ids=aclu_id_list), aclu_id_values)

	rs = cur.fetchall()
	if rs:
		for row in rs:
			legislator_id = row[0]
			session = row[1]
			if not "score_sessions" in legislators[legislator_id]:
				legislators[legislator_id]["score_sessions"] = []
			legislators[legislator_id]["score_sessions"].append(session)

	cur.close()

	legislator_list = []
	for aclu_id in legislators:
		if not "score_sessions" in legislators[aclu_id]:
			legislators[aclu_id]["score_sessions"] = []
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

def get_congress_by_coords(lat, lng, session):

	# HELLO quick warning here: these next two vars are hardcoded, and we are
	# going to need to make them ~less~ hardecoded.
	# (20180716/dphiffer)

	# UPDATE we are now using a global var curr_session, which is still hard-
	# coded. It's just not hardcoded in here. (20190108/dphiffer)

	redistricted = ['pa']

	curr_district = get_district_by_coords(lat, lng, session)

	if curr_district and curr_district['state'] in redistricted:
		next_district = get_district_by_coords(lat, lng, session + 1)
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
