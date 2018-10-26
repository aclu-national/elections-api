import os, requests, urllib

api_key = os.getenv('MAPBOX_API_KEY', None)

def geocode(address, near_lat=None, near_lng=None):

	global api_key

	base_url = "https://api.mapbox.com"
	query = "%s.json" % urllib.quote_plus(address.encode("utf-8"))
	endpoint = "/geocoding/v5/mapbox.places/%s" % query

	url = "%s%s?access_token=%s" % (base_url, endpoint, api_key)

	if near_lat and near_lng:
		proximity = urllib.quote_plus("%r,%r" % (near_lng, near_lat))
		url += "&proximity=%s" % proximity

	url += "&country=us"

	rsp = requests.get(url)
	print("geocoded: (%d) %s" % (rsp.status_code, url))

	if rsp.status_code == 200:
		return rsp.json()
	else:
		print("ERROR could not geocode %s" % address)
		print(rsp.text)
		return None
