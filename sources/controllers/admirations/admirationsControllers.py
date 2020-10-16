#!/usr/bin/env python3
""" shebang """

from preferences import profile_keys_to_remove
from sources.models.admirations.admirations import Admiration, AdmireSchema
from sources.models.profiles.profile import ProfileSchema
from sources.models.users.user import User
from auth.authentification import Auth
from sources.models import custom_response
from flask import Blueprint

from sources.tools.tools import check_dict_keys

admiration_api = Blueprint('admirations', __name__)
admiration_schema = AdmireSchema()
profile_schema = ProfileSchema()


@admiration_api.route('/admire_user/<int:artist_to_admire_id>', methods=['POST'])
@Auth.auth_required
def add_new_admiration_user(artist_to_admire_id, user_connected_model, user_connected_schema):
    """ User add new admiration """

    if not User.get_one_user(artist_to_admire_id):
        return custom_response("User not found", 400)

    if artist_to_admire_id is not user_connected_model.id:
        admire_info = user_connected_model.all_admires.filter_by(admire_id=artist_to_admire_id).first()

        if admire_info:
            return custom_response("exist", 400)

        Admiration(dict(user_id=user_connected_model.id, admire_id=artist_to_admire_id)).save()
        return custom_response("Added", 200)

    return custom_response("Unauthorized", 400)


@admiration_api.route('/delete_admire_user/<int:artist_do_not_admire_id>', methods=['DELETE'])
@Auth.auth_required
def delete_admiration_user(artist_do_not_admire_id, user_connected_model, user_connected_schema):
    """ User delete admiration """

    admire_info = user_connected_model.all_admires.filter_by(admire_id=artist_do_not_admire_id).first()
    if not admire_info:
        return custom_response("Not found", 400)

    admire_info.delete()
    return custom_response("deleted", 200)


@admiration_api.route('/all_user_admire/<int:user_id>', methods=['GET'])
def all_user_admiration(user_id):
    """ get all user admiration """

    user = User.get_one_user(user_id)
    if not user:
        return custom_response("user do not exist", 400)

    all_users = {"all_admire": [], "my_admirers": []}
    all_admiration = user.all_admires.all()
    all_admirers = user.my_admirers.all()

    for admire in all_admiration:
        u_pr = profile_schema.dump(User.get_one_user(admire.admire_id).profile)
        all_users['all_admire'].append(check_dict_keys(u_pr, _keys=profile_keys_to_remove, inverse=True))

    for admire in all_admirers:
        u_pr = profile_schema.dump(User.get_one_user(admire.admire_id).profile)
        all_users['my_admirers'].append(check_dict_keys(u_pr, _keys=profile_keys_to_remove, inverse=True))

    return custom_response(all_users, 200)


@admiration_api.route('/my_admire', methods=['GET'])
@Auth.auth_required
def all_my_admiration(user_connected_model, user_connected_schema):
    """ """

    return all_user_admiration(user_connected_model.id)
