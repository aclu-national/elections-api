import os, hashlib
from subprocess import call

mapbox_api_key = os.getenv('MAPBOX_API_KEY', None)

def get_pass(address, hours, lat, lng):

	hash = hashlib.sha1(address).hexdigest()

	base_dir = "/usr/local/aclu/voter-apple-wallet"
	path = "%s/passes/%s/pass.pkpass" % (base_dir, hash)

	if not os.path.isfile(path):
		cmd = ["/usr/local/aclu/voter-apple-wallet/pkpass.sh", address, hours, lat, lng]
		call(cmd, env={"MAPBOX_API_KEY": mapbox_api_key})

	return path
