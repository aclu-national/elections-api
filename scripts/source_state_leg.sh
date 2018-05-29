#!/bin/bash

PROJECT="elections-api"
PROJECT_PATH="/usr/local/aclu/$PROJECT"

source_dir="$PROJECT_PATH/sources/state_leg"
lower_house="01 02 04 05 06 08 09 10 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56 72"
upper_house="01 05 06 08 09 10 11 12 13 15 16 18 19 20 21 22 23 24 25 26 29 30 31 32 33 34 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56 72"

mkdir -p "$source_dir"

for n in $lower_house ; do
	id="tl_2017_""$n""_sldl"
	url="https://www2.census.gov/geo/tiger/TIGER2017/SLDL/$id.zip"
	echo "$url"
	#curl -q -o "$source_dir/$id.zip" "$url"
	mkdir -p "$source_dir/$id"
	unzip -d "$source_dir/$id" "$source_dir/$id.zip"
	ogr2ogr -f GeoJSON -t_srs crs:84 "$source_dir/$id/$id.geojson" "$source_dir/$id/$id.shp"
done

for n in $upper_house ; do
	id="tl_2017_""$n""_sldu"
	url="https://www2.census.gov/geo/tiger/TIGER2017/SLDU/$id.zip"
	echo "$url"
	#curl -q -o "$source_dir/$id.zip" "$url"
	mkdir -p "$source_dir/$id"
	unzip -d "$source_dir/$id" "$source_dir/$id.zip"
	ogr2ogr -f GeoJSON -t_srs crs:84 "$source_dir/$id/$id.geojson" "$source_dir/$id/$id.shp"
done
