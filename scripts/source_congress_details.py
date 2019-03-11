#!/bin/env python

import csv, os, re, sys
import index_congress_scores

columns_115 = [
	"running_in_2018"
]
columns_116 = [
	"running_for_president"
]

if len(sys.argv) < 2:
	sys.exit('Usage: %s [congress session]' % sys.argv[0])

session = int(sys.argv[1])

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

for chamber in ['rep', 'sen']:

	scores_path = '%s/elections-api-private/aclu/aclu_%s_scores_%d.csv' % (root_dir, chamber, session)
	scores_file = open(scores_path, 'rb')
	reader = csv.reader(scores_file)

	print("reading from %s" % scores_path)

	details_path = "%s/sources/aclu/aclu_%s_details_%d.csv" % (root_dir, chamber, session)
	details_file = open(details_path, 'wb')
	writer = csv.writer(details_file)

	print("writing to %s" % details_path)

	header = ['aclu_id', 'display_name']
	if session == 115:
		header += columns_115
	elif session == 116:
		header += columns_116

	writer.writerow(header)
	row_num = 0

	for row in reader:

		row_num += 1

		if row_num < 4:
			continue

		name = row[0]
		aclu_id = row[1]

		if name == "Vacant" or name == "":
			continue
		if name == "LEGEND:":
			break

		if aclu_id == "":
			if chamber == "rep":
				aclu_id = index_congress_scores.get_rep_id(row[2], name)
			elif chamber == "sen":
				aclu_id = index_congress_scores.get_sen_id(row[2], name)
			if aclu_id:
				aclu_id = aclu_id.replace("aclu/elections-api/congress_legislator:", "")

		name = re.sub("\s*\(.+\)\s*$", "", name)

		values = [aclu_id, name]

		print(name)

		if session == 115:
			for col in columns_115:
				values.append("0")

		if session == 116:
			for col in columns_116:
				values.append("0")

		writer.writerow(values)

print("Done")
