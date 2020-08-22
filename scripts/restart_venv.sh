#!/usr/bin/env bash

cd ../

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

