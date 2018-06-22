#!/bin/env python

import os, sys, psycopg2, re, json, csv, arrow, us
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

def format_date(date):
	if date == '':
		return None
	else:
		return arrow.get(date, 'M/D/YYYY').format('YYYY-MM-DD')

cur.execute("DROP TABLE IF EXISTS elections CASCADE")
cur.execute("DROP TABLE IF EXISTS election_info CASCADE")
cur.execute('''
CREATE TABLE election_info (
	state CHAR(2) PRIMARY KEY,
	online_reg_url VARCHAR(255),
	check_reg_url VARCHAR(255),
	polling_place_url VARCHAR(255),
	voter_id_req VARCHAR(255),
	same_day VARCHAR(255),
	vote_by_mail VARCHAR(255),
	early_voting VARCHAR(255)
)''')
conn.commit()

insert_sql = '''
	INSERT INTO election_info (
		state,
		online_reg_url,
		check_reg_url,
		polling_place_url,
		voter_id_req,
		same_day,
		vote_by_mail,
		early_voting
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
'''

fh = open('%s/sources/aclu/aclu_election_info.csv' % root_dir, 'rb')
reader = csv.reader(fh)

row_num = 0
header = []

for row in reader:
	if row_num == 0:
		header = row
	else:

		state = row[0].lower()

		print("election_info - %s" % state)

		values = (
			state,
			row[2],
			row[3],
			row[4],
			row[5],
			row[6],
			row[7],
			row[8]
		)
		cur.execute(insert_sql, values)

	row_num = row_num + 1

conn.commit()

cur.execute("DROP TABLE IF EXISTS election_dates CASCADE")
cur.execute('''
CREATE TABLE election_dates (
	state CHAR(2),
	type VARCHAR(20),
	name VARCHAR(255),
	value DATE
)''')
conn.commit()

insert_sql = '''
	INSERT INTO election_dates (
		state,
		type,
		name,
		value
	) VALUES (%s, %s, %s, %s)
'''

for type in ['primary', 'general']:

	fh = open('%s/sources/aclu/aclu_election_%s.csv' % (root_dir, type), 'rb')
	reader = csv.reader(fh)

	row_num = 0
	header = []

	for row in reader:

		state = row.pop(0)
		state = state.lower()
		state_name = row.pop(0)
		col_num = 0

		if row_num == 0:
			header = row
		else:
			for value in row:

				name = header[col_num]
				if name == 'notes':
					break

				print("election_date - %s - %s - %s" % (state, type, name))

				values = (
					state,
					type,
					name,
					format_date(value)
				)
				cur.execute(insert_sql, values)

				col_num = col_num + 1

		row_num = row_num + 1
		conn.commit()

print("Done")
