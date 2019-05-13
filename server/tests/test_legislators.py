#!/usr/bin/env python

import pytest

# ---------------
# Legislator data test setup
# ---------------

V1_ENDPOINTS = [
	('/v1/congress/legislators', 539)
]

V2_ENDPOINTS = [
	('/v2/congress/legislators', 537),
	('/v2/congress/legislators?session=115', 539),
	('/v2/congress/legislators?session=116', 537)
	# ('/v2/congress/legislators?session=all', 634)
]

V1_FIELDS = [
	'aclu_id', 
	'id', 
	'name', 
	'photo', 
	'url_slug',

	# non-required? fields:
	'bio',
	'contact',
	'running_for_president',
	'running_in_2018',
	'social',
	'term'
]

V2_FIELDS = [
	'id', 
	'name', 
	'photo', 
	'url_slug',

	# non-required? fields:
	'bio',
	'contact',
	'score_sessions',
	'sessions',
	'social',
	'term'
]


# ---------------
# Legislator data tests
# ---------------

@pytest.mark.parametrize('endpoint',V1_ENDPOINTS+V2_ENDPOINTS)
def test_nonzero_legislator_count(endpoint, client):
	"""
	Asserts the expected number of legislators returned by each endpoint
	"""
	response = client.get(endpoint[0])
	json_data = response.get_json()
	assert (len(json_data['congress_legislators']) == endpoint[1])


@pytest.mark.parametrize('endpoint', V1_ENDPOINTS)
def test_v1_legislators_have_required_fields(endpoint, client):
	"""
	Assert that all legislators returned by a given v1 endpoint have required fields
	"""
	assert legislators_have_required_fields(endpoint[0], V1_FIELDS, client)


@pytest.mark.parametrize('endpoint', V2_ENDPOINTS)
def test_v2_legislators_have_required_fields(endpoint, client):
	"""
	Assert that all legislators returned by a given v2 endpoint have required fields
	"""
	assert legislators_have_required_fields(endpoint[0], V2_FIELDS, client)


# ---------------
# Helpers
# ---------------

def legislators_have_required_fields(endpoint, fields, client):
	"""
	Checks that all legislators in a given endpoint have all specified fields
	Raises AssertionError containing any legislators missing a field
	"""
	response = client.get(endpoint)
	json_data = response.get_json()
	legislators = json_data['congress_legislators']

	# Check each legislator for each field
	incomplete_legislators = []
	for legislator in legislators:
		for field in fields:
			if field not in legislator:
				incomplete_legislators.append((legislator, field))

	if len(incomplete_legislators) != 0:
		error_message = "\n----------------\n"
		error_message += "Endpoint %s" % (endpoint)
		error_message += "\n----------------\n"
		error_message += "\t"
		error_message += '\n\t'.join(map(lambda x: format_legislator_error(x[0], x[1]), incomplete_legislators))
		raise AssertionError(error_message)
	else:
		return True

def format_legislator_error(legislator, field):
	# Todo: raise an exception if the legislator doesn't have a full name ?
	return "Missing '%s': %s" % (field, legislator['name']['full_name'])


