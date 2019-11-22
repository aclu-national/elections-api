#!/bin/env python

import requests

url = "https://elections.api.aclu.org/v2"
rsp = requests.get(url).json()

for path in sorted(rsp['valid_endpoints']):

	endpoint = rsp['valid_endpoints'][path]
	description = endpoint['description']

	print("### `%s`\n\n*%s*" % (path, description))

	if endpoint['args']:
		print("\nArguments:")
		for arg in sorted(endpoint['args']):
			print("* `%s`: %s" % (arg, endpoint['args'][arg]))
	else:
		print("\nNo arguments.")

	print("")
