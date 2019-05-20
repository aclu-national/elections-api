#!/usr/bin/env python

import pytest

# ---------------
# Legislator data test setup
# ---------------

# Fields required for each legislator
V2_REQUIRED_FIELDS = [
    [ 'name', 'full_name' ],
    [ 'name', 'first_name' ],
    [ 'name', 'last_name' ], 
    [ 'id', 'aclu_id' ],
    [ 'term', 'start_date' ],
    [ 'term', 'end_date' ],
    [ 'term', 'state' ],
    [ 'photo' ], 
    [ 'url_slug' ],
]

# Each 'congress/legislators' endpoint 
ENDPOINTS = [
    {
        'version': 'v1',
        'endpoint': '/v1/congress/legislators',
        'legislator_count': 539,
        'required_fields': []
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators',
        'legislator_count': 537,
        'required_fields': V2_REQUIRED_FIELDS
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators?session=115',
        'legislator_count': 539,
        'required_fields': V2_REQUIRED_FIELDS
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators?session=116',
        'legislator_count': 537,
        'required_fields': V2_REQUIRED_FIELDS
    },
    # {
    #   'version': 'v2',
    #   'endpoint': '/v2/congress/legislators?session=all',
    #   'legislator_count': 537,
    #   'required_fields': V2_REQUIRED_FIELDS
    # }
]

# ---------------
# Legislator data tests
# ---------------

@pytest.mark.parametrize('endpoint',ENDPOINTS)
def test_legislator_count(endpoint, client):
	"""
	Asserts the expected number of legislators returned by each endpoint
	"""
	response = client.get(endpoint['endpoint'])
	json_data = response.get_json()
	assert (len(json_data['congress_legislators']) == endpoint['legislator_count'])

@pytest.mark.parametrize('endpoint', ENDPOINTS)
def test_required_fields(endpoint, client):
    """
    Assert that all legislators returned by an endpoint have required fields
    """
    assert legislators_have_required_fields(endpoint['endpoint'], endpoint['required_fields'], client)

# ---------------
# Helpers
# ---------------

def valid_json_keys(json_data, keys):
    """
    Checks that a sequence of keys exists in a json object
    """
    obj = json_data
    try:
        for key in keys:
            obj = obj[key]
    except Exception as e:
        return False
    return True

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
            if not valid_json_keys(legislator, field):
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


