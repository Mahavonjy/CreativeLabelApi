#!/usr/bin/env python3
""" shebang """

from sources.models.bankingDetails.banking import BankingDetails, BankingSchema
from sources.controllers.tools.tools import validate_data
from auth.authentification import Auth
from sources.models import custom_response
from flask import Blueprint, request

banking_api = Blueprint('banking', __name__)
banking_schema = BankingSchema()


@banking_api.route('/create', methods=['POST'])
@Auth.auth_required
def create_user_banking_details(user_connected_model, user_connected_schema):
    """ create new banking details """

    data, error = validate_data(banking_schema, request)
    if error:
        return custom_response(data, 400)

    data['user_id'] = user_connected_model.id
    new_user_banking_details = BankingDetails(data)
    new_user_banking_details.save()
    return custom_response(banking_schema.dump(new_user_banking_details), 200)


@banking_api.route('/update', methods=['PUT'])
@Auth.auth_required
def update_user_banking_details(user_connected_model, user_connected_schema):
    """ update banking details """

    data, error = validate_data(banking_schema, request)
    if error:
        return custom_response(data, 400)

    user_banking = user_connected_model.banking
    if not user_banking:
        return custom_response("banking details not found, create one", 404)

    user_banking_schema = banking_schema.dump(user_banking[0])
    user_banking_schema.update(data)
    user_banking[0].update(user_banking_schema)
    return custom_response(user_banking_schema, 200)


@banking_api.route('/delete', methods=['DELETE'])
@Auth.auth_required
def delete_user_banking_details(user_connected_model, user_connected_schema):
    """ delete banking details """

    data, error = validate_data(banking_schema, request)
    if error:
        return custom_response(data, 400)

    user_banking = user_connected_model.banking
    if not user_banking:
        return custom_response("banking details not found, create one", 404)

    user_banking[0].delete()
    return custom_response("updated", 200)
