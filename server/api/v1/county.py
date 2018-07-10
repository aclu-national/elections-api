import flask, json, os, re, sys, arrow

def get_county_by_coords(lat, lng):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, state, area_land, area_water'

	if include_geometry == '1':
		columns += ', boundary_simple'

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM counties
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
	'''.format(columns=columns, lng=lng, lat=lat))

	rs = cur.fetchall()
	county = None

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

			if include_geometry == '1':
				county['geometry'] = row[7]

	cur.close()
	return county

def get_county_by_id(aclu_id):

	include_geometry = flask.request.args.get('geometry', False)

	columns = 'aclu_id, geoid, ocd_id, name, state, area_land, area_water'

	if include_geometry == '1':
		columns += ', boundary_simple'

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT {columns}
		FROM counties
		WHERE aclu_id = %s
	'''.format(columns=columns), (aclu_id,))

	rs = cur.fetchall()
	county = None

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

			if include_geometry == '1':
				county['geometry'] = row[7]

	cur.close()
	return county
