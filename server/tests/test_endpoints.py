#!/usr/bin/env python

import pytest

# ---------------
# Ensure that we're returning json and HTTP status code 200 for each valid endpoint.
# ---------------

VALID_ENDPOINTS = [

	# Top-level(?) endpoints
	'/',
	'/v1/',
	'/v2/',

	# v1 endpoints
	'/v1/apple_wallet', 
	'/v1/calendar',
	'/v1/congress',
	'/v1/congress/district',
	'/v1/congress/legislators',
	'/v1/congress/scores',
	'/v1/county',
	'/v1/geoip', 
	'/v1/google_civic_info',
	'/v1/pip', 
	'/v1/state',
	'/v1/state_leg', 
	
	# v2 endpoints
	'/v2/apple_wallet', 
	'/v2/calendar',
	'/v2/congress',
	'/v2/congress/district',
	'/v2/congress/legislators',
	'/v2/congress/scores',
	'/v2/county',
	'/v2/geoip', 
	'/v2/google_civic_info',
	'/v2/pip', 
	'/v2/state',
	'/v2/state_leg'
]

@pytest.mark.parametrize('endpoint', VALID_ENDPOINTS)
def test_json_response(endpoint, client):
	"""
	Asserts that an endpoint returns a json response.
	This creates a test case for each endpoint in VALID_ENDPOINTS
	"""
	response = client.get(endpoint)
	json_data = response.get_json()
	assert (json_data != None), "Endpoint "+endpoint+" did not return json"


@pytest.mark.parametrize('endpoint', VALID_ENDPOINTS)
def test_status_code(endpoint, client):
	"""
	Asserts that an endpoint returns HTTP status code 200.
	This creates a test case for each endpoint in VALID_ENDPOINTS
	"""
	response = client.get(endpoint)
	json_data = response.get_json()
	assert (response.status_code == 200), "Expected status code 200, got "+response.status_code


