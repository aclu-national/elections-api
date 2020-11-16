#!/bin/env python

import bs4, arrow, psycopg2, os, re, sys
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

source_path = "%s/sources/congress_sessions/congress_sessions.html" % root_dir

if not os.path.exists(source_path):
	print("ERROR: You need to download the congress_sessions:")
	print("")
	print("    cd sources/")
	print("    make congress_sessions")
	sys.exit(0)

curr_session = 116
curr_end_date = "2021-01-03"

next_session = 117
next_start_date = "2021-01-03"
next_end_date = "2023-01-03"

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS sessions") # old table name
cur.execute("DROP TABLE IF EXISTS congress_sessions")
cur.execute('''
	CREATE TABLE congress_sessions (
		id INTEGER PRIMARY KEY,
		start_date DATE,
		end_date DATE
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO congress_sessions (
		id,
		start_date,
		end_date
	) VALUES (%s, %s, %s)
'''

print("%s: %s to %s" % (next_session, next_start_date, next_end_date))
values = [
	next_session,
	next_start_date,
	next_end_date
]
cur.execute(insert_sql, values)

with open(source_path) as source_file:
	soup = bs4.BeautifulSoup(source_file.read(), "html.parser")

last_cell = None

for row in soup.find_all('tr'):
	cells = row.find_all('td')
	if len(list(cells)) < 4:
		continue

	# Clear superscript
	for cell in cells:
		sup = cell.find('sup')
		if sup:
			sup.clear()

	session = cells[0].get_text().strip()
	num_sessions = len(list(cells[2].strings))

	# Get start date
	start_date = list(cells[2].strings)[num_sessions - 1].strip()
	start_date = arrow.get(start_date, 'MMM D, YYYY').format('YYYY-MM-DD')

	# Get end date; the current session doesn't include an end date
	if int(session) == curr_session:
		end_date = curr_end_date
	else:
		end_date = list(cells[3].strings)[0]
		end_date = arrow.get(end_date, 'MMM D, YYYY').format('YYYY-MM-DD')

	print("%s: %s to %s" % (session, start_date, end_date))

	# Insert in db
	values = [
		int(session),
		start_date,
		end_date
	]
	cur.execute(insert_sql, values)

conn.commit()
conn.close()

print("Done")
