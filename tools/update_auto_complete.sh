#! /bin/bash

local output_path

#Set the correct output path, is there a way to automatically find this?
output_path="/etc/bash_completion.d"

python ./extract_nysa_completer.py

echo "Attempting to copy the auto complete output to the correct directory ${output_path}"
echo "You will need sudo priviledge to copy the generated script to ${output_path}/nysa"

sudo cp ./nysa "${output_path}/nysa"

echo "You will need to source the script or restart the bash shell for autocompletion to take effect"

