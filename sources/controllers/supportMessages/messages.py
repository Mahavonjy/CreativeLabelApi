#!/usr/bin/env python3
""" shebang """

from sources.models.supportMessages.messages import SupportMessages, SupportMessagesSchema
from sources.tools.tools import validate_data
from sources.models import custom_response
from auth.authentification import Auth
from flask import request, Blueprint

support_message_api = Blueprint('support_messages', __name__)
support_message = SupportMessagesSchema()


@support_message_api.route('/new_message', methods=['POST'])
def create_new_message():
    """
        A user create a new message to support
    """

    data, error = validate_data(support_message, request)
    if error:
        return custom_response(data, 400)

    SupportMessages(data).save()

    return custom_response("added", 200)


@support_message_api.route('/resolved', methods=['GET'])
def check_all_message_resolved():
    """
        A user create a new message to support
    """

    model_resolved, schema_resolved = SupportMessages.get_support_message_resolved(), []
    for mod_mess in model_resolved:
        schema_resolved.append(support_message.dump(mod_mess))

    return custom_response(schema_resolved, 200)


@support_message_api.route('/not_resolved', methods=['GET'])
def check_all_message_not_resolved():
    """
        A user create a new message to support
    """

    model_not_resolved, schema_not_resolved = SupportMessages.get_support_message_not_resolved(), []
    for mod_mess in model_not_resolved:
        schema_not_resolved.append(support_message.dump(mod_mess))

    return custom_response(schema_not_resolved, 200)


@support_message_api.route('/check_message/<int:message_id>', methods=['GET'])
def check_message_id(message_id):
    """
        A user create a new message to support
    """

    model_message = SupportMessages.get_message_by_id(message_id)
    if not model_message:
        return custom_response("id not found", 200)
    schema_message = support_message.dump(model_message)

    return custom_response(schema_message, 200)


@support_message_api.route('/update/<int:message_id>', methods=['PUT'])
@Auth.auth_required
def update_message(message_id, user_connected_model, user_connected_schema):
    """
        A user create a new message to support
    """

    if user_connected_model.right != 0:
        data, error = validate_data(support_message, request)
        if error:
            return custom_response(data, 400)

        model_message = SupportMessages.get_message_by_id(message_id)
        if not model_message:
            return custom_response("id not found", 200)

        model_message.update(data)

        return custom_response("updated", 200)
    return custom_response("Unauthorized", 400)
