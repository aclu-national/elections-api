# !/usr/bin/env python

import server
import pytest
import os

# @pytest.fixture
# def app():
# 	app = server.app
# 	return app

@pytest.fixture
def client():

	# Not sure if this is the right place
	google_api_key = os.getenv('GOOGLE_API_KEY', None)
	if not google_api_key:
		print("Please define GOOGLE_API_KEY environment var")
		exit(1)
	mapbox_api_key = os.getenv('MAPBOX_API_KEY', None)
	if not mapbox_api_key:
		print("Please define MAPBOX_API_KEY environment var")
		exit(1)

	# http://flask.pocoo.org/docs/1.0/api/
	app = server.app
	app.testing = True
	client = app.test_client()
	return client