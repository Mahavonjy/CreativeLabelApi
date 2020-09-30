#!/usr/bin/env bash

current_path=`pwd`
arr=(`echo ${current_path} | tr "/" "\n"`)
if [[ ${arr[@]:(-1)} == "scripts" ]]
then
	cd ../
fi


pwd=2245
user="cynthionmahavonjy"
index_name_of_all_beats="beats"
index_name_of_all_options="options"
index_name_of_all_services="services"
index_name_of_all_materials="materials"

rm -rf migrations/

# drop all table in db postgres
PGPASSWORD=$pwd PGUSER=$user psql -c "DROP SCHEMA public CASCADE;" creative
PGPASSWORD=$pwd PGUSER=$user psql -c "CREATE SCHEMA public;" creative

#PGPASSWORD=$pwd PGUSER=$user psql -c "DROP SCHEMA public CASCADE;" creative_test
#PGPASSWORD=$pwd PGUSER=$user psql -c "CREATE SCHEMA public;" creative_test

# drop all index in elastic search
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_beats}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_materials}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_services}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_options}"

# development
curl -XDELETE "http://localhost:9200/${index_name_of_all_beats}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_materials}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_services}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_options}"

# create all index in elastic search
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_beats}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_materials}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_services}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_options}"

# development
curl -XPUT "http://localhost:9200/${index_name_of_all_beats}"
curl -XPUT "http://localhost:9200/${index_name_of_all_materials}"
curl -XPUT "http://localhost:9200/${index_name_of_all_services}"
curl -XPUT "http://localhost:9200/${index_name_of_all_options}"

# create all table in db postgres
current_path=`pwd`
arr=(`echo ${current_path} | tr "/" "\n"`)
if [[ ${arr[@]:(-1)} != "scripts" ]]
then
	cd scripts
fi

source migrate.sh
