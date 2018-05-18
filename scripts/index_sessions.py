#!/bin/env python

import bs4, urllib3, certifi, arrow, psycopg2, os, re, sys
import postgres_db

curr_session = 115
curr_end_date = "2019-01-03"

next_session = 116
next_start_date = "2019-01-03"
next_end_date = "2021-01-03"

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS sessions")
cur.execute('''
	CREATE TABLE sessions (
		id INTEGER PRIMARY KEY,
		start_date DATE,
		end_date DATE
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO sessions (
		id,
		start_date,
		end_date
	) VALUES (%s, %s, %s)
'''

http = urllib3.PoolManager(
	cert_reqs='CERT_REQUIRED',
	ca_certs=certifi.where()
)
url = "https://www.senate.gov/reference/Sessions/sessionDates.htm"
req = http.request('GET', url)
soup = bs4.BeautifulSoup(req.data, "html.parser")

last_cell = None

for row in soup.find_all('tr'):
	cells = row.find_all('td')
	if len(list(cells)) < 4:
		continue

	for cell in cells:
		sup = cell.find('sup')
		if sup:
			sup.clear()

	label = cells[0].get_text().strip()
	if label:
		if last_cell:
			start_date = last_cell
			start_date = arrow.get(start_date, 'MMM D, YYYY').format('YYYY-MM-DD')
			print("%s: %s to %s" % (session, start_date, end_date))
			values = [
				int(session),
				start_date,
				end_date
			]
			cur.execute(insert_sql, values)

		session = label

		# Current session doesn't include an end date, weirdly
		if int(session) == curr_session:
			end_date = curr_end_date
		else:
			end_date = cells[3].get_text().strip()
			end_date = arrow.get(end_date, 'MMM D, YYYY').format('YYYY-MM-DD')

	last_cell = cells[2].get_text().strip()

start_date = last_cell
start_date = arrow.get(start_date, 'MMM D, YYYY').format('YYYY-MM-DD')
print("%s: %s to %s" % (session, start_date, end_date))

values = [
	int(session),
	start_date,
	end_date
]
cur.execute(insert_sql, values)

values = [
	next_session,
	next_start_date,
	next_end_date
]
cur.execute(insert_sql, values)

conn.commit()
conn.close()

print("Done")
