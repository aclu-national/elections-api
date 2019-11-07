#!/bin/env python

import psycopg2, os, re, sys, csv, arrow
import postgres_db
import unicodedata
import index_congress_details as congress_details

if len(sys.argv) < 2:
	sys.exit('Usage: %s [congress session]' % sys.argv[0])

session = int(sys.argv[1])

def strip_accents(s):
	s = s.replace("'", "")
	s = s.decode('utf-8')
	return ''.join(c for c in unicodedata.normalize('NFD', s)
		if unicodedata.category(c) != 'Mn')

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

if len(sys.argv) > 2 and sys.argv[2] == '--reset':
	print("resetting data tables")

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
			outcome VARCHAR(255),
			title VARCHAR(512),
			description TEXT,
			bill_summary VARCHAR(512),
			committee VARCHAR(255),
			link VARCHAR(255)
		)
	''')

else:
	print("using existing data tables")

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
		outcome,
		title,
		description,
		bill_summary,
		committee,
		link
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

if __name__ == "__main__":

	for chamber in ['rep', 'sen']:

		scores_csv = '%s/elections-api-private/aclu/aclu_%s_scores_%d.csv' % (root_dir, chamber, session)
		with open(scores_csv, 'rb') as csvfile:

			reader = csv.reader(csvfile)

			row_num = 0
			headers = []
			bills = []
			aclu_position = []

			for row in reader:

				# The reason to pop these values out of the row, is so we can assume all the data
				# left in 'row' is voting data
				first_name = row.pop(0)
				last_name = row.pop(0)
				legislator_id = row.pop(0)
				state_district = row.pop(0)
				party = row.pop(0)
				total_score = row.pop(0)

				if not re.search('^\d+%$', total_score):
					total_score = 'N/A'

				votes_total = 0
				votes_agreed = 0
				legislator_id = "aclu/elections-api/congress_legislator:%s" % legislator_id

				if first_name == 'LEGEND:':
					break

				if row_num == 0:
					headers = row
				elif row_num == 1:
					bills = row
				elif row_num == 2:
					aclu_position = row
				elif first_name != 'LEGEND:' and first_name != '' and first_name != 'Z-Vacant':
					print('%s %s' % (first_name, last_name))

					col_num = 0

					for col in row:

						score_num = headers[col_num]
						# If there isn't a number in the first row, then we should continue on
						if not re.search('^\d+$', score_num):
							col_num += 1
							continue

						if aclu_position[col_num] == 'ACLU Opposed':
							position = 'opposed'
						elif aclu_position[col_num] == 'ACLU Supported':
							position = 'supported'
						else:
							print('WARNING: unknown position for column num %s: %s' % (col_num, aclu_position[col_num]))
							position = 'unknown'

						aclu_id = 'aclu/us-congress-%d/%s_score:%s' % (session, chamber, score_num)
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
						col_num += 1

					congress_details.add_legislator_detail(legislator_id, session, 'votes_total', votes_total)
					congress_details.add_legislator_detail(legislator_id, session, 'votes_agreed', votes_agreed)
					congress_details.add_legislator_detail(legislator_id, session, 'total_score', total_score)

				row_num = row_num + 1

				conn.commit()

		# Gets data from index files
		filename = '%s/elections-api-private/aclu/aclu_%s_score_index_%d.csv' % (root_dir, chamber, session)
		with open(filename, 'rb') as csvfile:

			reader = csv.reader(csvfile)

			row_num = 0
			headers = []
			vote_context = 'floor'

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
				aclu_id = 'aclu/us-congress-%d/%s_score:%s' % (session, chamber, score_num)

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
				outcome = row[6]
				title = row[7]
				description = row[8]
				bill_summary = row[9]
				committee = row[10]
				link = row[11]

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
					outcome,
					title,
					description,
					bill_summary,
					committee,
					link
				)
				cur.execute(legislator_score_index_insert_sql, values)
				conn.commit()

	conn.close()

	print("Done")
