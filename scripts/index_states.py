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
		id SERIAL PRIMARY KEY,
		geoid VARCHAR(255),
		name VARCHAR(255),
		state CHAR(2),
		area_land BIGINT,
		area_water BIGINT,
		boundary TEXT,
		boundary_geom GEOMETRY
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO states (
		geoid,
		name,
		state,
		area_land,
		area_water,
		boundary
	) VALUES (%s, %s, %s, %s, %s, %s)
'''

cur = conn.cursor()
states_dir = "%s/data/states" % root_dir

files = []
for filename in os.listdir(states_dir):
	if not filename.endswith(".geojson"):
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
	with open(path) as geojson:
		feature = json.load(geojson)

	geoid = feature["properties"]["geoid"]
	name = feature["properties"]["name"]
	state = feature["properties"]["state"]
	area_land = int(feature["properties"]["area_land"])
	area_water = int(feature["properties"]["area_water"])
	geometry = feature["geometry"]
	boundary = json.dumps(geometry)

	state = [
		geoid,
		name,
		state,
		area_land,
		area_water,
		boundary
	]
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
