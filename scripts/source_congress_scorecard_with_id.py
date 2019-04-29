#!/bin/env python

import csv, os, re, sys
import postgres_db
import unicodedata
import re

if len(sys.argv) < 2:
	sys.exit('Usage: %s [congress session]' % sys.argv[0])

session = int(sys.argv[1])

def strip_accents(s):
	s = s.replace("'", "")
	s = s.decode('utf-8')
	return ''.join(c for c in unicodedata.normalize('NFD', s)
		if unicodedata.category(c) != 'Mn')

def get_rep_id(state_district, name):

	if not state_district in reps:
		return None
	rep = reps[state_district]
	name = strip_accents(name).lower()
	lname = strip_accents(rep["last_name"]).lower()
	if name.find(lname) == -1:
		print("Warning: could not find %s instead found %s" % (name, lname))
	aclu_id = rep["aclu_id"]
	results = re.search('(\d+)', aclu_id)
	aclu_id_number = results.group(1)
	return aclu_id_number

def get_sen_id(state, name):
	print(state, name)
	found = False
	name = strip_accents(name)
	for rep in sens[state]:
		lname = strip_accents(rep["last_name"])
		if name.find(lname) != -1:
			legislator_id = rep["aclu_id"]
			found = True
			break
	if not found:
		print("COULD NOT find an id for %s" % name)
		return None
	results = re.search('(\d+)', legislator_id)
	aclu_id_number = results.group(1)
	return aclu_id_number

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

reps = {}
sens = {}

conn = postgres_db.connect()
cur = conn.cursor()

# Get all the legislators (indexed from the unitedstates congress repo)
# select these properties where session id matches the passed in session
# and term start date is greater session start and term end date is smaller
# session end date
cur.execute('''
	SELECT lt.aclu_id, lt.state, lt.district_num, lt.type, l.last_name
	FROM congress_legislator_terms AS lt,
	     congress_legislators AS l,
	     congress_sessions AS s
	WHERE s.id = {session}
	  AND (
	  	lt.start_date >= s.start_date AND lt.end_date <= s.end_date
	  	OR lt.start_date <= s.start_date AND lt.end_date >= s.end_date
	  )
  AND lt.aclu_id = l.aclu_id
'''.format(session=session))

rs = cur.fetchall()
if rs:
	for row in rs:
		aclu_id = row[0]
		state = row[1].upper()
		district_num = row[2]
		type = row[3]
		# they are a representative, so we use district numbers
		if type == 'rep':
			if district_num == 0:
				district_num = 1
			if int(district_num) < 10:
				district_num = "0%s" % district_num
			else:
				district_num = str(district_num)
			state_district = "%s-%s" % (state, district_num)
			reps[state_district] = {
				'aclu_id': aclu_id,
				'last_name': row[4]
			}
		# they are a senator, so we expect more than one per state
		else:
			if not state in sens:
				sens[state] = []
				# sens['ak']
			found = False
			for rep in sens[state]:
				if rep['last_name'] == row[4]:
					found = True

			if not found:
				print("not found %s" % aclu_id)
				sens[state].append({
					'aclu_id': aclu_id,
					'last_name': row[4]
				})

for chamber in ['rep', 'sen']:

	scores_path = '%s/elections-api-private/aclu/aclu_%s_scores_%d.csv' % (root_dir, chamber, session)
	scores_file = open(scores_path, 'rb')
	reader = csv.reader(scores_file)

	print("reading from %s" % scores_path)

  # This file doesn't exist until we write to it
	scores_with_id_path = "%s/sources/aclu/aclu_%s_scores_with_id_%d.csv" % (root_dir, chamber, session)
	scores_with_id_file = open(scores_with_id_path, 'wb')
	writer = csv.writer(scores_with_id_file)

	print("writing to %s" % scores_with_id_path)

	row_num = 0

	for row in reader:

		row_num += 1

		name = row[0]
		state_or_state_district = row[2]

    # Don't start until row 4 because there are a few Header rows
		if row_num < 4:
			continue

		if name == 'LEGEND:':
				break

		if name != 'LEGEND:' and name != '' and name != 'Z-Vacant':
			if chamber == 'rep':
				leg_id = get_rep_id(state_or_state_district, name)
			elif chamber == 'sen':
				leg_id = get_sen_id(state_or_state_district, name)

			values = [name, leg_id, state_or_state_district]
			writer.writerow(values)

print("Done")