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
	url VARCHAR(255),
	link_text VARCHAR(255),
	disclaimer VARCHAR(255),
	expires DATE
)''')

cur.execute("DROP TABLE IF EXISTS election_targeted_initiatives CASCADE")
cur.execute('''
CREATE TABLE election_targeted_initiatives (
	ocd_id VARCHAR(255),
	name VARCHAR(255),
	position VARCHAR(16),
	blurb TEXT,
	url VARCHAR(255),
	link_text VARCHAR(255),
	disclaimer VARCHAR(255),
	expires DATE
)''')

conn.commit()

race_insert_sql = '''
	INSERT INTO election_targeted_races (
		ocd_id,
		office,
		summary,
		url,
		link_text,
		disclaimer,
		expires
	) VALUES (%s, %s, %s, %s, %s, %s, %s)
'''

initiative_insert_sql = '''
	INSERT INTO election_targeted_initiatives (
		ocd_id,
		name,
		position,
		blurb,
		url,
		link_text,
		disclaimer,
		expires
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
'''

fh = open('%s/elections-api-private/aclu/aclu_targeted.json' % root_dir, 'rb')
data = json.load(fh)

for item in data["races"]:
	print("race - %s - %s" % (item['ocd_id'], item['office']))
	url = None if not 'url' in item else item['url']
	link_text = None if not 'link_text' in item else item['link_text']
	disclaimer = None if not 'disclaimer' in item else item['disclaimer']
	expires = None if not 'expires' in item else item['expires']
	values = (
		item['ocd_id'],
		item['office'],
		item['summary'],
		url,
		link_text,
		disclaimer,
		expires
	)
	cur.execute(race_insert_sql, values)

for item in data["initiatives"]:
	print("ballot initiative - %s - %s" % (item['ocd_id'], item['name']))
	url = None if not 'url' in item else item['url']
	link_text = None if not 'link_text' in item else item['link_text']
	disclaimer = None if not 'disclaimer' in item else item['disclaimer']
	expires = None if not 'expires' in item else item['expires']
	values = (
		item['ocd_id'],
		item['name'],
		item['position'],
		item['blurb'],
		url,
		link_text,
		disclaimer,
		expires
	)
	cur.execute(initiative_insert_sql, values)

conn.commit()
print("Done")
