#!/bin/env python

import os, re, sys, yaml, json, unicodedata
import data_index

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

# Build lookup of existing legislators to avoid duplicate records
existing_legislator_lookup = {}
index = data_index.get_index('elections-api')
for path in index['lookup'] :
	if ('congress_legislators' in path) :
		abs_path = "%s/data/%s" % (root_dir, path)
		with open(abs_path, 'r') as f:
			legislator = json.load(f)
			bioguide_id = legislator['id']['bioguide']
			existing_legislator_lookup[bioguide_id] = index['lookup'][path]

source_path = "%s/sources/congress_legislators/legislators-current.yaml" % root_dir
print("Loading %s" % source_path)
file = open(source_path, "r")
data = yaml.load(file)

legislator_lookup = {}
legislator_list = []

for legislator in data:
	id = legislator["id"]["bioguide"]
	legislator_lookup[id] = legislator
	if (id not in existing_legislator_lookup):
		legislator_list.append(legislator)

source_path = "%s/sources/congress_legislators/legislators-social-media.yaml" % root_dir
print("Loading %s" % source_path)
file = open(source_path, "r")
data = yaml.load(file)

for legislator in data:
	id = legislator["id"]["bioguide"]
	legislator_lookup[id]["social"] = legislator["social"]

def strip_accents(s):
	if (type(s) == str):
		s = s.decode('utf-8')
	return ''.join(c for c in unicodedata.normalize('NFD', s)
		if unicodedata.category(c) != 'Mn')

def get_filename(legislator):
	fname = strip_accents(legislator["name"]["first"])
	lname = strip_accents(legislator["name"]["last"])
	name = "%s-%s" % (fname, lname)
	slug = re.sub('[^A-Za-z]+', '-', name).lower()
	state = legislator["terms"][0]["state"].lower()
	filename = "congress_legislator_%s_%s.json" % (state, slug)
	return filename

def get_url_slug(legislator):
	lname = strip_accents(legislator["name"]["last"])
	fname = strip_accents(legislator["name"]["first"])
	name = "%s-%s" % (fname, lname)
	name = re.sub('[^A-Za-z]+', '-', name).lower()
	state = legislator["terms"][0]["state"].lower()
	return "%s-%s" % (state, name)

def sort_legislators(a, b):
	a_filename = get_filename(a)
	b_filename = get_filename(b)
	if a_filename > b_filename:
		return 1
	else:
		return -1

legislator_list.sort(sort_legislators)

for legislator in legislator_list:

	filename = get_filename(legislator)
	state = legislator["terms"][0]["state"].lower()
	fname = legislator["name"]["first"]
	lname = legislator["name"]["last"]
	name = "%s %s" % (fname, lname)

	path = "congress_legislators/%s/%s" % (state, filename)
	abs_path = "%s/data/%s" % (root_dir, path)

	aclu_id = data_index.get_id('elections-api', 'congress_legislator', path, name)

	legislator["id"]["aclu_id"] = aclu_id
	legislator["url_slug"] = get_url_slug(legislator)

	print("Saving %s" % path)

	dirname = os.path.dirname(abs_path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(abs_path, 'w') as outfile:
		json.dump(legislator, outfile, indent=2, sort_keys=True)

print("Saving index")
data_index.save_index('elections-api')

print("Done")
