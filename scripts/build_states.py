#!/bin/env python

import json, os, sys, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/sources/states/states.geojson" % root_dir

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % path)
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state = props["STUSPS"].lower()

	name = "state_%s.geojson" % state
	path = "%s/data/states/%s" % (root_dir, name)

	print("Saving %s" % path)
	feature["properties"] = {
		"state": state,
		"name": props["NAME"],
		"area_land": props["ALAND"],
		"area_water": props["AWATER"],
		"fips_id": props["STATEFP"]
	}
	feature["id"] = "state_%s" % name

	mapzen.whosonfirst.utils.ensure_bbox(feature)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)

print("Done")
