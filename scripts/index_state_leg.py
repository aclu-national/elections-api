#!/bin/env python

import os, sys, psycopg2, re, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS state_leg CASCADE")
cur.execute('''
	CREATE TABLE state_leg (
		aclu_id VARCHAR(255) PRIMARY KEY,
		geoid VARCHAR(255),
		ocd_id VARCHAR(255),
		name VARCHAR(255),
		state CHAR(2),
		chamber VARCHAR(10),
		district_num VARCHAR(10),
		area_land BIGINT,
		area_water BIGINT,
		boundary TEXT,
		boundary_simple TEXT,
		boundary_geom GEOMETRY
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO state_leg (
		aclu_id,
		geoid,
		ocd_id,
		name,
		state,
		chamber,
		district_num,
		area_land,
		area_water,
		boundary,
		boundary_simple
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

cur = conn.cursor()
state_leg_dir = "%s/data/state_leg" % root_dir

state_dirs = []
for state in os.listdir(state_leg_dir):
	state_dirs.append(state)

files = []
for state_dir in state_dirs:
	for filename in os.listdir("%s/%s" % (state_leg_dir, state_dir)):
		if not filename.endswith(".geojson"):
			continue
		elif filename.endswith(".display.geojson"):
			continue
		files.append("%s/%s/%s" % (state_leg_dir, state_dir, filename))

files.sort()
for filename in files:

	print(filename)

	with open(filename) as geojson:
		feature = json.load(geojson)

	display_path = filename.replace('.geojson', '.display.geojson')
	with open(display_path) as display_geojson:
		display_feature = json.load(display_geojson)

	aclu_id = feature["properties"]["aclu_id"]
	geoid = feature["properties"]["geoid"]
	ocd_id = feature["properties"]["ocd_id"]
	name = feature["properties"]["name"]
	state = feature["properties"]["state"]
	chamber = feature["properties"]["chamber"]
	district_num = feature["properties"]["district_num"]
	area_land = int(feature["properties"]["area_land"])
	area_water = int(feature["properties"]["area_water"])
	boundary = json.dumps(feature["geometry"])
	boundary_simple = json.dumps(display_feature["geometry"])

	state_leg = [
		aclu_id,
		geoid,
		ocd_id,
		name,
		state,
		chamber,
		district_num,
		area_land,
		area_water,
		boundary,
		boundary_simple
	]
	state_leg = tuple(state_leg)
	cur.execute(insert_sql, state_leg)
	conn.commit()

print("Indexing postgis geometry")
cur.execute('''
	UPDATE state_leg
	SET boundary_geom = ST_SetSRID(ST_GeomFromGeoJSON(boundary), 4326)
''')
cur.execute('''
	CREATE INDEX state_leg_boundary_gix ON state_leg USING GIST (boundary_geom)
''')
conn.commit()

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur.execute('''
	VACUUM ANALYZE state_leg
''')

conn.close()
print("Done")
