#!/bin/env python

import json, os, sys, us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

path = "../sources/districts_116_pa/districts_116_pa.geojson"

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

	district = int(props["DISTRICT"])

	path = "districts_116_pa/districts_116_pa_%s.geojson" % district
	print("Saving %s" % path)
	feature["properties"] = {
		"state": state,
		"start_session": 116,
		"start_date": sessions[116]["start_date"],
		"end_session": 116,
		"end_date": sessions[116]["end_date"],
		"district": district
	}
	feature["id"] = "districts_116_pa_%s" % district

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)
