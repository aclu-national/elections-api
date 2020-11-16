#/bin/env python

import os, re, sys, yaml, urllib2, json

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
	wikipedia_url = 'https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=pageimages&format=json&formatversion=2&pithumbsize=500' % wikipedia_slug

	print("Downloading %s" % wikipedia_url)

	response = urllib2.urlopen(wikipedia_url)
	data = json.loads(response.read())
	page = data['query']['pages'][0]

	if not 'thumbnail' in page: 
		print("No image available")
	else: 
		image_url = page['thumbnail']['source']
		print("Downloading image %s" % image_url)
		os.popen("/usr/bin/curl --fail -s -o %s '%s'" % (abs_path, image_url))

print("Done")
