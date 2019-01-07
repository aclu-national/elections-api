#!/bin/env python

import psycopg2, os, re, sys, csv, arrow
import postgres_db

if len(sys.argv) < 2:
	sys.exit('Usage: %s [congress session]' % sys.argv[0])

session = int(sys.argv[1])

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS congress_legislator_details CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_details (
		aclu_id VARCHAR(255),
		session INTEGER,
		display_name VARCHAR(255),
		running_in_2018 INT
	)
''')

insert_sql = '''
	INSERT INTO congress_legislator_details (
		aclu_id,
		session,
		display_name,
		running_in_2018
	) VALUES (%s, %s, %s, %s)
'''

for chamber in ['rep', 'sen']:
	path = '%s/sources/aclu/aclu_%s_details_%d.csv' % (root_dir, chamber, session)
	file = open(path, 'rb')
	reader = csv.reader(file)

	row_num = 0
	headers = []

	for row in reader:
		if row_num == 0:
			headers = row
		else:
			print(row[1])

			running_in_2018 = None
			if row[2] == '1' or row[2] == '0':
				running_in_2018 = int(row[2])

			values = (
				row[0],
				session,
				row[1],
				running_in_2018
			)
			cur.execute(insert_sql, values)

		row_num = row_num + 1

	conn.commit()

print("Done")
