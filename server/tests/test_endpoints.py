#!/usr/bin/env python

# from flask import request, jsonify
import pytest
import json

# ---------------
# Top-level endpoints(?)
# ---------------

def test_endpoint(client):
	"""
	Test '/' route. is there a better name for this function
	"""
	res = client.get('/')
	json_data = res.get_json()
	assert json_data['ok'] == False

def test_v1(client):
	"""
	Test '/v1/' route
	"""
	res = client.get('/v1/')
	json_data = res.get_json()
	assert json_data['ok'] == False

def test_v2(client):
	"""
	Test '/v2/' route
	"""
	res = client.get('/v2/')
	json_data = res.get_json()
	assert json_data['ok'] == False

# ---------------
# V1 Endpoints
# ---------------

def test_v1_pip(client):
	"""
	Test '/v1/pip' route without data
	"""
	res = client.get('/v1/pip')
	json_data = res.get_json()
	assert json_data['ok'] == False

def test_v1_congress_legislators(client):
	"""
	Test '/v1/congress/legislators' route
	"""
	res = client.get('/v1/congress/legislators')
	json_data = res.get_json()
	assert json_data['ok'] == True



