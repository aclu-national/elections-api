#!/usr/bin/env python

import os, psycopg2

default_dsn = 'dbname=elections'
db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
db = psycopg2.connect(db_dsn)
cur = db.cursor()

cur.execute('''
	DELETE FROM google_civic_info
''')
num_rows = cur.rowcount

db.commit()
db.close()

print("deleted %d cache records" % num_rows)
