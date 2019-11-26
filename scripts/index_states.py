#!/bin/env python

import os, sys, psycopg2, re, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS states CASCADE")
cur.execute('''
	CREATE TABLE states (
		aclu_id VARCHAR(255) PRIMARY KEY,
		geoid VARCHAR(255),
		ocd_id VARCHAR(255),
		name VARCHAR(255),
		state CHAR(2),
		area_land BIGINT,
		area_water BIGINT,
		boundary TEXT,
		boundary_simple TEXT,
		boundary_geom GEOMETRY
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO states (
		aclu_id,
		geoid,
		ocd_id,
		name,
		state,
		area_land,
		area_water,
		boundary,
		boundary_simple
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

cur = conn.cursor()
states_dir = "%s/data/states" % root_dir

files = []
for filename in os.listdir(states_dir):
	if not filename.endswith(".geojson"):
		continue
	elif filename.endswith(".display.geojson"):
		continue
	files.append(filename)

files.sort()
for filename in files:

	regex = '^state_([a-z][a-z])\.geojson$'
	matches = re.search(regex, filename)
	if matches == None:
		print("skipping %s" % filename)
		continue

	print(filename)

	path = "%s/%s" % (states_dir, filename)
	with open(path, 'r', encoding='utf-8') as geojson:
		feature = json.load(geojson)

	display_path = path.replace('.geojson', '.display.geojson')
	with open(display_path, 'r', encoding='utf-8') as display_geojson:
		display_feature = json.load(display_geojson)

	aclu_id = feature["properties"]["aclu_id"]
	geoid = feature["properties"]["geoid"]
	ocd_id = feature["properties"]["ocd_id"]
	name = feature["properties"]["name"]

	if name == 'District of Columbia':
		name = 'Washington, D.C.'

	state = feature["properties"]["state"]
	area_land = int(feature["properties"]["area_land"])
	area_water = int(feature["properties"]["area_water"])
	boundary = json.dumps(feature["geometry"])
	boundary_simple = json.dumps(display_feature["geometry"])

	state = [
		aclu_id,
		geoid,
		ocd_id,
		name,
		state,
		area_land,
		area_water,
		boundary,
		boundary_simple
	]
	state = tuple(state)
	cur.execute(insert_sql, state)
	conn.commit()

print("Indexing postgis geometry")
cur.execute('''
	UPDATE states
	SET boundary_geom = ST_SetSRID(ST_GeomFromGeoJSON(boundary), 4326)
''')
cur.execute('''
	CREATE INDEX states_boundary_gix ON states USING GIST (boundary_geom)
''')
conn.commit()

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur.execute('''
	VACUUM ANALYZE states
''')

conn.close()
print("Done")
