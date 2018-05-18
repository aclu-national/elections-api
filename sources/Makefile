all: districts_113 districts_116_pa

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
