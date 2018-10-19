import os, hashlib
from subprocess import call

def get_pass(address, hours, lat, lng):

	hash = hashlib.sha1(address).hexdigest()

	base_dir = "/usr/local/aclu/voter-apple-wallet"
	path = "%s/passes/%s/pass.pkpass" % (base_dir, hash)

	if not os.path.isfile(path):

		cmd = ["/usr/local/aclu/voter-apple-wallet/pkpass.sh", address, hours, lat, lng]

		print(" ".join(cmd))

		call(cmd)

	return path
