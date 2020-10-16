#!/usr/bin/env bash

green=`tput setaf 2`
current_path=`pwd`
arr=(`echo ${current_path} | tr "/" "\n"`)
if [[ ${arr[@]:(-1)} == "scripts" ]]
then
	cd ../
fi

basic_env=""
development_test="FLASK_ENV=development_test"
while IFS= read -r line || [[ -n "$line" ]]; do
	if [[ ${line} == "FLASK_ENV"* ]]; then
	  basic_env=${line}
	fi
done < "$1"

sed -i -e "s/"${basic_env}"/"${development_test}"/g" .env
rm .env-e

sleep 1

echo
echo "${green}----- AUTHENTIFICATION TEST -----"
pytest -p no:warnings sources/tests/auth/authentification_test.py

echo
echo "${green}----- MEDIA UPLOAD TEST -----"
pytest -p no:warnings sources/tests/medias/media_test.py::TestMedia::test_upload_beat
echo
echo "${green}----- MEDIA UPDATE TEST -----"
pytest -p no:warnings sources/tests/medias/media_test.py::TestMedia::test_update_beat
echo
echo "${green}----- MEDIA DELETE BEAT TEST -----"
pytest -p no:warnings sources/tests/medias/media_test.py::TestMedia::test_delete_beat

echo
echo "${green}----- CONTRACT BEAT TEST -----"
pytest -p no:warnings sources/tests/beatContract/beat_contract_test.py

echo
echo "${green}----- ARTIST ADMIRATION TEST -----"
pytest -p no:warnings sources/tests/admirations/admiration_test.py

echo
echo "${green}----- PRESTIGE TEST -----"
pytest -p no:warnings sources/tests/prestiges/prestige_test.py

echo
echo "${green}----- CART TEST -----"
pytest -p no:warnings sources/tests/carts/cart_test.py

sleep 1

sed -i -e "s/"${development_test}"/"${basic_env}"/g" .env
rm .env-e
