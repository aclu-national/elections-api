#!/bin/env python

import json, os, sys, us, area, re
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/sources/districts_116_pa/districts_116_pa.geojson" % root_dir

sessions = {}
sessions[116] = {
	"start_date": "2019-01-03",
	"end_date": "2021-01-03"
}

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % path)
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state = "pa"

	district_num = str(props["DISTRICT"])
	geoid = "42%s" % district_num

	name = "district_116_pa_%s.geojson" % district_num
	path = "%s/data/districts_116_pa/%s" % (root_dir, name)

	non_zero_padded = re.search('^0+(\d+)', district_num)
	if not non_zero_padded:
		non_zero_padded = district_num
	else:
		non_zero_padded = non_zero_padded.group(1)

	ocd_id = 'ocd-division/country:us/state:pa/cd:%s' % non_zero_padded

	print("Saving %s" % path)
	feature["properties"] = {
		"geoid": geoid,
		"ocd_id": ocd_id,
		"state": state,
		"start_session": 116,
		"start_date": sessions[116]["start_date"],
		"end_session": 116,
		"end_date": sessions[116]["end_date"],
		"district_num": district_num
	}
	feature["id"] = "districts_116_pa_%s" % district_num

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)

print("Done")
