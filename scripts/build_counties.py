#!/bin/env python

import json, os, sys, re, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/sources/counties/counties.geojson" % root_dir

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % path)
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state_geoid = props["STATEFP"]
	state = us.states.lookup(state_geoid).abbr
	state = str(state).lower()

	slug = re.sub(r"[^a-zA-Z]+", '-', props["NAME"]).lower()
	name = "county_%s_%s" % (state, slug)
	path = "%s/data/counties/%s/%s.geojson" % (root_dir, state, name)

	print("Saving %s" % path)
	feature["properties"] = {
		"geoid": props["GEOID"],
		"state": state,
		"name": props["NAME"],
		"area_land": props["ALAND"],
		"area_water": props["AWATER"]
	}
	feature["id"] = name

	mapzen.whosonfirst.utils.ensure_bbox(feature)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)

print("Done")
