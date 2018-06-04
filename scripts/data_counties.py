#!/bin/env python

import json, os, sys, re, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import data_index

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/sources/counties/counties.geojson" % root_dir

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % path)
with open(path) as data_file:
	data = json.load(data_file)

def get_filename(props):
	slug = re.sub(r"[^a-zA-Z]+", '-', props["NAME"]).lower()
	state_geoid = props["STATEFP"]
	state = us.states.lookup(state_geoid).abbr
	state = str(state).lower()
	filename = "county_%s_%s.geojson" % (state, slug)
	return filename

def sort_counties(a, b):
	a_filename = get_filename(a['properties'])
	b_filename = get_filename(b['properties'])
	if (a_filename > b_filename):
		return 1
	else:
		return -1

data["features"].sort(sort_counties)

for feature in data["features"]:

	props = feature["properties"]

	state_geoid = props["STATEFP"]
	state = us.states.lookup(state_geoid).abbr
	state = str(state).lower()
	slug = re.sub(r"[^a-zA-Z]+", '-', props["NAME"]).lower()
	ocd_slug = re.sub(r"[^a-zA-Z]+", '_', props["NAME"]).lower()

	filename = get_filename(props)
	path = "counties/%s/%s" % (state, filename)
	abs_path = "%s/data/%s" % (root_dir, path)

	aclu_id = data_index.get_id('elections-api', 'county', path, props["NAME"])
	ocd_id = 'ocd-division/country:us/state:%s/county:%s' % (state, ocd_slug)

	print("Saving %s" % path)
	feature["properties"] = {
		"aclu_id": aclu_id,
		"geoid": props["GEOID"],
		"ocd_id": ocd_id,
		"state": state,
		"name": props["NAME"],
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
