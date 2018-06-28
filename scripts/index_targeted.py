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
cur.execute("DROP TABLE IF EXISTS election_targeted_races CASCADE")
cur.execute('''
CREATE TABLE election_targeted_races (
	ocd_id VARCHAR(255),
	office VARCHAR(255),
	summary TEXT,
	url VARCHAR(255)
)''')

cur.execute("DROP TABLE IF EXISTS election_targeted_initiatives CASCADE")
cur.execute('''
CREATE TABLE election_targeted_initiatives (
	ocd_id VARCHAR(255),
	name VARCHAR(255),
	position VARCHAR(16),
	blurb TEXT,
	url VARCHAR(255)
)''')

conn.commit()

race_insert_sql = '''
	INSERT INTO election_targeted_races (
		ocd_id,
		office,
		summary,
		url
	) VALUES (%s, %s, %s, %s)
'''

initiative_insert_sql = '''
	INSERT INTO election_targeted_initiatives (
		ocd_id,
		name,
		position,
		blurb,
		url
	) VALUES (%s, %s, %s, %s, %s)
'''

fh = open('%s/sources/aclu/aclu_targeted.json' % root_dir, 'rb')
data = json.load(fh)

for item in data["races"]:
	print("race - %s - %s" % (item['ocd_id'], item['office']))
	values = (
		item['ocd_id'],
		item['office'],
		item['summary'],
		item['url']
	)
	cur.execute(race_insert_sql, values)

for item in data["initiatives"]:
	print("ballot initiative - %s - %s" % (item['ocd_id'], item['name']))
	values = (
		item['ocd_id'],
		item['name'],
		item['position'],
		item['blurb'],
		item['url']
	)
	cur.execute(initiative_insert_sql, values)

conn.commit()
print("Done")
