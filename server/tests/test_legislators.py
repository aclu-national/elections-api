#!/usr/bin/env python

import pytest
import warnings

# ---------------
# Test the congress/legislator json responses.
# ---------------

# Each 'congress/legislators' endpoint
ENDPOINTS = [
    {
        'version': 'v1',
        'endpoint': '/v1/congress/legislators',
        'legislator_count': 539
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators',
        'legislator_count': 537
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators?session=115',
        'legislator_count': 540 #why did this change?
    },
    {
        'version': 'v2',
        'endpoint': '/v2/congress/legislators?session=116',
        'legislator_count': 537
    },
    # {
    #   'version': 'v2',
    #   'endpoint': '/v2/congress/legislators?session=all',
    #   'legislator_count': 537
    # }
]

# Each field in 'congress/legislators' that we'd like to test
LEGISLATOR_FIELDS = [
    {
        'field': 'bio',
        'required': True,
        'required_subfields': [],
        'optional_subfields': ['birthday', 'gender']
    },
    {
        'field': 'contact',
        'required': True,
        'required_subfields': [],
        'optional_subfields': ['address', 'contact_form', 'fax', 'office', 'phone', 'rss_url', 'url']
    },
    {
        'field': 'id',
        'required': True,
        'required_subfields': ['aclu_id'],
        'optional_subfields': ['ballotpedia', 'bioguide', 'fec', 'google_entity_id', 'govtrack', 'icpsr', 'lis', 'maplight', 'opensecrets', 'thomas', 'votesmart', 'wikidata', 'wikipedia']
    },
    {
        'field': 'name',
        'required': True,
        'required_subfields': ['first_name', 'full_name', 'last_name'],
        'optional_subfields': ['nickname']
    },
    {
        'field': 'photo',
        'required': True,
        'required_subfields': [],
        'optional_subfields': []
    },
    {
        'field': 'score_sessions',
        'required': True,
        'required_subfields': [],
        'optional_subfields': []
    },
    {
        'field': 'sessions',
        'required': True,
        'required_subfields': [],
        'optional_subfields': []
    },
    {
        'field': 'social',
        'required': True,
        'required_subfields': [],
        'optional_subfields': ['facebook', 'instagram', 'twitter', 'twitter_id', 'youtube', 'youtube_id']
    },
    {
        'field': 'term',
        'required': True,
        'required_subfields': ['end_date', 'office', 'party', 'start_date', 'state', 'state_full'],
        'optional_subfields': ['class', 'state_rank']
    },
    {
        'field': 'url_slug',
        'required': True,
        'required_subfields': [],
        'optional_subfields': []
    }
]


# ---------------
# Helper functions to filter/format the above data for passing into tests
# ---------------

# List of endpoints and associated counts: [(endpoint, count), (endpoint2, count2)]
def endpoints_and_counts():
    return map(lambda x : (x['endpoint'], x['legislator_count']), ENDPOINTS)

# List of v2 endpoints: [endpoint, endpoint, endpont]
def v2_endpoints():
    return map(lambda x : x['endpoint'], filter(lambda x : x['version'] == 'v2', ENDPOINTS))

# List of all required top-level legislator fields to check: [[field], [field], [field]]
def all_required_fields():
    return map(lambda x: [x['field']], LEGISLATOR_FIELDS)

# List of all required legislator subfields to check: [[field, subfield], [field, subfield]]
def all_required_subfields():
    fields = []
    for field in LEGISLATOR_FIELDS:
        subfields = map(lambda x: [field['field'], x], field['required_subfields'])
        fields += subfields
    return fields

# List of all optional legislator subfields to check: [[field, subfield], [field, subfield]]
def all_optional_subfields():
    fields = []
    for field in LEGISLATOR_FIELDS:
        subfields = map(lambda x: [field['field'], x], field['optional_subfields'])
        fields += subfields
    return fields

# ---------------
# Test the congress/legislator json responses
# ---------------

@pytest.mark.parametrize('endpoint, count', endpoints_and_counts())
def test_legislator_count(endpoint, count, client):
	"""
	Asserts the expected number of legislators returned by each endpoint
	"""
	response = client.get(endpoint)
	json_data = response.get_json()
	assert (len(json_data['congress_legislators']) == count)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_fields(endpoint, client):
    """
    Asserts that all legislators in a given endpoint have all top-level fields
    """
    fields = all_required_fields()
    assert legislators_have_fields(fields, endpoint, client, required=True)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_required_subfields(endpoint, client):
    """
    Asserts that all legislators in a given endpoint have all required subfields
    """
    fields = all_required_subfields()
    assert legislators_have_fields(fields, endpoint, client, required=True)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_optional_subfields(endpoint, client):
    """
    Asserts that all legislators in a given endpoint have all optional subfields.
    Note: This will only throw up a warning if fields are missing.
    """
    fields = all_optional_subfields()
    assert legislators_have_fields(fields, endpoint, client, required=False)

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

def legislators_have_fields(fields, endpoint, client, required):
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
        if (required):
            raise AssertionError(error_message)
        else:
            warnings.warn(UserWarning(error_message.encode('utf-8')))
            return True
    else:
        return True

def format_legislator_error(legislator, field):
	# Todo: raise an exception if the legislator doesn't have a full name ?
	return "Missing '%s': %s" % (field, legislator['name']['full_name'])


