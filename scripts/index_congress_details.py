#!/bin/env python

import psycopg2, os, re, sys, csv, arrow
import postgres_db

conn = postgres_db.connect()
cur = conn.cursor()

def add_legislator_detail(aclu_id, session, name, value):

	if re.search('^\d+$', aclu_id):
		aclu_id = 'aclu/elections-api/congress_legislator:%s' % aclu_id

	insert_sql = '''
		INSERT INTO congress_legislator_details (
			aclu_id,
			session,
			detail_name,
			detail_value
		) VALUES (%s, %s, %s, %s)
	'''
	values = (
		aclu_id,
		session,
		name,
		value
	)
	cur.execute(insert_sql, values)
	conn.commit()

if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit('Usage: %s [congress session]' % sys.argv[0])

	session = int(sys.argv[1])

	script = os.path.realpath(sys.argv[0])
	scripts_dir = os.path.dirname(script)
	root_dir = os.path.dirname(scripts_dir)

	cur.execute("DROP TABLE IF EXISTS congress_legislator_details CASCADE")
	cur.execute('''
		CREATE TABLE congress_legislator_details (
			aclu_id VARCHAR(255),
			session INTEGER,
			detail_name VARCHAR(255),
			detail_value TEXT
		)
	''')

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

					aclu_id = row[0]
					name = headers[col_num]
					add_legislator_detail(aclu_id, session, name, value)

					col_num += 1

			row_num += 1

		conn.commit()

	print("Done")
