#!/usr/bin/env python3
""" shebang """

from preferences.defaultData import type_of_isl_artist, allowed_lang, allowed_events
from sources.models import custom_response
from flask import Blueprint

artist_type_api = Blueprint('artist_type', __name__)


@artist_type_api.route('/all', defaults={'lang': None}, methods=['GET'])
@artist_type_api.route('/all/<string:lang>', methods=['GET'])
def all_artist_types(lang):
    """ get all artist types """

    if lang and lang not in allowed_lang:
        return custom_response("Lang not allowed", 400)

    data_of_artist_type = dict(artist_types=type_of_isl_artist, events=allowed_events)

    return custom_response(data_of_artist_type, 200)
