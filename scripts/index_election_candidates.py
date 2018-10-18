#!/bin/env python

import psycopg2, os, re, sys, csv, us
import postgres_db

# We only import Federal candidates and State candidates from states where we're
# approved to display them. (20181018/dphiffer)
state_filter = [
	"fl",
	"mi",
	"ga",
	"ks",
	"wi",
	"pa",
	"ia",
	"mn",
	"oh",
	"tn"
]

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS election_candidates CASCADE")
cur.execute('''
	CREATE TABLE election_candidates (
		ocd_id VARCHAR(255),
		state CHAR(2),
		name VARCHAR(255),
		first_name VARCHAR(255),
		last_name VARCHAR(255),
		ballotpedia_url VARCHAR(255),
		candidates_id INT,
		person_id INT,
		party VARCHAR(255),
		race_id INT,
		office_name VARCHAR(255),
		office_level VARCHAR(32),
		district_type VARCHAR(32),
		is_incumbent BOOLEAN,
		primary_date DATE,
		primary_status VARCHAR(32),
		primary_runoff_date DATE,
		primary_runoff_status VARCHAR(32),
		general_date DATE,
		general_status VARCHAR(32),
		contact_website VARCHAR(255),
		campaign_website_url VARCHAR(255),
		campaign_facebook_url VARCHAR(255)
	)
''')
conn.commit()

insert_sql = '''
	INSERT INTO election_candidates (
		ocd_id,
		state,
		name,
		first_name,
		last_name,
		ballotpedia_url,
		candidates_id,
		person_id,
		party,
		race_id,
		office_name,
		office_level,
		district_type,
		is_incumbent,
		primary_date,
		primary_status,
		primary_runoff_date,
		primary_runoff_status,
		general_date,
		general_status,
		contact_website,
		campaign_website_url,
		campaign_facebook_url
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

def valid_date(date_str):
	if date_str == "":
		return None
	else:
		return date_str

def valid_bool(bool_str):
	if bool_str == "Yes":
		return True
	elif bool_str == "No":
		return False
	else:
		return None

files = []

source_dir = "%s/sources/ballotpedia" % root_dir
path = "%s/ballotpedia_candidates.csv" % source_dir
csvfile = open(path, 'rb')

reader = csv.reader(csvfile)

row_num = 0
headers = []

def csv_row(row, headers):
	col_num = 0
	row_obj = {}
	for key in headers:
		row_obj[key] = row[col_num]
		col_num = col_num + 1
	return row_obj

for row in reader:
	if row_num == 0:
		headers = row
	else:
		row = csv_row(row, headers)

		level = row['office_level'].lower()
		state = row['state'].lower()

		# Only show Federal-level candidates and State candidates from a list of
		# approved states. Note that special elections seem not to have OCD IDs
		# associated with them. (20181018/dphiffer)
		if level == 'federal' or (level == 'state' and state in state_filter):

			print("%s: %s (%s)" % (row['ocdid'], row['name'], row['office_name']))

			values = (
				row['ocdid'].lower(),
				state,
				row['name'],
				row['first_name'],
				row['last_name'],
				row['url'], # ballotpedia_url
				int(row['candidates_id']),
				int(row['person_id']),
				row['party'],
				int(row['race_id']),
				row['office_name'],
				level,
				row['district_type'],
				valid_bool(row['is_incumbent?']), # is_incumbent
				valid_date(row['primary']), # primary_date
				row['primary_status'],
				valid_date(row['primary_runoff']), # primary_runoff_date
				row['primary_runoff_status'],
				valid_date(row['general']), # general_date
				row['general_status'],
				row['contact_website'],
				row['campaign_website_url'],
				row['campaign_facebook_url']
			)

			cur.execute(insert_sql, values)

	row_num = row_num + 1
conn.commit()
