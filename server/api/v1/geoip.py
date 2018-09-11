import os, requests, urllib
import maxminddb

api_key = os.getenv('IPSTACK_API_KEY', None)

def get_coords(ip):

	global api_key

	if api_key:
		return get_ipstack_coords(ip)
	else:
		return get_maxmind_coords(ip)

def get_ipstack_coords(ip):

	global api_key
	print(api_key)

	try:
		base_url = "http://api.ipstack.com"
		path = "/%s" % urllib.quote_plus(ip)
		url = "%s%s?access_key=%s" % (base_url, path, api_key)
		rsp = requests.get(url).json()
		return {
			'ok': True,
			'source': 'ipstack',
			'ip': ip,
			'lat': rsp['latitude'],
			'lng': rsp['longitude']
		}
	except:
		return {
			'ok': False,
			'error': 'Unable to lookup IP address with ipstack.'
		}

def get_maxmind_coords(ip):

	try:
		# yeah, this is hardcoded and probably shouldn't be
		root_dir = "/usr/local/aclu/elections-api"
		db_path = '%s/sources/maxmind/geolite2_city.mmdb' % root_dir
		reader = maxminddb.open_database(db_path)
		rsp = reader.get(ip)
		return {
			'ok': True,
			'source': 'maxmind',
			'ip': ip,
			'lat': rsp['location']['latitude'],
			'lng': rsp['location']['longitude']
		}
	except:
		return {
			'ok': False,
			'error': 'Unable to lookup IP address with maxmind.'
		}
