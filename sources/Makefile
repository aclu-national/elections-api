all: districts_113 districts_116_pa legislators states counties

districts_113:
	mkdir -p districts_113
	curl -o districts_113/districts_113.zip https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d districts_113 districts_113/districts_113.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 districts_113/districts_113.geojson districts_113/tl_rd13_us_cd113.shp

districts_116_pa:
	mkdir -p districts_116_pa
	curl -o districts_116_pa/districts_116_pa.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d districts_116_pa districts_116_pa/districts_116_pa.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 districts_116_pa/districts_116_pa.geojson districts_116_pa/Remedial\ Plan\ Shapefile.shp

legislators:
	mkdir -p legislators
	curl -o legislators/legislators-current.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-current.yaml
	curl -o legislators/legislators-social-media.yaml https://raw.githubusercontent.com/unitedstates/congress-legislators/master/legislators-social-media.yaml

states:
	mkdir -p states
	curl -o states/states.zip http://www2.census.gov/geo/tiger/2017/STATE/tl_2017_us_state.zip
	unzip -d states states/states.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 states/states.geojson states/tl_2017_us_state.shp

counties:
	mkdir -p counties
	curl -o counties/counties.zip http://www2.census.gov/geo/tiger/2017/COUNTY/tl_2017_us_county.zip
	unzip -d counties counties/counties.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 counties/counties.geojson counties/tl_2017_us_county.shp
