#!/bin/env python

import os, sys, psycopg2, re, json, csv, arrow, us
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS election_blurbs CASCADE")
cur.execute('''
CREATE TABLE election_blurbs (
	office VARCHAR(255) PRIMARY KEY,
	name VARCHAR(255),
	title TEXT,
	summary TEXT,
	details_title TEXT
)''')

cur.execute("DROP TABLE IF EXISTS election_blurb_details CASCADE")
cur.execute('''
CREATE TABLE election_blurb_details (
	office VARCHAR(255),
	detail TEXT,
	detail_number INTEGER
)''')

cur.execute("DROP TABLE IF EXISTS election_blurb_alt_names CASCADE")
cur.execute('''
CREATE TABLE election_blurb_alt_names (
	office VARCHAR(255),
	alt_name VARCHAR(255)
)''')

conn.commit()

blurb_insert_sql = '''
	INSERT INTO election_blurbs (
		office,
		name,
		title,
		summary,
		details_title
	) VALUES (%s, %s, %s, %s, %s)
'''

detail_insert_sql = '''
	INSERT INTO election_blurb_details (
		office,
		detail,
		detail_number
	) VALUES (%s, %s, %s)
'''

alt_name_insert_sql = '''
	INSERT INTO election_blurb_alt_names (
		office,
		alt_name
	) VALUES (%s, %s)
'''

filename = "%s/sources/aclu/aclu_blurbs.json" % root_dir
file = open(filename, 'rb')
data = json.load(file)

for office in data:

	print(office)

	values = (
		office,
		data[office]['name'],
		data[office]['title'],
		data[office]['summary'],
		data[office]['details_title']
	)
	cur.execute(blurb_insert_sql, values)

	detail_num = 0
	for detail in data[office]['details']:
		values = (
			office,
			detail,
			detail_num
		)
		cur.execute(detail_insert_sql, values)
		detail_num = detail_num + 1

	if 'alt_names' in data[office]:
		for alt_name in data[office]['alt_names']:
			values = (
				office,
				alt_name
			)
			cur.execute(alt_name_insert_sql, values)

conn.commit()
print("Done")
