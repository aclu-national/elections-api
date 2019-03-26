#/bin/env python

import os, re, sys, yaml
from subprocess import call

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

source_path = "%s/sources/congress_legislators/legislators-current.yaml" % root_dir
print("Loading %s" % source_path)
file = open(source_path, "r")
data = yaml.load(file)

for legislator in data:
	bioguide = legislator["id"]["bioguide"]
	url = "http://bioguide.congress.gov/bioguide/photo/%s/%s.jpg" % (bioguide[0], bioguide)
	path = "%s/sources/congress_photos/%s.jpg" % (root_dir, bioguide)
	if not os.path.exists(path):
		cmd = ["/usr/bin/curl", "--fail", "-s", "-o", path, url]
		print("Downloading %s" % url)
		call(cmd)

print("Done")
