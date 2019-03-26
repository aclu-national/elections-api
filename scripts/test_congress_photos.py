import os, re, sys

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

for f in os.listdir('%s/sources/congress_photos' % root_dir):
	path = '%s/sources/congress_photos/%s' % (root_dir, f)
	if os.path.isfile(path):
		if re.search('\.jpg$', path):
			cmd = 'identify %s | cut -d " " -f 3 | cut -d "x" -f 1' % path
			width = int(os.popen(cmd).read())
			if width < 175:
				print("%s is only %d pixels wide" % (f, width))
