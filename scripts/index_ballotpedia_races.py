#!/bin/env python

import psycopg2, os, re, sys, csv, us
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS election_races CASCADE")
cur.execute('''
	CREATE TABLE election_races (
		ocd_id VARCHAR(255),
		name VARCHAR(255),
		state CHAR(2),
		year CHAR(4),
		race_type VARCHAR(20),
		office_type VARCHAR(64),
		office_level VARCHAR(20),
		primary_date DATE,
		primary_runoff_date DATE,
		general_date DATE,
		general_runoff_date DATE
	)
''')
conn.commit()

insert_sql = '''
	INSERT INTO election_races (
		ocd_id,
		name,
		state,
		year,
		race_type,
		office_type,
		office_level,
		primary_date,
		primary_runoff_date,
		general_date,
		general_runoff_date
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

files = []

source_dir = "%s/sources/ballotpedia" % root_dir
path = "%s/ballotpedia_races.csv" % source_dir
csvfile = open(path, 'rb')

reader = csv.reader(csvfile)

row_num = 0
headers = []
skipped = []
guessed = {}

def csv_row(row, headers):
	col_num = 0
	row_obj = {}
	for key in headers:
		row_obj[key] = row[col_num]
		col_num = col_num + 1
	return row_obj

def guess_ocd_id(name):

	match = re.match('^U.S. House (.+) At-large District$', name, re.I)
	if match:
		state_name = unicode(match.group(1))
		state = us.states.lookup(state_name)
		if state:
			return "ocd-division/country:us/state:%s" % state.abbr.lower()

	match = re.match('^(.+?) Supreme Court', name)
	if match:
		state_name = unicode(match.group(1))
		state = us.states.lookup(state_name)
		if state:
			return "ocd-division/country:us/state:%s" % state.abbr.lower()

	# Maryland Court of Appeals
	match = re.match('^(.+?) Court of (Criminal )?Appeals', name)
	if match:
		state_name = unicode(match.group(1))
		state = us.states.lookup(state_name)
		if state:
			return "ocd-division/country:us/state:%s" % state.abbr.lower()

	match = re.match('^New Hampshire House of Representatives (.+?) (\d+)$', name)
	if match:
		sldl = match.group(2)
		return "ocd-division/country:us/state:nh/sldl:%s" % sldl

	return ''

for row in reader:
	if row_num == 0:
		headers = row
	else:
		row = csv_row(row, headers)
		ocd_id = row['ocdid']
		name = row['office_name']

		ocd_id_match = re.search('(state|district):(\w\w)', ocd_id)

		if not ocd_id_match:
			ocd_id = guess_ocd_id(name)
			ocd_id_match = re.search('(state|district):(\w\w)', ocd_id)
			if ocd_id_match:
				guessed[name] = ocd_id
			else:
				print("skipping %s (bad ocd_id)" % name)
				skipped.append(name)
				continue
		else:
			print("indexing %s: %s" % (ocd_id, name))

		state = ocd_id_match.group(2)
		year = row['year']
		race_type = row['type'].lower()
		office_type = row['office_type']
		office_level = row['office_level'].lower()
		primary_date = row['primary_election_date']
		primary_runoff_date = row['primary_runoff_election_date']
		general_date = row['general_election_date']
		general_runoff_date = row['general_runoff_election_date']

		if primary_date == 'None' or primary_date == '':
			primary_date = None
		if primary_runoff_date == 'None' or primary_runoff_date == '':
			primary_runoff_date = None
		if general_date == 'None' or general_date == '':
			general_date = None
		if general_runoff_date == 'None' or general_runoff_date == '':
			general_runoff_date = None

		values = (
			ocd_id, name, state, year, race_type, office_type, office_level,
			primary_date, primary_runoff_date,
			general_date, general_runoff_date
		)
		cur.execute(insert_sql, values)

	row_num = row_num + 1
conn.commit()

print("Done")

if len(guessed) > 0:
	print("Guessed ocd_ids:")
	for name in guessed:
		print("\t%s: %s" % (name, guessed[name]))

if len(skipped) > 0:
	print("Skipped:")
	for name in skipped:
		print("\t%s" % name)

print("Skipped %d rows" % len(skipped))
