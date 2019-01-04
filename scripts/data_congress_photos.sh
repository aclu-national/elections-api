#!/bin/bash

project="elections-api"
project_path="/usr/local/aclu/$project"
source_path="$project_path/sources/congress_photos"
data_path="$project_path/data/congress_photos"
legislators_path="$project_path/data/congress_legislators"

smartcrop="/usr/local/bin/smartcrop"
width="175"
height="175"

mkdir -p "$data_path"

for path in `ls $source_path/*.jpg` ; do
	filename=`basename $path`
	cropped="$data_path/$filename"
	if [ ! -f "$cropped" ] ; then
		echo "Cropping $filename"
		json=`echo $cropped | sed 's/.jpg/.json/'`
		$smartcrop --width $width --height $height $path $cropped > $json
	fi
done

for state in `ls $legislators_path` ; do
	for json in `ls $legislators_path/$state` ; do
		bioguide=`jq -r ".id.bioguide" "$legislators_path/$state/$json"`
		fname=`jq -r ".name.first" "$legislators_path/$state/$json"`
		lname=`jq -r ".name.last" "$legislators_path/$state/$json"`
		if [ ! -f "$data_path/$bioguide.jpg" ] ; then
			echo "No photo found for $fname $lname ($bioguide)"
		fi
	done
done
