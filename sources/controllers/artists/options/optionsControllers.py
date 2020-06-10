#!/usr/bin/env python3
""" shebang """

from sqlalchemy import func

from sources.controllers.artists.materials.materialsControllers import create_new_materials_for_new_services, \
    delete_material_technical_sheet
from sources.controllers import convert_dict_to_sql_json
from sources.models.artists.options.artistOptions import Options, OptionsSchema
from auth.authentification import Auth
from sources.controllers.tools.tools import validate_data
from sources.models import custom_response
from flask import Blueprint, request

options_api = Blueprint('options', __name__)
option_schema = OptionsSchema()


@options_api.route('/create', methods=['POST'])
@Auth.auth_required
def create_new_options(user_connected_model, user_connected_schema):
    """ create new materials """

    data, error = validate_data(option_schema, request)
    if error:
        return custom_response(data, 400)

    all_user_option = user_connected_model.options.all()
    for option in all_user_option:
        if option.name == data['name']:
            return custom_response("already exist", 400)

    data["user_id"] = user_connected_model.id
    data["materials_id"] = create_new_materials_for_new_services()
    new_option = Options(data)
    new_option.save()
    return custom_response(option_schema.dump(new_option), 200)


@options_api.route('/update/<int:option_id>', methods=['PUT'])
@Auth.auth_required
def update_one_option(option_id, user_connected_model, user_connected_schema):
    """ update one options """

    data, error = validate_data(option_schema, request)
    if error:
        return custom_response(data, 400)

    option_selected = user_connected_model.options.filter_by(id=option_id).first()
    if option_selected:
        option_selected_schema = option_schema.dump(option_selected)
        if data['special_dates']:
            data['special_dates'] = func.json_build_object(*convert_dict_to_sql_json(data['special_dates']))
        option_selected_schema.update(data)
        option_selected.update(option_selected_schema)
        return custom_response(option_schema.dump(option_selected), 200)

    return custom_response("option not found", 404)


@options_api.route('/delete/<int:option_id>', methods=['DELETE'])
@Auth.auth_required
def delete_one_option(option_id, user_connected_model, user_connected_schema):
    """ delete one options """

    option_selected = user_connected_model.options.filter_by(id=option_id).first()
    if option_selected:
        delete_material_technical_sheet(option_selected.material)
        option_selected.delete()
        return custom_response("deleted", 200)

    return custom_response("option not found", 404)
