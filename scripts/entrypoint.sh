#!/usr/bin/env bash

source .env
source scripts/migrate.sh
/usr/bin/supervisord
