#!/usr/bin/env bash

cd ../

pwd=2245
user="cynthionmahavonjy"
index_name_of_all_options="options"
index_name_of_all_services="services"
index_name_of_all_materials="materials"
index_name_of_albums_and_songs="albums_and_songs"

rm -rf migrations/

# drop all table in db postgres
PGPASSWORD=$pwd PGUSER=$user psql -c "DROP SCHEMA public CASCADE;" creative
PGPASSWORD=$pwd PGUSER=$user psql -c "CREATE SCHEMA public;" creative

#PGPASSWORD=$pwd PGUSER=$user psql -c "DROP SCHEMA public CASCADE;" creative_test
#PGPASSWORD=$pwd PGUSER=$user psql -c "CREATE SCHEMA public;" creative_test

# drop all index in elastic search
curl -XDELETE "http://elasticsearch:9200/${index_name_of_albums_and_songs}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_materials}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_services}"
curl -XDELETE "http://elasticsearch:9200/${index_name_of_all_options}"

# development
curl -XDELETE "http://localhost:9200/${index_name_of_albums_and_songs}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_materials}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_services}"
curl -XDELETE "http://localhost:9200/${index_name_of_all_options}"

# create all index in elastic search
curl -XPUT "http://elasticsearch:9200/${index_name_of_albums_and_songs}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_materials}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_services}"
curl -XPUT "http://elasticsearch:9200/${index_name_of_all_options}"

# development
curl -XPUT "http://localhost:9200/${index_name_of_albums_and_songs}"
curl -XPUT "http://localhost:9200/${index_name_of_all_materials}"
curl -XPUT "http://localhost:9200/${index_name_of_all_services}"
curl -XPUT "http://localhost:9200/${index_name_of_all_options}"

# create all table in db postgres
cd scripts
source migrate.sh
