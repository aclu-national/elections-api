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

if __name__ == '__main__':
	port = os.getenv('PORT', 5000)
	port = int(port)
	app.run(host='0.0.0.0', port=port)
