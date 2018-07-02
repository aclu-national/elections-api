#!/usr/bin/env python

import flask, flask_cors, json, os, psycopg2, re, sys, arrow
from api.v1 import api as api_v1

app = flask.Flask(__name__)
flask_cors.CORS(app)
app.register_blueprint(api_v1, url_prefix='/v1')

@app.before_request
def init():
	db_connect()
	setup_sessions()
	setup_targeted()
	setup_blurbs()

def db_connect():
	default_dsn = 'dbname=elections'
	db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
	flask.g.db = psycopg2.connect(db_dsn)

def setup_sessions():
	flask.g.sessions = {}
	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, start_date, end_date
		FROM congress_sessions
		ORDER BY id DESC
	''')

	rs = cur.fetchall()
	results = []
	if rs:
		for row in rs:
			id = row[0]
			flask.g.sessions[id] = {
				"start_date": str(row[1]),
				"end_date": str(row[2])
			}

def setup_targeted():
	flask.g.targeted = {
		'races': {},
		'initiatives': {}
	}
	cur = flask.g.db.cursor()

	cur.execute('''
		SELECT ocd_id, office, summary, url
		FROM election_targeted_races
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			ocd_id = row[0]

			if not ocd_id in flask.g.targeted['races']:
				flask.g.targeted['races'][ocd_id] = []

			flask.g.targeted['races'][ocd_id].append({
				'office': row[1],
				'summary': row[2],
				'url': row[3]
			})

	cur.execute('''
		SELECT ocd_id, name, position, blurb, url
		FROM election_targeted_initiatives
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			ocd_id = row[0]

			if not ocd_id in flask.g.targeted['initiatives']:
				flask.g.targeted['initiatives'][ocd_id] = []

			flask.g.targeted['initiatives'][ocd_id].append({
				'name': row[1],
				'position': row[2],
				'blurb': row[3],
				'url': row[4]
			})

def setup_blurbs():

	flask.g.blurbs = {}
	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT office, name, title, summary, details_title
		FROM election_blurbs
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			flask.g.blurbs[office] = {
				'name': row[1],
				'title': row[2],
				'summary': row[3],
				'details_title': row[4],
				'details': []
			}

	cur.execute('''
		SELECT office, detail
		FROM election_blurb_details
		ORDER BY office, detail_number
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			flask.g.blurbs[office]['details'].append(row[1])

	cur.execute('''
		SELECT office, search, replace
		FROM election_blurb_alt_names
	''')

	rs = cur.fetchall()
	if rs:
		for row in rs:
			office = row[0]
			search = row[1]
			replace = row[2]
			if not 'alt_names' in flask.g.blurbs[office]:
				flask.g.blurbs[office]['alt_names'] = {}
			flask.g.blurbs[office]['alt_names'][search] = replace

@app.route("/")
def index():
	return flask.jsonify({
		'ok': False,
		'error': 'Please use the /v1 endpoint.',
		'valid_endpoints': [
			'/v1/'
		]
	})

if __name__ == '__main__':
	port = os.getenv('PORT', 5000)
	port = int(port)
	app.run(host='0.0.0.0', port=port)
