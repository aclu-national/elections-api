all: congress_113 congress_116_pa congress_legislators states counties state_leg ocd_ids

congress_113:
	mkdir -p congress_113
	curl -o congress_113/congress_113.zip https://www2.census.gov/geo/tiger/TIGERrd13_st/nation/tl_rd13_us_cd113.zip
	unzip -d congress_113 congress_113/congress_113.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 congress_113/congress_113.geojson congress_113/tl_rd13_us_cd113.shp

congress_116_pa:
	mkdir -p congress_116_pa
	curl -o congress_116_pa/congress_116_pa.zip http://www.pacourts.us/assets/files/setting-6061/file-6845.zip?cb=b6385e
	unzip -d congress_116_pa congress_116_pa/congress_116_pa.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 congress_116_pa/congress_116_pa.geojson congress_116_pa/Remedial\ Plan\ Shapefile.shp

congress_legislators:
	mkdir -p congress_legislators
	curl -o congress_legislators/congress_legislators-current.yaml https://raw.githubusercontent.com/unitedstates/congress-congress_legislators/master/congress_legislators-current.yaml
	curl -o congress_legislators/congress_legislators-social-media.yaml https://raw.githubusercontent.com/unitedstates/congress-congress_legislators/master/congress_legislators-social-media.yaml

states:
	mkdir -p states
	curl -o states/states.zip https://www2.census.gov/geo/tiger/TIGER2017/STATE/tl_2017_us_state.zip
	unzip -d states states/states.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 states/states.geojson states/tl_2017_us_state.shp

counties:
	mkdir -p counties
	curl -o counties/counties.zip https://www2.census.gov/geo/tiger/TIGER2017/COUNTY/tl_2017_us_county.zip
	unzip -d counties counties/counties.zip
	ogr2ogr -f GeoJSON -t_srs crs:84 counties/counties.geojson counties/tl_2017_us_county.shp

state_leg:
	mkdir -p state_leg
	../scripts/source_state_leg.sh

ocd_ids:
	mkdir -p ocd_ids
	curl -o ocd_ids/ocd_ids.zip -L https://github.com/opencivicdata/ocd-division-ids/archive/master.zip
	unzip -d ocd_ids ocd_ids/ocd_ids.zip
