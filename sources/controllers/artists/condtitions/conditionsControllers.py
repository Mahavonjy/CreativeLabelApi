#!/usr/bin/env python3
""" shebang """

from flask import Blueprint, request
from sqlalchemy import func

from preferences.defaultData import refund_allowed_type

from sources.tools.tools import convert_dict_to_sql_json, validate_data
from sources.models.users.user import User
from sources.models import custom_response
from sources.models.artists.conditions.globals import ConditionGlobals, ConditionGlobalSchema
from auth.authentification import Auth

artist_condition = Blueprint('artist_conditions', __name__)
condition_globals_schema = ConditionGlobalSchema()


@artist_condition.route('/update', methods=['PUT'])
@Auth.auth_required
def update_my_global_function(user_connected_model, user_connected_schema):
    data, error = validate_data(condition_globals_schema, request)
    if error:
        return custom_response(data, 400)

    if data['refund_policy'] not in refund_allowed_type:
        return custom_response("refund not support", 400)

    if data['travel_expenses']:
        data['travel_expenses'] = func.json_build_object(*convert_dict_to_sql_json(data['travel_expenses']))

    user_condition_globals = user_connected_model.condition_globals[0]
    user_condition_globals.update(data)

    return custom_response("updated", 200)


@artist_condition.route('/condition/<int:user_id>', methods=['GET'])
def check_artist_condition_global(user_id):

    user = User.get_one_user(user_id)
    if user and user.condition_globals:
        return custom_response(condition_globals_schema.dump(user.condition_globals[0]), 200)
    return custom_response("user or user condition global not found", 400)


def generate_condition_globals(user_id):
    """
    :param user_id:
    :return:
    """

    ConditionGlobals(dict(
        user_id=user_id,
    )).save()
    return True
