#!/usr/bin/env bash

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

echo "-----run authentification test-----"
pytest sources/tests/auth/authentification_test.py

sleep 1

sed -i -e "s/"${development_test}"/"${basic_env}"/g" .env
rm .env-e
