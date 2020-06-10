#!/usr/bin/env python3
""" shebang """

from flask import g as auth
from sqlalchemy import func
from statistics import mean
from flask import Blueprint, request

from sources.models.users.user import User
from sources.models import custom_response
from auth.authentification import Auth
from preferences.defaultDataConf import USER_AUDITOR_PRO
from sources.tools.tools import validate_data
from sources.controllers import convert_dict_to_sql_json
from sources.models.stars.noteStars import Stars, StarSchema

user_stars = Blueprint('users_stars', __name__)
user_stars_schema = StarSchema()


def check_service_stars(service_id):
    """ check service note """

    try:
        return mean(Stars.get_stars_by_service_id(service_id).note or [0])
    except AttributeError:
        return [0]


def update_note(stars_model, stars_, data, user_connected_model):
    try:
        if stars_['users_who_rated'].get(str(user_connected_model.id)) is not None:
            stars_['note'].remove(stars_['users_who_rated'].get(str(auth.user.get('id'))))
    except KeyError:
        pass
    finally:
        note = data['note'].pop()
        stars_["users_who_rated"][str(user_connected_model.id)] = note
        stars_['note'].append(note)
        stars_["users_who_rated"] = func.json_build_object(*convert_dict_to_sql_json(stars_["users_who_rated"]))
        stars_model.update(stars_)
    return custom_response({"note": mean(stars_['note'])}, 200)


@user_stars.route('/update', methods=['PUT'])
@Auth.auth_required
def update_note_by_service_id_or_user_id(user_connected_model, user_connected_schema):
    """

    @return:
    """
    data, error = validate_data(user_stars_schema, request)
    if error:
        return custom_response(data, 400)

    if data.get('service_id'):
        stars_to_add_note = Stars.get_stars_by_service_id(data.get('service_id'))
        if not stars_to_add_note:
            custom_response("Service rate not found", 400)
        stars_ = user_stars_schema.dump(stars_to_add_note)
        update_note(stars_to_add_note, stars_, data, user_connected_model)
        return custom_response("success", 200)
    elif data.get('user_id'):
        artist_to_note = User.get_one_user(data['user_id'])
        user_who_set_note = User.get_one_user(auth.user.get('id'))
        if not artist_to_note.user_type == user_who_set_note.user_type == USER_AUDITOR_PRO:
            stars_to_add_note = Stars.get_stars_by_user_id(data.get('user_id'))
            if not stars_to_add_note:
                custom_response("Service rate not found", 400)
            stars_ = user_stars_schema.dump(stars_to_add_note)
            update_note(stars_to_add_note, stars_, data, user_connected_model)
            return custom_response("success", 200)
        return custom_response("Unauthorized", 400)
    return custom_response("I need user_id or service_id", 400)


def generate_basic_stars(user_id=None, service_id=None):
    """
    :param user_id: user id who create note item in database
    :param service_id:
    :return: True
    """

    if user_id:
        Stars(dict(user_id=user_id)).save()
    elif service_id:
        Stars(dict(service_id=service_id)).save()
    return True
