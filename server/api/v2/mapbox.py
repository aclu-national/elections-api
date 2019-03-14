import os, requests, urllib, traceback

api_key = os.getenv('MAPBOX_API_KEY', None)

def geocode(address, near_lat=None, near_lng=None):

	base_url = "https://api.mapbox.com"
	query = "%s.json" % urllib.quote_plus(address.encode("utf-8"))
	endpoint = "/geocoding/v5/mapbox.places/%s" % query

	url = "%s%s?access_token=%s" % (base_url, endpoint, api_key)

	if near_lat and near_lng:
		proximity = urllib.quote_plus("%r,%r" % (near_lng, near_lat))
		url += "&proximity=%s" % proximity

	url += "&country=us"

	rsp = requests.get(url)

	if rsp.status_code != 200:
		return None

	try:
		rsp = rsp.json()
		return {
			'lat': rsp['features'][0]['center'][1],
			'lng': rsp['features'][0]['center'][0]
		}
	except:
		print("ERROR could not geocode %s" % address)
		print(traceback.format_exc())
		return None
