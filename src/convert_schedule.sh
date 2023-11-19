#!/bin/bash

path_to_schedule=(resources/*.xls)
file_name=$(ls "$path_to_schedule" 2>/dev/null | head -n 1)
file_name=$(basename "$file_name" .xls)
pyexcel transcode "$path_to_schedule" resources/"$file_name".xlsx
rm "$path_to_schedule"
