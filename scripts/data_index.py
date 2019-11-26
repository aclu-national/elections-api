#!/usr/bin/env python

import os, sys, re
import unicodecsv as csv

index = None

def get_csv_path(repo):

	# NOTE: this assumes that everything is stored using a specific naming
	# convention: /usr/local/aclu/[repo]/data/data.csv (20180601/dphiffer)

	return "/usr/local/aclu/%s/data/data.csv" % repo

def get_index(repo):

	global index

	if index and repo in index:
		return index[repo]

	if not index:
		index = {}

	if not repo in index:
		index[repo] = {
			'count': 0,
			'lookup': {},
			'list': []
		}

	csv_path = get_csv_path(repo)

	if not os.path.isfile(csv_path):
		return index[repo]
	else:
		with open(csv_path, 'r', encoding='utf-8') as csv_file:
			reader = csv.reader(csv_file)
			row_num = 0
			for row in reader:
				if row_num == 0:
					header = row
				else:
					id = row[0]
					path = row[1]
					name = row[2]
					match = re.search(r"\d+$", id)
					if match:
						number = int(match.group(0))
						index['count'] = number
					index[repo]['lookup'][path] = row
					index[repo]['list'].append(row)
				row_num = row_num + 1
			index[repo]['count'] = row_num

	return index[repo]

def save_index(repo):

	csv_path = get_csv_path(repo)

	with open(csv_path, 'w', encoding='utf-8') as csv_file:
		writer = csv.writer(csv_file, delimiter=',', encoding='utf-8')
		headers = ['id', 'path', 'name']
		writer.writerow(headers)
		for line in index[repo]['list']:
			writer.writerow(line)
		csv_file.close()

def get_id(repo, type, path, name):

	index = get_index(repo)

	if path in index['lookup']:
		return index['lookup'][path][0]
	else:
		number = index['count']
		index['count'] = index['count'] + 1
		id = "aclu/%s/%s:%d" % (repo, type, number)
		record = [id, path, name]
		index['lookup'][path] = record
		index['list'].append(record)
		return id
