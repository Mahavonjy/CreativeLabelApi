#!/usr/bin/env python3
""" shebang """

import datetime

from dateutil.relativedelta import relativedelta
from flask import Blueprint

from preferences.defaultData import discovery_allowed_genres
from sources.models.users.user import User
from sources.models import custom_response, es
from sources.models.medias.media import MediaOnStreamSchema
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import check_dict_keys, check_key_value_match

beats_suggestion = Blueprint('beats_suggestions', __name__)
media_schema = MediaOnStreamSchema()
profile_schema = ProfileSchema()
profile_keys_to_remove = ['address', 'age', 'city', 'region', 'social_id', 'photo', 'email', 'cover_photo', 'phone']


@beats_suggestion.route('/top_beats', methods=['GET'])
def get_top_beats(listed=False):
    """ top beat at the three last month """

    last_3_month_date = datetime.datetime.now() + relativedelta(months=-3)
    beats_and_artist = es.search(
        index="beats",
        body={
            "from": 0,
            "size": 10,
            "query": {
                "range": {
                    "created_at": {
                        "gte": last_3_month_date,
                        "lte": "now"
                    }
                }
            },
            "sort": [
                {"listened": "desc"},
                {"admire": "desc"},
                {"share": "desc"}
            ]}
    )

    beats = []
    for k in beats_and_artist['hits']['hits']:
        beats.append(k['_source'])

    if listed:
        return beats

    return custom_response({'top_beats': beats}, 200)


@beats_suggestion.route('/top_beatMakers', methods=['GET'])
def get_top_beat_maker(listed=False):
    """ get top beatmakers """

    top_beats = get_top_beats(listed=True)
    top_beat_maker = []

    for beat in top_beats:
        user = User.get_one_user(beat['user_id'])
        beat_maker_profile = profile_schema.dump(user.profile)
        beat_maker_profile = check_dict_keys(beat_maker_profile, _keys=profile_keys_to_remove, inverse=True)
        beat_maker_profile['number_of_beats'] = user.medias.count()

        if beat_maker_profile not in top_beat_maker:
            top_beat_maker.append(beat_maker_profile)

    if listed:
        return top_beat_maker

    return custom_response({"top_beatmaker": top_beat_maker}, 200)


@beats_suggestion.route('/lasted_beats', methods=['GET'])
def get_descending_beats(listed=False):
    """ get 10 beats in DB """

    all_beats = es.search(
        index="beats",
        body={
            "from": 0,
            "size": 10,
            "query": {"match_all": {}},
            "sort": [{"created_at": "desc"}]
        }
    )

    for k in all_beats['hits']['hits']:
        all_beats.append(k['_source'])

    if listed:
        return all_beats

    return custom_response({"descending": all_beats}, 200)


@beats_suggestion.route('/random', methods=['GET'])
def get_random_beats(listed=False):
    """ get 10 beats random in DB """

    beats_and_artist = es.search(index="beats", body={"from": 0, "size": 20, "query": {"match_all": {}}})
    all_beats = []

    for k in beats_and_artist['hits']['hits']:
        all_beats.append(k['_source'])

    if listed:
        return all_beats

    return custom_response({"random": all_beats}, 200)


@beats_suggestion.route('/news_beat_makers', methods=['GET'])
def all_new_beat_maker_in_the_six_last_month(listed=False):
    """ new beatMaker in the six last month with one or plus beats shared """

    all_beat_makers = []
    _beat_maker = User.all_beat_maker_in_three_last_month()
    for _user in _beat_maker:
        beat_maker_profile = profile_schema.dump(_user.profile)
        all_beat_makers.append(check_dict_keys(beat_maker_profile, _keys=profile_keys_to_remove, inverse=True))

    if listed:
        return all_beat_makers

    return custom_response({"new_beatMaker": all_beat_makers}, 200)


@beats_suggestion.route('/discovery_beats', methods=['GET'])
def african_discovery_beats(listed=False):
    """ Check african specific beat style """

    _query_list = [{"match": {"genre": genre}} for genre in discovery_allowed_genres]
    beats_and_artist = check_key_value_match(_query_list)
    all_beats = []

    for k in beats_and_artist['hits']['hits']:
        all_beats.append(k['_source'])

    if listed:
        return all_beats

    return custom_response(all_beats, 200)


@beats_suggestion.route('/all', methods=['GET'])
def all_beats_suggestion_tried():
    """ tried all function of suggestion and trie it """

    return custom_response(dict(
        random=get_random_beats(listed=True),
        top_beatmaker=get_top_beat_maker(listed=True),
        top_beats=get_top_beats(listed=True),
        discovery_beats=african_discovery_beats(listed=True),
        new_beatMaker=all_new_beat_maker_in_the_six_last_month(listed=True),
    ), 200)
