#!/usr/bin/env python3
""" shebang """

import json
from sources.models import custom_response
from flask import Blueprint

flags_api = Blueprint('flags', __name__)


@flags_api.route('/check_country_and_city', methods=['GET'])
def get_all_country_allowed():
    """ read file text and add city """

    with open('country/Countries.json') as f:
        data = json.load(f)

    # change validates.py file if change it
    return custom_response([
        {
            "name": "Madagascar",
            "value": list(set(data['Madagascar']))
        }, {
            "name": "France",
            "value": list(set(data['France']))
        }, {
            "name": "Belgique",
            "value": list(set(data['Belgium']))
        }, {
            "name": "Luxembourg",
            "value": list(set(data['Luxembourg']))
        }, {
            "name": "Mauritius",
            "value": list(set(data['Mauritius']))
        }, {
            "name": "Mayotte",
            "value": list(set(data['Mayotte']))
        }, {
            "name": "Allemagne",
            "value": list(set(data['Germany']))
        },
    ], 200)
