import re
import postgres_db

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS aclu_ids CASCADE")
cur.execute('''
CREATE TABLE aclu_ids (
	id INTEGER PRIMARY KEY,
	aclu_id VARCHAR(255),
	type VARCHAR(255)
)''')

conn.commit()

insert_sql = '''
	INSERT INTO aclu_ids (
		id,
		aclu_id,
		type
	) VALUES (%s, %s, %s)
'''

types = {
	'congress_districts': 'congress_district',
	'congress_legislators': 'congress_legislator',
	'counties': 'county',
	'state_leg': 'state_leg',
	'states': 'state'
}

for table in types:

	cur.execute('''
		SELECT aclu_id
		FROM {table}
	'''.format(table=table))

	rs = cur.fetchall()
	if rs:
		for row in rs:
			aclu_id = row[0]

			print(aclu_id)

			id = re.search('\d+$', aclu_id).group(0)
			id = int(id)
			type = types[table]

			cur.execute(insert_sql, (id, aclu_id, type))

conn.commit()
print('Done')
