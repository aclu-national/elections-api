#!/bin/env python

import psycopg2, os, re, sys, csv
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
		type VARCHAR(20),
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
		type,
		office_level,
		primary_date,
		primary_runoff_date,
		general_date,
		general_runoff_date
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

files = []

source_dir = "%s/sources/ballotpedia" % root_dir
path = "%s/ballotpedia_races.csv" % source_dir
csvfile = open(path, 'rb')

reader = csv.reader(csvfile)

row_num = 0
headers = []
skipped = 0

for row in reader:
	if row_num == 0:
		headers = row
	else:
		ocd_id = row[8]
		name = row[0]

		ocd_id_match = re.search('state:(\w\w)', ocd_id)

		if not ocd_id_match:
			print("skipping %s (bad ocd_id)" % name)
			skipped = skipped + 1
			continue
		else:
			print("indexing %s: %s" % (ocd_id, name))

		state = ocd_id_match.group(1)
		year = row[1]
		type = row[13].lower()
		office_level = row[3].lower()
		primary_date = row[9]
		primary_runoff_date = row[10]
		general_date = row[11]
		general_runoff_date = row[12]

		if primary_date == 'None' or primary_date == '':
			primary_date = None
		if primary_runoff_date == 'None' or primary_runoff_date == '':
			primary_runoff_date = None
		if general_date == 'None' or general_date == '':
			general_date = None
		if general_runoff_date == 'None' or general_runoff_date == '':
			general_runoff_date = None

		values = (
			ocd_id, name, state, year, type, office_level,
			primary_date, primary_runoff_date,
			general_date, general_runoff_date
		)
		cur.execute(insert_sql, values)

	row_num = row_num + 1
conn.commit()

print("Done")
