#!/bin/env python

import json, os, sys, us, area, optparse
import postgres_db
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

opt_parser = optparse.OptionParser()
opt_parser.add_option('-s', '--start', dest='start', type='int', action='store', default=None, help='Start session (e.g. 113)')
opt_parser.add_option('-e', '--end', dest='end', type='int', default=None, action='store', help='End session (e.g. 115)')
options, args = opt_parser.parse_args()

session = options.start
district_prop = "CD%sFP" % session
path = "%s/sources/districts_%s/districts_%s.geojson" % (root_dir, session, session)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("SELECT id, start_date, end_date FROM sessions")
rs = cur.fetchall()
sessions = {}
if rs:
	for row in rs:
		id = row[0]
		sessions[id] = {
			"start_date": str(row[1]),
			"end_date": str(row[2])
		}

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % path)
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state_fips = props["STATEFP"]
	state = us.states.lookup(state_fips).abbr
	state = str(state).lower()

	if props[district_prop] == "ZZ":
		continue

	district = int(props[district_prop])

	id = "district_%s_%s_%s" % (session, state, district)
	name = "%s.geojson" % id
	path = "%s/data/districts_%s/%s/%s" % (root_dir, session, state, name)

	print("Saving %s" % path)

	feature["properties"] = {
		"state": state,
		"start_session": options.start,
		"start_date": sessions[options.start]["start_date"],
		"end_session": options.end,
		"end_date": sessions[options.end]["end_date"],
		"district_num": district
	}
	feature["id"] = id

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)

print("Done")