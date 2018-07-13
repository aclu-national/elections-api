#!/bin/env python

import os, sys, psycopg2, re, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS districts CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_districts CASCADE")
cur.execute('''
	CREATE TABLE congress_districts (
		aclu_id VARCHAR(255) PRIMARY KEY,
		geoid VARCHAR(255),
		ocd_id VARCHAR(255),
		name VARCHAR(255),
		state CHAR(2),
		start_session INTEGER,
		end_session INTEGER,
		district_num INTEGER,
		at_large_only CHAR DEFAULT 'N',
		boundary TEXT,
		boundary_simple TEXT,
		boundary_geom GEOMETRY,
		area FLOAT
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO congress_districts (
		aclu_id,
		geoid,
		ocd_id,
		name,
		state,
		start_session,
		end_session,
		district_num,
		boundary,
		boundary_simple,
		area
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

directories = []

for state in os.listdir("%s/data/congress_districts_113" % root_dir):
	if state.startswith("."):
		continue
	directories.append("%s/data/congress_districts_113/%s" % (root_dir, state))

for state in os.listdir("%s/data/congress_districts_115" % root_dir):
	if state.startswith("."):
		continue
	directories.append("%s/data/congress_districts_115/%s" % (root_dir, state))

directories.append("%s/data/congress_districts_116_pa" % root_dir)
directories.sort()

for dir in directories:

	cur = conn.cursor()

	files = []
	for filename in os.listdir(dir):
		if not filename.endswith(".geojson"):
			continue
		files.append(filename)

	files.sort()
	for filename in files:

		if filename.endswith('.display.geojson'):
			continue

		regex = '^congress_district_(\d+)_([a-z][a-z])_(\d+)\.geojson$'
		matches = re.search(regex, filename)
		if matches == None:
			print("skipping %s" % filename)
			continue

		print(filename)

		path = "%s/%s" % (dir, filename)
		with open(path) as geojson:
			feature = json.load(geojson)

		display_path = path.replace('.geojson', '.display.geojson')
		with open(display_path) as display_geojson:
			display_feature = json.load(display_geojson)

		aclu_id = feature["properties"]["aclu_id"]
		geoid = feature["properties"]["geoid"]
		ocd_id = feature["properties"]["ocd_id"]
		name = feature["properties"]["name"]
		state = feature["properties"]["state"]
		start_session = int(feature["properties"]["start_session"])
		end_session = int(feature["properties"]["end_session"])
		district_num = int(feature["properties"]["district_num"])
		boundary = json.dumps(feature["geometry"])
		boundary_simple = json.dumps(display_feature["geometry"])
		area = float(feature["properties"]["area"])

		district = [
			aclu_id,
			geoid,
			ocd_id,
			name,
			state,
			start_session,
			end_session,
			district_num,
			boundary,
			boundary_simple,
			area
		]
		cur.execute(insert_sql, district)

	conn.commit()

print("Marking excess at-large districts")
cur.execute('''
	UPDATE congress_districts
	SET at_large_only = 'Y'
	WHERE district_num = 0 AND (
		SELECT count(aclu_id)
		FROM congress_districts AS d
		WHERE d.start_session <= congress_districts.end_session
		  AND d.end_session >= congress_districts.start_session
		  AND d.state = congress_districts.state
	) = 1
''')

print("Indexing postgis geometry")
cur.execute('''
	UPDATE congress_districts
	SET boundary_geom = ST_SetSRID(ST_GeomFromGeoJSON(boundary), 4326)
''')
cur.execute('''
	CREATE INDEX districts_boundary_gix ON congress_districts USING GIST (boundary_geom)
''')
conn.commit()

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur.execute('''
	VACUUM ANALYZE congress_districts
''')

conn.close()
print("Done")
