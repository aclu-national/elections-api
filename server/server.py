#!/usr/bin/env python

import flask, flask_cors, json, os, psycopg2, re, sys, arrow
from api.v1 import api as api_v1

app = flask.Flask(__name__)
flask_cors.CORS(app)
app.register_blueprint(api_v1, url_prefix='/v1')

@app.before_request
def init():
	default_dsn = 'dbname=elections'
	db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
	flask.g.db = psycopg2.connect(db_dsn)

@app.route('/')
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
