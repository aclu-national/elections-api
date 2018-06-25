#!/bin/env python

import os, sys, re, json

def simplify(path):
	output_path = path.replace('.geojson', '.display.geojson')
	simplify_args = "-filter-islands min-area=500000 -simplify resolution=300"
	output_args = "-o format=geojson geojson-type=Feature force"
	cmd = "mapshaper %s %s %s %s" % (path, simplify_args, output_args, output_path)
	os.system(cmd)

if __name__ == "__main__":
	script = os.path.realpath(sys.argv[0])
	scripts_dir = os.path.dirname(script)
	root_dir = os.path.dirname(scripts_dir)

	#min_interval = 10.0
	#max_interval = 100.0
	#min_area = 1225433.0
	#max_area = 1716598874914.0
	#area_range = max_area - min_area

	data_dirs = [
		'congress_districts_113',
		'congress_districts_116_pa',
		'counties',
		'state_leg',
		'states'
	]

	dirs = []
	for data_dir in data_dirs:
		if data_dir == 'congress_districts_116_pa':
			dirs.append("%s/data/congress_districts_116_pa" % root_dir)
		else:
			for state in os.listdir("%s/data/%s" % (root_dir, data_dir)):
				dir = "%s/data/%s/%s" % (root_dir, data_dir, state)
				if os.path.isdir(dir):
					dirs.append(dir)

	dirs.sort()

	for dir in dirs:

		state_records = []
		files = []

		for filename in os.listdir(dir):
			if not filename.endswith(".geojson"):
				continue
			elif filename.endswith(".display.geojson"):
				continue
			files.append(filename)

		files.sort()

		for filename in files:
			path = "%s/%s" % (dir, filename)
			simplify(path)
