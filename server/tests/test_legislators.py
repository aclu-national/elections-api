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

# List of endpoints and associated counts
def endpoints_and_counts():
    return map(lambda x : (x['endpoint'], x['legislator_count']), ENDPOINTS)

# List of v2 endpoints
def v2_endpoints():
    return map(lambda x : x['endpoint'], filter(lambda x : x['version'] == 'v2', ENDPOINTS))

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
def test_legislator_bio(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'bio' field
    """
    # Required fields
    assert legislators_have_field(['bio'], endpoint, client, required=True)

    # Optional fields
    assert legislators_have_field(['bio', 'birthday'], endpoint, client, required=False)
    assert legislators_have_field(['bio', 'gender'], endpoint, client, required=False)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_contact(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'contact' field
    """
    # Required fields
    assert legislators_have_field(['contact'], endpoint, client, required=True)

    # Optional fields
    assert legislators_have_field(['contact', 'contact_form'], endpoint, client, required=False)
    assert legislators_have_field(['contact', 'fax'], endpoint, client, required=False)
    assert legislators_have_field(['contact', 'office'], endpoint, client, required=False)
    assert legislators_have_field(['contact', 'phone'], endpoint, client, required=False)
    assert legislators_have_field(['contact', 'rss_url'], endpoint, client, required=False)
    assert legislators_have_field(['contact', 'url'], endpoint, client, required=False)
        
@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_id(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'id' field
    """
    # Required fields
    assert legislators_have_field(['id'], endpoint, client, required=True)
    assert legislators_have_field(['id', 'aclu_id'], endpoint, client, required=True)

    # Optional fields
    assert legislators_have_field(['id', 'ballotpedia'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'bioguide'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'cspan'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'fec'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'url'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'google_entity_id'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'govtrack'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'icpsr'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'lis'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'maplight'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'opensecrets'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'thomas'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'votesmart'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'wikidata'], endpoint, client, required=False)
    assert legislators_have_field(['id', 'wikipedia'], endpoint, client, required=False)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_name(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'id' field
    """
    # Required fields
    assert legislators_have_field(['name'], endpoint, client, required=True)
    assert legislators_have_field(['name', 'first_name'], endpoint, client, required=True)
    assert legislators_have_field(['name', 'full_name'], endpoint, client, required=True)
    assert legislators_have_field(['name', 'last_name'], endpoint, client, required=True)

    # Optional fields
    assert legislators_have_field(['name', 'nickname'], endpoint, client, required=False)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_photo(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'id' field
    """
    assert legislators_have_field(['photo'], endpoint, client, required=True)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_sessions(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'score_sessions' and 'sessions' field
    """
    assert legislators_have_field(['score_sessions'], endpoint, client, required=True)
    assert legislators_have_field(['sessions'], endpoint, client, required=True)


@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_social(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'social' field
    """
    # Required
    assert legislators_have_field(['social'], endpoint, client, required=True)

    # Optional fields
    assert legislators_have_field(['social', 'facebook'], endpoint, client, required=False)
    assert legislators_have_field(['social', 'instagram'], endpoint, client, required=False)
    assert legislators_have_field(['social', 'twitter'], endpoint, client, required=False)
    assert legislators_have_field(['social', 'twitter_id'], endpoint, client, required=False)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_term(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'term' field
    """
    assert legislators_have_field(['term'], endpoint, client, required=True)
    assert legislators_have_field(['term','class'], endpoint, client, required=True)
    assert legislators_have_field(['term','end_date'], endpoint, client, required=True)
    assert legislators_have_field(['term','office'], endpoint, client, required=True)

@pytest.mark.parametrize('endpoint', v2_endpoints())
def test_legislator_url_slug(endpoint, client):
    """
    Assert that all v2 legislators have properly structured 'url_slug' field
    """
    assert legislators_have_field(['url_slug'], endpoint, client, required=True)
    

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

def legislators_have_field(field, endpoint, client, required):
    """
    Checks that all legislators in a given endpoint have the specified field.
    If the field is 'required', then raise an error for missing data; otherwise just a warning
    """
    response = client.get(endpoint)
    json_data = response.get_json()
    legislators = json_data['congress_legislators']

    # Check each legislator for field
    incomplete_legislators = []
    for legislator in legislators:
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


