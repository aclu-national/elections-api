all: congress_sessions \
     congress_districts \
     congress_legislators \
     congress_photos \
     states \
     counties \
     state_leg

congress_sessions:
	mkdir -p congress_sessions
	curl -o congress_sessions/congress_sessions.html https://www.senate.gov/reference/Sessions/sessionDates.htm

congress_districts: congress_districts_115 \
                    congress_districts_116_pa

congress_districts_115:
	mkdir -p congress_districts_115
	curl -o congress_districts_115/congress_districts_115_lookup.zip https://www2.census.gov/geo/tiger/TIGER2017/CD/tl_2017_us_cd115.zip
	unzip -d congress_districts_115 congress_districts_115/congress_districts_115_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 congress_districts_115/congress_districts_115_lookup.geojson congress_districts_115/tl_2017_us_cd115.shp
	curl -o congress_districts_115/congress_districts_115_display.zip https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_cd115_500k.zip
	unzip -d congress_districts_115 congress_districts_115/congress_districts_115_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 congress_districts_115/congress_districts_115_display.geojson congress_districts_115/cb_2017_us_cd115_500k.shp

congress_districts_116_pa:
	mkdir -p congress_districts_116_pa
	curl -o congress_districts_116_pa/congress_districts_116_pa.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d congress_districts_116_pa congress_districts_116_pa/congress_districts_116_pa.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 congress_districts_116_pa/congress_districts_116_pa.geojson congress_districts_116_pa/Remedial\ Plan\ Shapefile.shp

congress_legislators:
	mkdir -p congress_legislators
	curl -o congress_legislators/legislators-current.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml
	curl -o congress_legislators/legislators-social-media.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-social-media.yaml

congress_photos:
	mkdir -p congress_photos
	python ../scripts/source_congress_photos_bioguide.py
	python ../scripts/source_congress_photos_wikipedia.py

states:
	mkdir -p states
	curl -o states/states_lookup.zip https://www2.census.gov/geo/tiger/TIGER2017/STATE/tl_2017_us_state.zip
	unzip -d states states/states_lookup.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 states/states_lookup.geojson states/tl_2017_us_state.shp
	curl -o states/states_display.zip https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_state_500k.zip
	unzip -d states states/states_display.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 states/states_display.geojson states/cb_2017_us_state_500k.shp

counties:
	mkdir -p counties
	curl -o counties/counties.zip https://www2.census.gov/geo/tiger/TIGER2017/COUNTY/tl_2017_us_county.zip
	unzip -d counties counties/counties.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 counties/counties.geojson counties/tl_2017_us_county.shp

state_leg:
	mkdir -p state_leg
	../scripts/source_state_leg.sh

maxmind:
	mkdir -p maxmind
	curl -o maxmind/GeoLite2-City.tar.gz http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
	tar xf maxmind/GeoLite2-City.tar.gz -C maxmind
	mv maxmind/GeoLite2-City_*/GeoLite2-City.mmdb maxmind/geolite2_city.mmdb
