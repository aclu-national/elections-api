import flask, json, os, re, sys, arrow
from copy import deepcopy

def get_ocd_ids(areas):
	ocd_ids = []
	for area in areas:
		if area == None:
			continue
		if 'ocd_id' in area:
			ocd_ids.append(area['ocd_id'])
	return ocd_ids

def get_aclu_ids(areas):
	aclu_ids = []
	for area in areas:
		if area == None:
			continue
		if 'aclu_id' in area:
			id = re.search('\d+$', area['aclu_id']).group(0)
			aclu_ids.append(id)
	return '-'.join(aclu_ids)

def get_targeted():

	targeted = {
		'races': {},
		'initiatives': {}
	}

	cur = flask.g.db.cursor()

	cur.execute('''
		SELECT ocd_id, office, summary, url, link_text, disclaimer
		FROM election_targeted_races
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			ocd_id = row[0]

			if not ocd_id in targeted['races']:
				targeted['races'][ocd_id] = []

			targeted['races'][ocd_id].append({
				'office': row[1],
				'summary': row[2],
				'url': row[3],
				'link_text': row[4],
				'disclaimer': row[5]
			})

	cur.execute('''
		SELECT ocd_id, name, position, blurb, url, link_text, disclaimer
		FROM election_targeted_initiatives
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			ocd_id = row[0]

			if not ocd_id in targeted['initiatives']:
				targeted['initiatives'][ocd_id] = []

			targeted['initiatives'][ocd_id].append({
				'name': row[1],
				'position': row[2],
				'blurb': row[3],
				'url': row[4],
				'link_text': row[5],
				'disclaimer': row[6]
			})

	return targeted

def get_blurbs():

	blurbs = {}

	cur = flask.g.db.cursor()

	cur.execute('''
		SELECT office, name, title, summary, details_title
		FROM election_blurbs
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			blurbs[office] = {
				'name': row[1],
				'title': row[2],
				'summary': row[3],
				'details_title': row[4],
				'details': []
			}

	cur.execute('''
		SELECT office, detail
		FROM election_blurb_details
		ORDER BY office, detail_number
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			blurbs[office]['details'].append(row[1])

	cur.execute('''
		SELECT office, search, replace
		FROM election_blurb_alt_names
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			search = row[1]
			replace = row[2]
			if not 'alt_names' in blurbs[office]:
				blurbs[office]['alt_names'] = {}
			blurbs[office]['alt_names'][search] = replace

	return blurbs

def format_date(date):
	if date == None:
		return None
	else:
		return arrow.get(date).format('YYYY-MM-DD')

def localize_blurb(office_blurb, race_name):
	for search in office_blurb['alt_names']:
		if re.search(search, race_name):
			blurb = deepcopy(office_blurb)
			replace = office_blurb['alt_names'][search]
			blurb['name'] = blurb['name'].replace(replace, search)
			blurb['title'] = blurb['title'].replace(replace, search)
			blurb['summary'] = blurb['summary'].replace(replace, search)
			blurb['details_title'] = blurb['details_title'].replace(replace, search)
			return blurb
	return office_blurb

def get_spatial_request():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)
	id = flask.request.args.get('id', None)

	if (lat == None or lng == None) and id == None:
		return "Please include either 'lat' and 'lng' args or an 'id' arg."

	if lat != None and lng != None:

		if not re.search('^-?\d+(\.\d+)?', lat):
			return "Please include a numeric 'lat'."

		if not re.search('^-?\d+(\.\d+)?', lng):
			return "Please include a numeric 'lng'."

		return {
			'lat': lat,
			'lng': lng
		}

	elif re.search('^(\d+)(-\d+)*$', id):

		id_list = map(int, id.split('-'))

		placeholders = ', '.join(['%s'] * len(id_list))
		values = tuple(id_list)

		cur = flask.g.db.cursor()
		cur.execute('''
			SELECT aclu_id, type
			FROM aclu_ids
			WHERE id IN ({id_list})
		'''.format(id_list=placeholders), values)

		rsp = {}
		rs = cur.fetchall()
		if rs:
			for row in rs:
				type = row[1]
				aclu_id = row[0]
				if type == 'state_leg':
					if not 'state_leg' in rsp:
						rsp['state_leg'] = []
					rsp['state_leg'].append(aclu_id)
				elif type == 'congress_district':
					if not 'congress_district' in rsp:
						rsp['congress_district'] = aclu_id
					else:
						rsp['next_congress_district'] = aclu_id
				else:
					rsp[type] = aclu_id

		return rsp

	else:
		return 'Could not understand spatial request.'
