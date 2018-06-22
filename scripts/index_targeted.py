#!/bin/env python

import os, sys, psycopg2, re, json, csv, arrow, us
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS elections_targeted CASCADE")
cur.execute("DROP TABLE IF EXISTS election_targeted CASCADE")
cur.execute('''
CREATE TABLE election_targeted (
	type VARCHAR(20),
	ocd_id VARCHAR(255),
	title VARCHAR(255),
	description TEXT
)''')
conn.commit()

insert_sql = '''
	INSERT INTO election_targeted (
		type,
		ocd_id,
		title,
		description
	) VALUES (%s, %s, %s, %s)
'''

fh = open('%s/sources/aclu/aclu_targeted.json' % root_dir, 'rb')
data = json.load(fh)

for item in data["races"]:
	print("race - %s - %s" % (item['ocd_id'], item['title']))
	values = (
		'race',
		item['ocd_id'],
		item['title'],
		item['description']
	)
	cur.execute(insert_sql, values)

for item in data["ballot_initiatives"]:
	print("ballot initiative - %s - %s" % (item['ocd_id'], item['title']))
	values = (
		'ballot_initiative',
		item['ocd_id'],
		item['title'],
		item['description']
	)
	cur.execute(insert_sql, values)

conn.commit()
print("Done")
