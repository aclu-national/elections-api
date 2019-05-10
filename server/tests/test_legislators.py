#!/usr/bin/env python

import pytest

# ---------------
# Legislator data test setup
# ---------------

V1_ENDPOINTS = [
	'/v1/congress/legislators'
]

V2_ENDPOINTS = [
	'/v2/congress/legislators',
	'/v2/congress/legislators?session=115',
	'/v2/congress/legislators?session=116'
]

V1_REQUIRED_FIELDS = [
	'aclu_id', 
	'id', 
	'name', 
	'photo', 
	'url_slug'

	# Other fields:
		# bio
		# contact
		# running_for_president
		# running_in_2018
		# social
		# term
]

V2_REQUIRED_FIELDS = [
	'id', 
	'name', 
	'photo', 
	'url_slug'

	# Other fields:
		# bio
		# contact
		# score_sessions
		# sessions
		# social
		# term
]

# ---------------
# Legislator data tests
# ---------------

@pytest.mark.parametrize('endpoint',V1_ENDPOINTS+V2_ENDPOINTS)
def test_nonzero_legislator_count(endpoint, client):
	"""
	Asserts a greater-than-zero number of legislators returned by each endpoint
	"""
	response = client.get(endpoint)
	json_data = response.get_json()
	assert (len(json_data['congress_legislators']) > 0)

