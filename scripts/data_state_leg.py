#!/bin/env python

import json, os, sys, re, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import data_index

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

source_dir = "%s/sources/state_leg" % root_dir
data_dir = "%s/data/state_leg" % root_dir

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

files = []
for subdir in os.listdir(source_dir):
	if os.path.isdir("%s/%s" % (source_dir, subdir)):
		for filename in os.listdir("%s/%s" % (source_dir, subdir)):
			if not filename.endswith(".geojson"):
				continue
			files.append("%s/%s/%s" % (source_dir, subdir, filename))

files.sort()

for filename in files:

	print("Loading %s" % filename)
	with open(filename) as data_file:
		data = json.load(data_file)

	for feature in data["features"]:

		props = feature["properties"]
		state_geoid = props["STATEFP"]
		state = us.states.lookup(state_geoid).abbr
		state = str(state).lower()

		chamber = "unknown"
		district_num = "unknown"

		if filename.endswith("sldu.geojson"):
			chamber = "upper"
			district_num = props["SLDUST"]
			chamber_id = "sldu"
		elif filename.endswith("sldl.geojson"):
			chamber = "lower"
			district_num = props["SLDLST"]
			chamber_id = "sldl"
		else:
			print("skipping %s" % path)
			continue

		name = "state_leg_%s_%s_%s.geojson" % (state, chamber, district_num)
		path = "state_leg/%s/%s" % (state, name)
		abs_path = "%s/data/%s" % (root_dir, path)

		non_zero_padded = re.search('^0+(\d+)', district_num)
		if not non_zero_padded:
			non_zero_padded = district_num
		else:
			non_zero_padded = non_zero_padded.group(1)

		ocd_id = 'ocd-division/country:us/state:%s/%s:%s' % (state, chamber_id, non_zero_padded)
		aclu_id = data_index.get_id('elections-api', 'state_leg', path, props["NAMELSAD"])

		print("Saving %s" % path)
		feature["properties"] = {
			"aclu_id": aclu_id,
			"geoid": props["GEOID"],
			"ocd_id": ocd_id,
			"name": props["NAMELSAD"],
			"state": state,
			"chamber": chamber,
			"district_num": district_num,
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
