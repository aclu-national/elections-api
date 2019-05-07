# !/usr/bin/env python

import server
import pytest

# @pytest.fixture
# def app():
# 	app = server.app
# 	return app

@pytest.fixture
def client():
	# http://flask.pocoo.org/docs/1.0/api/
	app = server.app
	app.testing = True
	client = app.test_client()
	return client