#!/usr/bin/env python

import postgres_db, optparse, sys, os, json, us
import unicodecsv as csv

if __name__ == "__main__":

	if len(sys.argv) < 2:
		print("Usage: python polling_place_addresses.py [file.csv]")
		exit(1)

	path = sys.argv[1]
	file = open(path, 'rb')
	reader = csv.reader(file)

	header = None
	skipped = 0
	imported = 0

	conn = postgres_db.connect()
	cur = conn.cursor()

	cur.execute('''
		CREATE TABLE IF NOT EXISTS addresses (
			id SERIAL PRIMARY KEY,
			filename VARCHAR(255),
			row_num INTEGER,
			address VARCHAR(255),
			state CHAR(2),
			status VARCHAR(255) DEFAULT 'pending',
			created TIMESTAMP,
			updated TIMESTAMP
		)
	''')

	cur.execute('''
		CREATE TABLE IF NOT EXISTS google_civic_voter_info (
			id SERIAL PRIMARY KEY,
			address_id INTEGER,
			response_code INTEGER,
			response TEXT,
			num_polling_locations INTEGER,
			num_drop_off_locations INTEGER,
			num_early_vote_sites INTEGER,
			updated TIMESTAMP
		)
	''')
	conn.commit()

	filename = os.path.basename(path)

	address_sql = '''
		INSERT INTO addresses
		(filename, row_num, address, state, created, updated)
		VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
	'''

	row_num = 0

	for row in reader:
		row_num += 1

		if row_num % 10000 == 0:
			print "imported %d" % row_num
			conn.commit()

		if row_num == 1:
			header = row
			continue

		country = row[6]
		if country != 'US' and country != 'United States' and country != '':
			#print("Could not parse country %s" % country)
			skipped += 1
			continue

		street = row[2].split("\n")
		street = street[0]

		if street == "":
			continue

		city = row[3]

		try:
			state = row[4]
			if state == '':
				continue

			state_obj = us.states.lookup(unicode(state))
			state = state_obj.abbr

		except:
			#print("Could not parse state %s" % row[4])
			skipped += 1
			continue

		state = state.lower()

		zip = row[5]
		if len(zip) > 5:
			zip = zip[:5]

		try:
			address = "%s, %s, %s %s" % (street, city, state.upper(), zip)
		except:
			print("Could not interpolate:")
			print(row)
			skipped += 1
			continue

		try:
			values = (filename, row_num, address, state)
			cur.execute(address_sql, values)
			imported += 1
		except:
			skipped += 1

	conn.commit()
	print("%d imported" % imported)
	print("%d skipped" % skipped)
