#!/bin/env python

import os, sys, json, us, area
import data_index
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

def sort_states(a, b):
	if a['properties']['STUSPS'] > b['properties']['STUSPS']:
		return 1
	else:
		return -1

data["features"].sort(sort_states)

for feature in data["features"]:

	props = feature["properties"]
	state = props["STUSPS"].lower()
	name = props["NAME"]

	filename = "state_%s.geojson" % state
	path = "states/%s" % filename
	abs_path = "%s/data/%s" % (root_dir, path)
	ocd_id = 'ocd-division/country:us/state:%s' % state
	aclu_id = data_index.get_id('elections-api', 'state', path, name)

	print("Saving %s" % path)
	feature["properties"] = {
		"aclu_id": aclu_id,
		"geoid": props["STATEFP"],
		"ocd_id": ocd_id,
		"state": state,
		"name": name,
		"area_land": props["ALAND"],
		"area_water": props["AWATER"]
	}
	feature["id"] = aclu_id

	mapzen.whosonfirst.utils.ensure_bbox(feature)

	dirname = os.path.dirname(abs_path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(abs_path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)

print("Saving index")
data_index.save_index('elections-api')

print("Done")