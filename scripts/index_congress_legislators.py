#!/bin/env python

import psycopg2, os, re, sys, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS legislators CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislators CASCADE")
cur.execute('''
	CREATE TABLE congress_legislators (
		aclu_id VARCHAR(255) PRIMARY KEY,
		url_slug VARCHAR(255) UNIQUE,
		first_name VARCHAR(255),
		last_name VARCHAR(255),
		full_name VARCHAR(255),
		nickname VARCHAR(255),
		birthday DATE,
		gender VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_concordances CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislator_concordances CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_concordances (
		aclu_id VARCHAR(255),
		concordance_name VARCHAR(255),
		concordance_value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_terms CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislator_terms CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_terms (
		id SERIAL PRIMARY KEY,
		aclu_id VARCHAR(255),
		type VARCHAR(16),
		state CHAR(2),
		district_num INTEGER,
		start_date DATE,
		end_date DATE,
		party VARCHAR(32)
	)
''')
cur.execute('''
	CREATE INDEX congress_legislator_term_lookup_idx ON congress_legislator_terms (
		aclu_id,
		state,
		district_num,
		end_date
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_term_details CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislator_term_details CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_term_details (
		term_id INTEGER,
		aclu_id VARCHAR(255),
		detail_name VARCHAR(255),
		detail_value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_social_media CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislator_social_media CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_social_media (
		aclu_id VARCHAR(255),
		social_media_name VARCHAR(255),
		social_media_value VARCHAR(255)
	)
''')

conn.commit()

legislator_insert_sql = '''
	INSERT INTO congress_legislators (
		aclu_id,
		url_slug,
		first_name,
		last_name,
		full_name,
		nickname
	) VALUES (%s, %s, %s, %s, %s, %s)
'''

concordances_insert_sql = '''
	INSERT INTO congress_legislator_concordances (
		aclu_id,
		concordance_name,
		concordance_value
	) VALUES (%s, %s, %s)
'''

terms_insert_sql = '''
	INSERT INTO congress_legislator_terms (
		{columns}
	) VALUES ({placeholders}) RETURNING id
'''

details_insert_sql = '''
	INSERT INTO congress_legislator_term_details (
		term_id,
		aclu_id,
		detail_name,
		detail_value
	) VALUES (%s, %s, %s, %s)
'''

social_media_insert_sql = '''
	INSERT INTO congress_legislator_social_media (
		aclu_id,
		social_media_name,
		social_media_value
	) VALUES (%s, %s, %s)
'''

dir = "%s/data/congress_legislators" % root_dir

state_dirs = []
for filename in os.listdir(dir):
	state_dirs.append("%s/%s" % (dir, filename))

files = []
for state_dir in state_dirs:
	for filename in os.listdir(state_dir):
		if not filename.endswith(".json"):
			continue
		files.append("%s/%s" % (state_dir, filename))

files.sort()

cur = conn.cursor()

for filename in files:

	print("Loading %s" % filename)
	file = open(filename, "r")
	legislator = json.load(file)

	aclu_id = legislator["id"]["aclu_id"]

	values = [
		aclu_id,
		legislator["url_slug"],
		legislator["name"]["first"],
		legislator["name"]["last"]
	]

	if "official_full" in legislator["name"]:
		values.append(legislator["name"]["official_full"])
	else:
		full_name = "%s %s" % (
			legislator["name"]["first"],
			legislator["name"]["last"]
		)
		values.append(full_name)

	if "nickname" in legislator["name"]:
		values.append(legislator["name"]["nickname"])
	else:
		values.append(None)

	values = tuple(values)
	cur.execute(legislator_insert_sql, values)

	if "bio" in legislator and "birthday" in legislator["bio"]:
		cur.execute('''
			UPDATE congress_legislators
			SET birthday = %s
			WHERE aclu_id = %s
		''', (legislator["bio"]["birthday"], aclu_id))

	if "bio" in legislator and "gender" in legislator["bio"]:
		cur.execute('''
			UPDATE congress_legislators
			SET gender = %s
			WHERE aclu_id = %s
		''', (legislator["bio"]["gender"], aclu_id))

	for key, value in legislator["id"].iteritems():

		if isinstance(value, list):
			value = ",".join(value)

		values = (
			aclu_id,
			key,
			value
		)
		cur.execute(concordances_insert_sql, values)
		#print("\t%s = %s" % (key, value))

	for term in legislator["terms"]:

		columns = ["aclu_id"]
		values = [aclu_id]
		placeholders = ["%s"]
		details = []

		for key, value in term.iteritems():
			if key in ["type", "state", "district", "start", "end", "party"]:

				if key == "start" or key == "end":
					key = "%s_date" % key
				elif key == "state":
					value = value.lower()
				elif key == "district":
					key = "district_num"
					if term['state'] in ['AS', 'DC', 'GU', 'MP', 'PR', 'VI']:
						value = 98

				columns.append(key)
				values.append(value)
				placeholders.append("%s")

				#print("\t%s = %s" % (key, value))
			else:
				if isinstance(value, list) or isinstance(value, dict):
					value = json.dumps(value)
				#print("\t%s = %s (detail)" % (key, value))
				details.append([key, value])

		columns = ", ".join(columns)
		placeholders = ", ".join(placeholders)
		values = tuple(values)

		sql = terms_insert_sql.format(columns=columns, placeholders=placeholders)

		cur.execute(sql, values)
		term_id = cur.fetchone()[0]

		for detail in details:
			values = [term_id, aclu_id] + detail
			cur.execute(details_insert_sql, values)

	if "social" in legislator:
		for key in legislator["social"]:
			values = [aclu_id, key, legislator["social"][key]]
			cur.execute(social_media_insert_sql, values)

	conn.commit()

conn.close()
print("Done")
