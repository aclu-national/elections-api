#!/bin/env python

import json, os, sys, us, area, re
import data_index
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

source_path = "%s/sources/congress_districts_116_pa/congress_districts_116_pa.geojson" % root_dir

sessions = {
	116: {
		"start_date": "2019-01-03",
		"end_date": "2021-01-03"
	}
}

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading %s" % source_path)
with open(source_path, 'r', encoding='utf-8') as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state = "pa"

	district_num = str(props["DISTRICT"])
	geoid = "42%s" % district_num

	filename = "congress_district_116_pa_%s.geojson" % district_num
	path = "congress_districts_116_pa/%s" % filename
	abs_path = "%s/data/%s" % (root_dir, path)

	non_zero_padded = re.search('^0+(\d+)', district_num)
	if not non_zero_padded:
		non_zero_padded = district_num
	else:
		non_zero_padded = non_zero_padded.group(1)

	ocd_id = 'ocd-division/country:us/state:pa/cd:%s' % non_zero_padded
	name = "PA Congressional District %s" % non_zero_padded
	aclu_id = data_index.get_id('elections-api', 'congress_district', path, name)

	print("Saving %s" % path)
	feature["properties"] = {
		"aclu_id": aclu_id,
		"geoid": geoid,
		"ocd_id": ocd_id,
		"name": name,
		"state": state,
		"start_session": 116,
		"start_date": sessions[116]["start_date"],
		"end_session": 116,
		"end_date": sessions[116]["end_date"],
		"district_num": district_num
	}
	feature["id"] = aclu_id

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(abs_path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(abs_path, 'w', encoding='utf-8') as outfile:
		encoder.encode_feature(feature, outfile)

print("Saving index")
data_index.save_index('elections-api')

print("Done")
