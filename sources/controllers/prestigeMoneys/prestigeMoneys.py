#!/usr/bin/env python3
""" shebang """

from sources.models.prestigeMoneys.prestigeMoneys import Prestige, PrestigeSchema
from sources.models.users.user import User, UserSchema
from sources.tools.tools import random_string, convert_dict_to_sql_json
from auth.authentification import Auth
from sources.mail.SendMail import send_prestige
from sources.models import custom_response
from preferences import defaultData
from flask import wrappers
from flask import Blueprint
from sqlalchemy import func
import datetime

prestige_api = Blueprint('prestige', __name__)
prestige_schema = PrestigeSchema()
user_schema = UserSchema()


def prestige_data(ser_user_sender_id, ser_user_recipient_id, prestige, song_id):
    """

    :param ser_user_sender_id: id of user who send a prestige
    :param ser_user_recipient_id: id of artist who receive the prestige
    :param prestige: this is an information of the prestige
    :param song_id: store an id song
    :return: a dict of all information
    """

    return dict(
        key_share=random_string(20), media_id=song_id, recipient_id=ser_user_recipient_id,
        sender_id=ser_user_sender_id, prestige=defaultData.prestige_allowed_type[prestige]
    )


@prestige_api.route('/send/<int:prestige>/<int:song_id>', methods=['POST'])
@Auth.auth_required
def send_prestige_email(prestige, song_id, user_connected_model, user_connected_schema):
    """

    @param song_id: store an id song
    @param prestige:  prestige type
    @param user_connected_schema:
    @param user_connected_model:
    :return: success if success else prestige not found
    """

    # song = response_is_song_not_exist = get_one_media(song_id, True)
    # if isinstance(response_is_song_not_exist, wrappers.Response) and response_is_song_not_exist.status_code == 400:
    #     return response_is_song_not_exist
    # user_recipient = User.get_one_user(song.get('user_id'))
    # ser_user_recipient = user_schema.dump(user_recipient)
    # if user_connected_schema.get('email') == ser_user_recipient.get('email'):
    #     return custom_response('Unauthorized', 400)
    # data = prestige_data(user_connected_schema.get('id'), ser_user_recipient.get('id'), prestige, song_id)
    # if not data:
    #     return custom_response("prestige not found", 400)
    # now = datetime.datetime.now().strftime("%Y-%m")
    # Prestige(data).save()
    # send_prestige("SendPrestige.html", user_connected_schema.get('name'), user_connected_schema.get('email'),
    #               ser_user_recipient.get('email'), data.get('prestige'), song.get('title'))
    # user_recipient_story_model = user_recipient.history[0]
    # recipient_story['months_story'][str(now)]['prestige'].append(defaultData.prestige_allowed_type[prestige])
    # recipient_story['months_story'] = func.json_build_object(*convert_dict_to_sql_json(recipient_story['months_story']))
    # user_recipient.history[0].update(recipient_story)
    # return custom_response("success", 200)
