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

	google_api_key = os.getenv('GOOGLE_API_KEY', None)
	if not google_api_key:
		print("Please define GOOGLE_API_KEY environment var")
		exit(1)

	mapbox_api_key = os.getenv('MAPBOX_API_KEY', None)
	if not mapbox_api_key:
		print("Please define MAPBOX_API_KEY environment var")
		exit(1)

	app.run(host='0.0.0.0', port=port)
