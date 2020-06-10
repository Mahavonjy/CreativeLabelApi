#!/usr/bin/env python3
""" shebang """

from sources.models.profiles.profile import ProfileSchema
from sources.models import custom_response, es
from sources.models.users.user import User
from flask import Blueprint

api_medias_search = Blueprint('medias_search', __name__)
profile_schema = ProfileSchema()


@api_medias_search.route('/songs/<string:text_>', methods=['GET'])
def search_song_in_db(text_, ref=None):
    """ search matching with text_ in table medias """

    resp = es.search(
        index="albums_and_songs",
        body={"from": 0, "size": 10,
              "query": {"bool": {"must": [{"wildcard": {"title": "*" + text_ + "*"}}]}},
              "sort": [{"number_play": {"order": "asc", "mode": "min"}}]}
    )
    songs = [r['_source'] for r in resp['hits']['hits']]
    if ref:
        return songs
    return custom_response({"songs": songs}, 200)


@api_medias_search.route('/albums/<string:text_>', methods=['GET'])
def search_album_in_db(text_, ref=None):
    """ search matching with text_ in table medias """

    resp = es.search(
        index="albums_and_songs",
        body={"from": 0, "size": 10,
              "query": {"bool": {"must": [{"wildcard": {"album_name": "*" + text_ + "*"}}]}},
              "sort": [{"number_play": {"order": "asc", "mode": "min"}}]}
    )
    albums = [r['_source'] for r in resp['hits']['hits']]
    if ref:
        return albums
    return custom_response({"albums": albums}, 200)


@api_medias_search.route('/artists/<string:text_>', methods=['GET'])
def search_artist(text_, ref=None):
    """ search matching with text_ in table medias """

    resp, l_, artists = es.search(
        index="albums_and_songs",
        body={"from": 0, "size": 10, "_source": ["user_id"],
              "query": {"bool": {"must": [{"wildcard": {"artist": "*" + text_ + "*"}}]}}}
    ), [], []
    for r in resp['hits']['hits']:
        if r['_source']['user_id'] not in l_:
            l_.append(r['_source']['user_id'])
            artists.append(profile_schema.dump(User.get_one_user(r['_source']['user_id']).profile))
    if ref:
        return artists
    return custom_response({"artists": artists}, 200)


@api_medias_search.route('/all/<string:text_>', methods=['GET'])
def search_all_in_db(text_):
    """ search matching with text_ in table album&media """

    return custom_response({
        "songs": search_song_in_db(text_, True),
        "albums": search_album_in_db(text_, True),
        "artists": search_artist(text_, True)}
        , 200)
