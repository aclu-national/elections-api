#/bin/env python

import os, re, sys, yaml, urllib2

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

source_path = "%s/sources/congress_legislators/legislators-current.yaml" % root_dir
print("Loading %s" % source_path)
file = open(source_path, "r")
data = yaml.load(file)

exists = 0
not_exists = 0

for legislator in data:

	bioguide = legislator["id"]["bioguide"]
	path = 'congress_photos/%s.jpg' % bioguide
	abs_path = '/usr/local/aclu/elections-api/sources/%s' % path

	fname = legislator["name"]["first"]
	lname = legislator["name"]["last"]

	if os.path.isfile(abs_path):
		continue

	if not 'wikipedia' in legislator["id"]:
		print("no wikipedia article for %s %s (%s)" % (fname, lname, bioguide))
		print("   maybe check for it here? https://en.wikipedia.org/wiki/%s_%s" % (fname, lname))
		continue

	wikipedia_slug = legislator["id"]["wikipedia"].replace(' ', '_')
	wikipedia_slug = urllib2.quote(wikipedia_slug.encode('utf-8'))
	wikipedia_url = 'https://en.wikipedia.org/wiki/%s' % wikipedia_slug

	print("Downloading %s" % path)

	cmd = "/usr/bin/curl -s '%s' | /usr/local/bin/pup '.infobox img attr{src}'" % wikipedia_url
	image_url = os.popen(cmd).read()
	image_url = image_url.split('\n')[0]
	image_url = 'https:' + image_url.strip()

	os.popen("/usr/bin/curl --fail -s -o %s '%s'" % (abs_path, image_url))

print("Done")
