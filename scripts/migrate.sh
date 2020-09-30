#!/usr/bin/env bash

current_path=`pwd`
arr=(`echo ${current_path} | tr "/" "\n"`)
if [[ ${arr[@]:(-1)} == "scripts" ]]
then
	cd ../
fi

pwd=`pwd`'/migrations'

sleep 1

if [[ ! -d ${pwd} ]]
then
	python manage.py db init
fi

python manage.py db migrate
python manage.py db upgrade

if [[ $@ == -r ]]
then
	nohup flask run --host=0.0.0.0 --port=5000
fi
