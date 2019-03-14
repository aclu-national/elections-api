import flask, json, os, re, sys, arrow

def get_state_legs_by_coords(lat, lng):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, state, chamber, district_num, area_land, area_water'

	if include_geometry == '1':
		columns += ', boundary_simple'

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM state_leg
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(columns=columns, lng=lng, lat=lat))

	rs = cur.fetchall()
	state_legs = []

	if rs:
		for row in rs:

			state_leg = {
				'aclu_id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'chamber': row[5],
				'district_num': row[6],
				'area_land': row[7],
				'area_water': row[8]
			}

			if include_geometry == '1':
				state_leg['geometry'] = row[9]

			state_legs.append(state_leg)

	cur.close()
	return state_legs

def get_state_legs_by_ids(aclu_ids):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, state, chamber, district_num, area_land, area_water'

	if include_geometry == '1':
		columns += ', boundary_simple'

	aclu_id_list = ', '.join(['%s'] * len(aclu_ids))
	aclu_id_values = tuple(aclu_ids)

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM state_leg
		WHERE aclu_id IN ({aclu_ids})
	'''.format(columns=columns, aclu_ids=aclu_id_list), aclu_id_values)

	rs = cur.fetchall()
	state_legs = []

	if rs:
		for row in rs:

			state_leg = {
				'aclu_id': row[0],
				'geoid': row[1],
				'ocd_id': row[2],
				'name': row[3],
				'state': row[4],
				'chamber': row[5],
				'district_num': row[6],
				'area_land': row[7],
				'area_water': row[8]
			}

			if include_geometry == '1':
				state_leg['geometry'] = row[9]

			state_legs.append(state_leg)

	cur.close()
	return state_legs
