#!/bin/bash

project="elections-api"
project_path="/usr/local/aclu/$project"
source_path="$project_path/sources/congress_photos"
data_path="$project_path/data/congress_photos"

node="/usr/local/bin/node"
smartcrop="/usr/local/bin/smartcrop"
width="175"
height="175"

mkdir -p "$data_path"

for path in `ls $source_path/*.jpg` ; do
	filename=`basename $path`
	echo "Cropping $filename"
	cropped="$data_path/$filename"
	json=`echo $cropped | sed 's/.jpg/.json/'`
	$node $smartcrop --width $width --height $height $path $cropped > $json
done
