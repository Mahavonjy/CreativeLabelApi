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
echo "${green}-----run authentification test-----"
# pytest sources/tests/auth/authentification_test.py

echo
echo "${green}-----run media test-----"
pytest sources/tests/medias/media_test.py::TestMedia::test_update_beat

sleep 1

sed -i -e "s/"${development_test}"/"${basic_env}"/g" .env
rm .env-e
