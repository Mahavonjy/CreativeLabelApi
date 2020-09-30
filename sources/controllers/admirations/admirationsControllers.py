#!/usr/bin/env python3
""" shebang """

from sources.models.admirations.admirations import Admiration, AdmireSchema
from sources.models.profiles.profile import ProfileSchema
from sources.models.users.user import User
from auth.authentification import Auth
from sources.models import custom_response
from flask import Blueprint

admiration_api = Blueprint('admirations', __name__)
admiration_schema = AdmireSchema()
profile_schema = ProfileSchema()


@admiration_api.route('/admire_user/<int:admire_id>', methods=['POST'])
@Auth.auth_required
def add_new_admiration_user(admire_id, user_connected_model, user_connected_schema):
    """ User add new admiration """

    def add():
        """ new user admired """

        new_admiration = Admiration(dict(user_id=user_connected_model.id, admire_id=admire_id))
        new_admiration.save()
        return "added"

    if not User.get_one_user(admire_id):
        return custom_response("User admire not found", 400)

    if admire_id is not user_connected_model.id:
        admire_info = user_connected_model.user.filter_by(admire_id=admire_id).first()
        return custom_response("exist", 400) if admire_info else custom_response(add(), 200)
    return custom_response("Unauthorized", 400)


@admiration_api.route('/delete_admire_user/<int:admire_id>', methods=['DELETE'])
@Auth.auth_required
def delete_admiration_user(admire_id, user_connected_model, user_connected_schema):
    """ User delete admiration """

    admire_info = user_connected_model.user.filter_by(admire_id=admire_id).first()
    if not admire_info:
        return custom_response("user admire not found", 400)
    admire_info.delete()
    return custom_response("deleted", 200)


@admiration_api.route('/all_user_admire/<int:user_id>', methods=['GET'])
def all_user_admiration(user_id):
    """ get all user admiration """

    user = User.get_one_user(user_id)
    if not user:
        return custom_response("user do not exist", 400)
    all_admiration, all_users, count = user.user.all(), {}, 0
    if all_admiration:
        for admire in all_admiration:
            info_admire = admiration_schema.dump(admire)
            ser_user = profile_schema.dump(User.get_one_user(info_admire["admire_id"]).profile)
            all_users[count], count = ser_user, count + 1
        return custom_response(all_users, 200)
    return custom_response("Empty", 200)
