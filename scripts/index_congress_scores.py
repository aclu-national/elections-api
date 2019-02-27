#!/bin/env python

import psycopg2, os, re, sys, csv, arrow
import postgres_db
import unicodedata
import index_congress_details as congress_details

if len(sys.argv) < 2:
	sys.exit('Usage: %s [congress session]' % sys.argv[0])

session = int(sys.argv[1])

def strip_accents(s):
	s = s.decode('utf-8')
	return ''.join(c for c in unicodedata.normalize('NFD', s)
		if unicodedata.category(c) != 'Mn')

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS legislator_scores CASCADE")
cur.execute("DROP TABLE IF EXISTS congress_legislator_scores CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_scores (
		aclu_id VARCHAR(255),
		legislator_id VARCHAR(255),
		session INTEGER,
		position VARCHAR(255),
		name VARCHAR(512),
		value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS congress_legislator_score_index CASCADE")
cur.execute('''
	CREATE TABLE congress_legislator_score_index (
		aclu_id VARCHAR(255),
		session INTEGER,
		vote_context VARCHAR(255),
		roll_call INTEGER,
		vote_date DATE,
		vote_type VARCHAR(255),
		bill VARCHAR(255),
		amendment VARCHAR(255),
		title VARCHAR(512),
		bill_summary VARCHAR(512),
		description TEXT,
		committee VARCHAR(255),
		link VARCHAR(255)
	)
''')

legislator_score_insert_sql = '''
	INSERT INTO congress_legislator_scores (
		aclu_id,
		legislator_id,
		session,
		position,
		name,
		value
	) VALUES (%s, %s, %s, %s, %s, %s)
'''

legislator_score_index_insert_sql = '''
	INSERT INTO congress_legislator_score_index (
		aclu_id,
		session,
		vote_context,
		roll_call,
		vote_date,
		vote_type,
		bill,
		amendment,
		title,
		description,
		committee,
		link
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

reps = {}
sens = {}

cur.execute('''
	SELECT lt.aclu_id, lt.state, lt.district_num, lt.type, l.last_name
	FROM congress_legislator_terms AS lt,
	     congress_legislators AS l,
	     congress_sessions AS s
	WHERE s.id = 115
	  AND (
	  	lt.start_date >= s.start_date AND lt.end_date <= s.end_date
	  	OR lt.start_date <= s.start_date AND lt.end_date >= s.end_date
	  )
  AND lt.aclu_id = l.aclu_id
'''.format(session=session))

rs = cur.fetchall()
if rs:
	for row in rs:
		aclu_id = row[0]
		state = row[1].upper()
		district_num = row[2]
		type = row[3]
		if type == 'rep':
			if district_num == 0:
				district_num = 1
			if int(district_num) < 10:
				district_num = "0%s" % district_num
			else:
				district_num = str(district_num)
			state_district = "%s-%s" % (state, district_num)
			reps[state_district] = aclu_id
		else:
			if not state in sens:
				sens[state] = []

			found = False
			for rep in sens[state]:
				if rep['last_name'] == row[4]:
					found = True

			if not found:
				sens[state].append({
					'aclu_id': aclu_id,
					'last_name': row[4]
				})

# NOTE: there are two blocks of code here that look pretty similar, but vary
# a bit, so don't make the mistake of changing one and not the other.
# (20180613/dphiffer)

rep_scores_csv = '%s/elections-api-private/aclu/aclu_rep_scores_%d.csv' % (root_dir, session)
with open(rep_scores_csv, 'rb') as csvfile:

	reader = csv.reader(csvfile)

	row_num = 0
	headers = []
	bills = []
	aclu_position = []

	for row in reader:

		name = row.pop(0)
		state_district = row.pop(0)
		party = row.pop(0)
		total_score = row.pop(0)

		votes_total = 0
		votes_agreed = 0

		if name == 'LEGEND:':
			break

		if row_num == 0:
			headers = row
		elif row_num == 1:
			bills = row
		elif row_num == 2:
			aclu_position = row
		elif name != 'LEGEND:' and name != '' and name != 'Z-Vacant':

			print(name)

			if state_district in reps:
				col_num = 0

				legislator_id = reps[state_district]

				values = [
					'',
					legislator_id,
					session,
					'',
					'total',
					total_score
				]
				values = tuple(values)
				cur.execute(legislator_score_insert_sql, values)

				for col in row:

					if aclu_position[col_num] == 'ACLU Opposed':
						position = 'opposed'
					elif aclu_position[col_num] == 'ACLU Supported':
						position = 'supported'
					else:
						print('WARNING: unknown position for column num %s: %s' % (col_num, aclu_position[col_num]))
						position = 'unknown'

					score_num = headers[col_num]
					aclu_id = 'aclu/elections-api/rep_score:%s' % score_num
					name = bills[col_num]
					value = row[col_num]

					if value == '1' or value == '0':
						votes_total += 1
						if value == '1':
							votes_agreed += 1

					values = [
						aclu_id,
						legislator_id,
						session,
						position,
						name,
						value
					]
					values = tuple(values)
					cur.execute(legislator_score_insert_sql, values)
					col_num = col_num + 1

				congress_details.add_legislator_detail(legislator_id, session, 'votes_total', votes_total)
				congress_details.add_legislator_detail(legislator_id, session, 'votes_agreed', votes_agreed)

		row_num = row_num + 1

		conn.commit()

# NOTE: there are two blocks of code here that look pretty similar, but vary
# a bit, so don't make the mistake of changing one and not the other.
# (20180613/dphiffer)

sen_scores_csv = '%s/elections-api-private/aclu/aclu_sen_scores_%d.csv' % (root_dir, session)
with open(sen_scores_csv, 'rb') as csvfile:

	reader = csv.reader(csvfile)

	row_num = 0
	headers = []
	bills = []
	aclu_position = []

	for row in reader:

		name = row.pop(0)
		state = row.pop(0)
		party = row.pop(0)
		total_score = row.pop(0)

		votes_total = 0
		votes_agreed = 0

		if name == 'LEGEND:':
			break

		if row_num == 0:
			headers = row
		elif row_num == 1:
			bills = row
		elif row_num == 2:
			aclu_position = row
		elif name != 'LEGEND:' and name != '' and name != 'Z-Vacant':
			print name

			found = False
			for rep in sens[state]:
				lname = strip_accents(rep["last_name"])
				if name.find(lname) != -1:
					legislator_id = rep["aclu_id"]
					found = True

			if not found:
				print("COULD NOT FIND %s" % name)
				print(sens[state])
				continue

			values = [
				'',
				legislator_id,
				session,
				'',
				'total',
				total_score
			]
			values = tuple(values)
			cur.execute(legislator_score_insert_sql, values)

			col_num = 0
			for col in row:

				if aclu_position[col_num] == 'ACLU Opposed' or aclu_position[col_num] == 'ACLU ACLU Opposed':
					position = 'opposed'
				elif aclu_position[col_num] == 'ACLU Supported':
					position = 'supported'
				else:
					print('WARNING: unknown position for column num %s' % col_num)
					position = 'unknown'

				score_num = headers[col_num]
				aclu_id = 'aclu/elections-api/sen_score:%s' % score_num
				name = bills[col_num]
				value = row[col_num]

				if value == '1' or value == '0':
					votes_total += 1
					if value == '1':
						votes_agreed += 1

				values = [
					aclu_id,
					legislator_id,
					session,
					position,
					name,
					value
				]
				values = tuple(values)
				cur.execute(legislator_score_insert_sql, values)
				col_num = col_num + 1

			congress_details.add_legislator_detail(legislator_id, session, 'votes_total', votes_total)
			congress_details.add_legislator_detail(legislator_id, session, 'votes_agreed', votes_agreed)

		row_num = row_num + 1

		conn.commit()

for chamber in ['rep', 'sen']:

	filename = '%s/elections-api-private/aclu/aclu_%s_score_index_%d.csv' % (root_dir, chamber, session)
	with open(filename, 'rb') as csvfile:

		reader = csv.reader(csvfile)

		row_num = 0
		headers = []

		for row in reader:

			row_num = row_num + 1 # 1-indexed

			if row_num == 1:
				headers = row
				continue
			elif row[1] == 'FLOOR VOTES':
				vote_context = 'floor'
				continue
			elif row[1] == 'COMMITTEE VOTES':
				vote_context = 'committee'
				continue
			elif not re.search('^\d+$', row[0]):
				continue

			score_num = row[0]
			aclu_id = 'aclu/elections-api/%s_score:%s' % (chamber, score_num)

			if re.search('^\d+$', row[1]):
				roll_call = int(row[1])
			else:
				roll_call = None

			if re.match('\d*/\d*/\d{4}', row[2]):
				vote_date = arrow.get(row[2], 'M/D/YYYY').format('YYYY-MM-DD')
			elif re.match('\d*/\d*/\d{2}', row[2]):
				vote_date = arrow.get(row[2], 'M/D/YY').format('YYYY-MM-DD')
			else:
				print("WARNING: could not parse date")
				continue

			vote_type = row[3]
			bill = row[4]
			amendment = row[5]
			title = row[6]
			#bill_summary = row[7]
			description = row[7]
			committee = row[8]
			link = row[9]

			print(aclu_id)

			values = (
				aclu_id,
				session,
				vote_context,
				roll_call,
				vote_date,
				vote_type,
				bill,
				amendment,
				title,
				#bill_summary,
				description,
				committee,
				link
			)
			cur.execute(legislator_score_index_insert_sql, values)
			conn.commit()

conn.close()

print("Done")
