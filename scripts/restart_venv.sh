#!/usr/bin/env bash

current_path=`pwd`
arr=(`echo ${current_path} | tr "/" "\n"`)
if [[ ${arr[@]:(-1)} == "scripts" ]]
then
	cd ../
fi

pwd=`pwd`'/venv'

sleep 1

if [[ ! -d ${pwd} ]]
then
	rm -rf venv
fi

deactivate
python3 -m venv venv
source ../venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

