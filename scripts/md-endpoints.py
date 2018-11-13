#!/bin/env python

import requests

url = "https://elections.api.aclu.org/v1"
rsp = requests.get(url).json()

for path in rsp['valid_endpoints']:

	endpoint = rsp['valid_endpoints'][path]
	description = endpoint['description']

	print("* `%s`  \n  *%s*  \n  Arguments:  " % (path, description))

	for arg in endpoint['args']:
		print("    - `%s`: %s" % (arg, endpoint['args'][arg]))
