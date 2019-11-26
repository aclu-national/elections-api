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
		office_type VARCHAR(255),
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

source_dir = "%s/elections-api-private/ballotpedia" % root_dir
path = "%s/ballotpedia_races.csv" % source_dir
csvfile = open(path, 'r', encoding='utf-8')

reader = csv.reader(csvfile)

row_num = 0
headers = []

skipped = []
guessed = {}

empty_office_type = []
guessed_office_type = {}

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

def guess_office_type(name):

	match = re.search('Superior Court of .+ County California', name)
	if match:
		return 'County Judge'

	match = re.search('Supreme Court', name)
	if match:
		return 'State Supreme Court'

	match = re.search('County Justice of the Peace', name)
	if match:
		return 'Justice of the Peace'

	match = re.search('District Court', name)
	if match:
		return 'County Judge'

	match = re.search('Parish Traffic Court', name)
	if match:
		return 'County Judge'

	match = re.search('County Court', name)
	if match:
		return 'County Judge'

	match = re.search('County Magistrate', name)
	if match:
		return 'County Judge'

	match = re.search('County.* Clerk', name)
	if match:
		return 'County Clerk'

	match = re.search('County Constable', name)
	if match:
		return 'County Constable'

	match = re.search('^(.+?) (County .+)$', name)
	if match:
		return match.group(2)

	match = re.search('^(.+?) Community College', name)
	if match:
		return 'Community College Board'

	match = re.search('University.* Board', name)
	if match:
		return 'University Board'

	match = re.search('(Natural Resources|Water Reclamation)', name)
	if match:
		return 'Natural Resources Board'

	match = re.search('(Public Power|Metropolitan Utilities)', name)
	if match:
		return 'Public Utilities Board'

	match = re.search('Board of Alderman', name)
	if match:
		return 'Board of Alderman'

	for state in us.states.STATES:

		match = re.match('^%s (.+)$' % state.name, name)
		if match:
			return 'State %s' % match.group(1)

		match = re.match('^(.+) of %s$' % state.name, name)
		if match:
			return 'State %s' % match.group(1)

	return ''

def normalize_office_type(office_type, office_level):

	match = re.search("(District|Prosecuting|County|Commonwealth's|State's) Attorney", office_type, re.I)
	if match:
		before = office_type
		office_type = 'District Attorney'

	office_type = re.sub('(Precinct|Place|District|Office|Area|Position|Ward|Zone|Division) \d+', '', office_type, re.I)
	office_type = office_type.lower()
	office_type = re.sub('\W+', '_', office_type)
	office_type = re.sub('_$', '', office_type)

	if office_type == 'representative' or office_type == 'senator':
		if office_level == 'federal':
			office_type = 'us_%s' % office_type
		elif office_level == 'state':
			office_type = 'state_%s' % office_type

	office_type = re.sub('_commission$', '_commissioner', office_type)
	office_type = re.sub('^state_state_', 'state_', office_type)
	office_type = re.sub('^state_(.+_of_state)$', '\g<1>', office_type)
	office_type = re.sub('(_public_instruction|_schools)$', '_education', office_type)

	office_type = office_type.replace('governor_s_', 'governors_')
	office_type = office_type.replace('state_u_s_shadow_', 'us_shadow_')
	office_type = office_type.replace('county_sheriff_al', 'county_sheriff')
	office_type = office_type.replace('insurance_and_safety_fire_commissioner', 'insurance_commissioner')
	office_type = office_type.replace('county_assessor_of_property', 'county_assessor')
	office_type = office_type.replace('county_assessor_county_clerk_recorder', 'county_assessor_clerk_recorder')
	office_type = office_type.replace('county_assessor_recorder_county_clerk', 'county_assessor_clerk_recorder')
	office_type = office_type.replace('commissioner_of_labor_and_industries', 'commissioner_of_labor')
	office_type = office_type.replace('commissioner_of_agriculture_and_consumer_services', 'commissioner_of_agriculture')
	office_type = office_type.replace('commissioner_of_agriculture_and_industries', 'commissioner_of_agriculture')
	office_type = office_type.replace('commissioner_of_state_lands', 'commissioner_of_public_lands')
	office_type = office_type.replace('superindendent', 'superintendent')
	office_type = office_type.replace('state_attorney_general', 'attorney_general')
	office_type = office_type.replace('state_lieutenant_governor', 'lieutenant_governor')

	return office_type

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

		if office_level == 'local':
			office_level = 'county'

		primary_date = row['primary_election_date']
		primary_runoff_date = row['primary_runoff_election_date']
		general_date = row['general_election_date']
		general_runoff_date = row['general_runoff_election_date']

		if office_type == '':
			office_type = guess_office_type(name)
			if not office_type:
				empty_office_type.append(name)

		office_type = normalize_office_type(office_type, office_level)

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

path = "%s/sources/aclu/aclu_election_races.csv" % root_dir
csvfile = open(path, 'r', encoding='utf-8')
reader = csv.reader(csvfile)

row_num = 0
headers = []

for row in reader:
	if row_num == 0:
		headers = row
	else:
		if row[0] == "":
			continue
		primary_date = None if row[7] == "" else row[7]
		primary_runoff_date = None if row[8] == "" else row[8]
		general_date = None if row[9] == "" else row[9]
		general_runoff_date = None if row[10] == "" else row[10]
		values = (
			row[0],
			row[1],
			row[2],
			row[3],
			row[4],
			row[5],
			row[6],
			primary_date,
			primary_runoff_date,
			general_date,
			general_runoff_date
		)
		cur.execute(insert_sql, values)

	row_num = row_num + 1
conn.commit()

print("Done")

if len(skipped) > 0:
	print("Skipped:")
	for name in skipped:
		print("\t%s" % name)

print("%d rows with empty ocd_id" % len(skipped))

if len(empty_office_type) > 0:
	print("Empty office_type:")
	for name in empty_office_type:
		print("\t%s" % name)

print("%d rows with empty office_type" % len(empty_office_type))
print("%d from aclu_election_races.csv" % (row_num - 1,))
