#!/usr/bin/env python3
""" shebang """

from flask import Blueprint
from operator import itemgetter
from sources.models.users.user import User
from sources.models import custom_response
from auth.authentification import Auth
from sources.models.profiles.profile import ProfileSchema
from sources.models.artists.history.history import ArtistHistory, ArtistHistorySchema

artist_suggestion = Blueprint('artist_suggestion', __name__)
month_story_s = ArtistHistorySchema()
profile_schema = ProfileSchema()


def new_artists():
    """ get 10 new artist """

    all_artist = ArtistHistory.top_last()
    user_id_list = [month_story_s.dump(artist)['user_id'] for artist in all_artist]
    return [profile_schema.dump(User.get_one_user(_id).profile) for _id in user_id_list]


def top_artist_story():
    """ Top artist stream in 3 last month """

    story_s = []
    # for artist in all_artist:
    #     artist_month_story = month_story_s.dump(artist)
    #     if artist_month_story:
    #         n = history_schema.dump(artist_history)['months_story'][9:]
    #         m = sorted(n, key=itemgetter('modified_at'), reverse=True)[:2]
    #         for k in m:
    #             artist_month_story['month_stream'] += k['month_stream']
    #     story_s.append(artist_month_story)
    sorted_story = sorted(story_s, key=itemgetter('month_stream'), reverse=True)[:10]
    return [profile_schema.dump(User.get_one_user(p['user_id']).profile) for p in sorted_story]


@artist_suggestion.route('/', methods=['GET'])
@Auth.auth_required
def merge_suggestion(user_connected_model, user_connected_schema):
    """ i return all suggestion merge in this function """

    first_tmp, sec_tmp = User.get_len_artist()
    if first_tmp <= 10:
        return custom_response(dict(artist_suggestion=[profile_schema.dump(usr.profile) for usr in sec_tmp]), 200)
    top_arts = top_artist_story()
    new_arts = new_artists()
    new_arts = [i for i in new_arts if i not in top_arts]
    return custom_response(dict(top_artist=top_arts, new_artists=new_arts), 200)
