#!/usr/bin/env python3
""" shebang """

from sources.models.profiles.profile import ProfileSchema
from sources.models import custom_response, es
from sources.models.users.user import User, UserSchema
from flask import Blueprint

from sources.tools.tools import check_dict_keys

api_medias_search = Blueprint('medias_search', __name__)
profile_schema = ProfileSchema()
user_schema = UserSchema()


@api_medias_search.route('/<string:string_to_search>', methods=['GET'])
def search_beats_and_artist(string_to_search):
    """ search matching with text_ in table medias """

    beats_and_artist = es.search(
        index="beats",
        doc_type="songs",
        body={"from": 0, "size": 10,
              "query": {
                  "query_string": {
                      "fields": ["title", "artist", "genre", "artist_tag", "description"],
                      "query": "*" + string_to_search + "*"
                  }
              },
              "sort": [{"listened": {"order": "asc", "mode": "min"}}]}
    )

    data = {'beats': [], 'artists': []}
    for r in beats_and_artist['hits']['hits']:
        data['beats'].append(r['_source'])

        artist_profile = profile_schema.dump(User.get_one_user(r['_source']['user_id']).profile)
        keys_to_remove = ['address', 'age', 'city', 'region', 'social_id', 'photo', 'email', 'cover_photo', 'photo']
        artist_profile = check_dict_keys(artist_profile, _keys=keys_to_remove, inverse=True)
        if artist_profile not in data['artists']:
            data['artists'].append(artist_profile)

    return custom_response(data, 200)


@api_medias_search.route('/beat/<int:beat_id>', methods=['GET'])
def get_beat_by_id(beat_id):
    """ """

    beat = es.search(
        index="beats",
        doc_type="songs",
        body={
            "query": {
                "bool": {
                    "must": [
                        {"match": {"id": beat_id}}
                    ]
                }
            }
        }
    )

    try:
        return custom_response(check_dict_keys(beat['hits']['hits'][0]['_source'], ['wave', 'stems'], True), 200)
    except IndexError:
        return custom_response("beat not found or deleted", 400)
