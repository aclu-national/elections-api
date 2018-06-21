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
for filename in os.listdir(source_dir):
	if not filename.endswith(".csv"):
		continue
	files.append("%s/%s" % (source_dir, filename))

files.sort()

for path in files:

	with open(path, 'rb') as csvfile:

		reader = csv.reader(csvfile)

		row_num = 0
		headers = []

		for row in reader:
			if row_num == 0:
				headers = row
			else:
				ocd_id = row[9]
				name = row[1]
				state = row[0].lower()
				year = row[2]
				type = row[14].lower()
				office_level = row[4].lower()
				primary_date = row[10]
				primary_runoff_date = row[11]
				general_date = row[12]
				general_runoff_date = row[13]

				if primary_date == 'None':
					primary_date = None
				if primary_runoff_date == 'None':
					primary_runoff_date = None
				if general_date == 'None':
					general_date = None
				if general_runoff_date == 'None':
					general_runoff_date = None

				print("indexing %s: %s" % (ocd_id, name))

				values = (
					ocd_id, name, state, year, type, office_level,
					primary_date, primary_runoff_date,
					general_date, general_runoff_date
				)
				cur.execute(insert_sql, values)

			row_num = row_num + 1
		conn.commit()

print("Done")
