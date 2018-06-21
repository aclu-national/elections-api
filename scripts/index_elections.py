#!/bin/env python

import os, sys, psycopg2, re, json, csv, arrow, us
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS elections CASCADE")
cur.execute('''
CREATE TABLE elections (
	state CHAR(2),
	description VARCHAR(255),
	type VARCHAR(255),
	election_date DATE,
	primary_reg_deadline DATE,
	primary_reg_mail_online_deadline DATE,
	general_reg_deadline DATE,
	general_reg_mail_online_deadline DATE,
	online_url VARCHAR(255),
	same_day VARCHAR(255),
	absentee VARCHAR(255),
	early VARCHAR(255),
	early_start DATE,
	early_end DATE,
	vbm_apply DATE,
	vbm_ballot_due DATE,
	id_required VARCHAR(255),
	sos_info_url VARCHAR(255),
	polling_place_locator_url VARCHAR(255),
	ballotpedia_url VARCHAR(255),
	notes VARCHAR(255)
)''')
conn.commit()

insert_sql = '''
	INSERT INTO elections (
		state,
		description,
		type,
		election_date,
		primary_reg_deadline,
		primary_reg_mail_online_deadline,
		general_reg_deadline,
		general_reg_mail_online_deadline,
		online_url,
		same_day,
		absentee,
		early,
		early_start,
		early_end,
		vbm_apply,
		vbm_ballot_due,
		id_required,
		sos_info_url,
		polling_place_locator_url,
		ballotpedia_url,
		notes
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

fh = open('%s/sources/aclu/aclu_elections.csv' % root_dir, 'rb')
reader = csv.reader(fh)

row_num = 0
header = []

def format_date(date):
	if date == '':
		return None
	else:
		return arrow.get(date, 'M/D/YYYY').format('YYYY-MM-DD')

for row in reader:
	if row_num == 0:
		header = row
	else:

		print("%s - %s - %s" % (row[0], row[1], format_date(row[3])))

		state = us.states.lookup(unicode(row[0])).abbr.lower()
		values = (
			state,
			row[1],
			row[2],
			format_date(row[3]),
			format_date(row[4]),
			format_date(row[5]),
			format_date(row[6]),
			format_date(row[7]),
			row[8],
			row[9],
			row[10],
			row[11],
			format_date(row[12]),
			format_date(row[13]),
			format_date(row[14]),
			format_date(row[15]),
			row[16],
			row[17],
			row[18],
			row[19],
			row[20]
		)
		cur.execute(insert_sql, values)
	row_num = row_num + 1

conn.commit()
print("Done")
