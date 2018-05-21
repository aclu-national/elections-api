#!/bin/env python

import psycopg2, os, re, sys, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS legislators CASCADE")
cur.execute('''
	CREATE TABLE legislators (
		bioguide VARCHAR(10) PRIMARY KEY,
		first_name VARCHAR(255),
		last_name VARCHAR(255),
		full_name VARCHAR(255),
		birthday DATE,
		gender VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_concordances CASCADE")
cur.execute('''
	CREATE TABLE legislator_concordances (
		bioguide VARCHAR(10),
		concordance_name VARCHAR(255),
		concordance_value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_terms CASCADE")
cur.execute('''
	CREATE TABLE legislator_terms (
		id SERIAL PRIMARY KEY,
		bioguide VARCHAR(10),
		type VARCHAR(16),
		state CHAR(2),
		district_num INTEGER,
		start_date DATE,
		end_date DATE,
		party VARCHAR(32)
	)
''')
cur.execute('''
	CREATE INDEX legislator_term_lookup_idx ON legislator_terms (
		bioguide,
		state,
		district_num,
		end_date
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_term_details CASCADE")
cur.execute('''
	CREATE TABLE legislator_term_details (
		term_id INTEGER,
		bioguide VARCHAR(10),
		detail_name VARCHAR(255),
		detail_value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_social_media CASCADE")
cur.execute('''
	CREATE TABLE legislator_social_media (
		bioguide VARCHAR(10),
		social_media_name VARCHAR(255),
		social_media_value VARCHAR(255)
	)
''')

conn.commit()

legislator_insert_sql = '''
	INSERT INTO legislators (
		bioguide,
		first_name,
		last_name,
		full_name
	) VALUES (%s, %s, %s, %s)
'''

concordances_insert_sql = '''
	INSERT INTO legislator_concordances (
		bioguide,
		concordance_name,
		concordance_value
	) VALUES (%s, %s, %s)
'''

terms_insert_sql = '''
	INSERT INTO legislator_terms (
		{columns}
	) VALUES ({placeholders}) RETURNING id
'''

details_insert_sql = '''
	INSERT INTO legislator_term_details (
		term_id,
		bioguide,
		detail_name,
		detail_value
	) VALUES (%s, %s, %s, %s)
'''

social_media_insert_sql = '''
	INSERT INTO legislator_social_media (
		bioguide,
		social_media_name,
		social_media_value
	) VALUES (%s, %s, %s)
'''

dir = "%s/data/legislators" % root_dir

files = []
for filename in os.listdir(dir):
	if not filename.endswith(".json"):
		continue
	files.append(filename)

files.sort()
for filename in files:

	cur = conn.cursor()

	bioguide = filename.replace(".json", "")
	path = "%s/data/legislators/%s" % (root_dir, filename)

	print("Loading %s" % path)

	file = open(path, "r")
	legislator = json.load(file)

	values = [
		bioguide,
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

	print("Indexing %s: %s" % (bioguide, values[3]))

	values = tuple(values)
	cur.execute(legislator_insert_sql, values)

	if "bio" in legislator and "birthday" in legislator["bio"]:
		cur.execute('''
			UPDATE legislators
			SET birthday = %s
			WHERE bioguide = %s
		''', (legislator["bio"]["birthday"], bioguide))

	if "bio" in legislator and "gender" in legislator["bio"]:
		cur.execute('''
			UPDATE legislators
			SET gender = %s
			WHERE bioguide = %s
		''', (legislator["bio"]["gender"], bioguide))

	for key, value in legislator["id"].iteritems():

		if isinstance(value, list):
			value = ",".join(value)

		values = (
			bioguide,
			key,
			value
		)
		cur.execute(concordances_insert_sql, values)
		#print("\t%s = %s" % (key, value))

	for term in legislator["terms"]:

		columns = ["bioguide"]
		values = [bioguide]
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
			values = [term_id, bioguide] + detail
			cur.execute(details_insert_sql, values)

	if "social" in legislator:
		for key in legislator["social"]:
			values = [bioguide, key, legislator["social"][key]]
			cur.execute(social_media_insert_sql, values)

	conn.commit()

conn.close()
print("Done")
