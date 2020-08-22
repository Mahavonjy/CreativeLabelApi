#!/usr/bin/env bash

cd ../

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

# pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U