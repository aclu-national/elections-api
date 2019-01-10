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
		detail_name VARCHAR(255),
		detail_value TEXT
	)
''')

insert_sql = '''
	INSERT INTO congress_legislator_details (
		aclu_id,
		session,
		detail_name,
		detail_value
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

			col_num = 0
			for value in row:

				name = headers[col_num]

				values = (
					row[0],
					session,
					name,
					value
				)
				cur.execute(insert_sql, values)

				col_num += 1

		row_num = row_num + 1

	conn.commit()

print("Done")
