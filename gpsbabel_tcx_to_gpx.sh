#!/usr/bin/env bash
# This script will convert tcx files (from e.g. Garmin head unit) to GPX files.
# Requires gpsbabel for the actual conversion

input_folder="/mnt/data/Documenten/Garmin/History/Zuid_Europa_2017"
gpsbabel_bin="/home/fvdnabee/Downloads/gpsbabel-continuous/gpsbabel"

output_folder="$input_folder/tcx2gpx"
if [[ ! -d $output_folder ]]; then
	mkdir $output_folder
fi

pushd $input_folder
for tcxfile in *.tcx ; do
	outputfilename=${tcxfile%.tcx}.gpx
	cli_cmd="$gpsbabel_bin  -t -i gtrnctr -f $tcxfile -o gpx -F $output_folder/$outputfilename"
	output=$($cli_cmd)
	echo "$cli_cmd returned $?"
done
popd

