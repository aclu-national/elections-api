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
	position VARCHAR(255) PRIMARY KEY,
	description TEXT
)''')
conn.commit()

insert_sql = '''
	INSERT INTO election_blurbs (
		position,
		description
	) VALUES (%s, %s)
'''

dir = "%s/sources/aclu/blurbs" % root_dir
for filename in os.listdir(dir):
	if not filename.endswith(".html"):
		continue

	position = filename.replace('.html', '')
	with open("%s/%s" % (dir, filename)) as file:
		description = file.read()
		file.close()

	print(position)

	values = (
		position,
		description
	)
	cur.execute(insert_sql, values)

conn.commit()
print("Done")
