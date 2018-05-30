#!/bin/env python

import json, os, sys, re, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

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

for path in files:

	print("Loading %s" % path)
	with open(path) as data_file:
		data = json.load(data_file)

	for feature in data["features"]:

		props = feature["properties"]
		state_fips = props["STATEFP"]
		state = us.states.lookup(state_fips).abbr
		state = str(state).lower()

		chamber = "unknown"
		district_num = "unknown"

		if props["LSAD"] == "LU":
			chamber = "upper"
			district_num = props["SLDUST"]
		elif props["LSAD"] == "LL":
			chamber = "lower"
			district_num = props["SLDLST"]

		name = "state_leg_%s_%s_%s" % (state, chamber, district_num)
		path = "%s/%s/%s.geojson" % (data_dir, state, name)

		print("Saving %s" % path)
		feature["properties"] = {
			"state": state,
			"chamber": chamber,
			"district_num": district_num,
			"name": props["NAMELSAD"],
			"area_land": props["ALAND"],
			"area_water": props["AWATER"],
			"fips_id": props["GEOID"]
		}
		feature["id"] = name

		mapzen.whosonfirst.utils.ensure_bbox(feature)

		dirname = os.path.dirname(path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		with open(path, 'w') as outfile:
			encoder.encode_feature(feature, outfile)

	print("Done")
