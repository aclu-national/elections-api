#!/bin/env python

import os, re, sys, yaml, json

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

legislators = {}

path = "%s/sources/legislators/legislators-current.yaml" % root_dir
print("Loading %s" % path)
file = open(path, "r")
data = yaml.load(file)

for legislator in data:
	id = legislator["id"]["bioguide"]
	legislators[id] = legislator

path = "%s/sources/legislators/legislators-social-media.yaml" % root_dir
print("Loading %s" % path)
file = open(path, "r")
data = yaml.load(file)

for legislator in data:
	id = legislator["id"]["bioguide"]
	legislators[id]["social"] = legislator["social"]

for id in legislators:

	legislator = legislators[id]
	name = "%s.json" % id
	path = "%s/data/legislators/%s" % (root_dir, name)

	print("Saved %s" % path)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		json.dump(legislator, outfile, indent=4, sort_keys=True)

print("Done")
