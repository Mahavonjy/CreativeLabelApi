#!/usr/bin/env python3
""" shebang """

from flask import Blueprint, request

from auth.authentification import Auth
from preferences import GOOGLE_BUCKET_TECHNICAL_SHEET
from sources.controllers import update_file_storage
from sources.controllers.tools.tools import validate_data
from sources.models import custom_response, add_in_storage
from sources.models.artists.materials.artistMaterials import Materials, MaterialsSchema

materials_api = Blueprint('materials', __name__)
materials_schema = MaterialsSchema()
bucket_name = GOOGLE_BUCKET_TECHNICAL_SHEET


def create_new_materials_for_new_services():
    """ create new materials """

    new_material = Materials({"list_of_materials": []})
    new_material.save()
    return new_material.id


def update_material(user_connected_schema, user_material_to_update, requested, data):
    technical_sheet = requested.files.get('technical_sheet')
    if technical_sheet:
        data["technical_sheet"] = add_in_storage(bucket_name, user_connected_schema, technical_sheet, req=True)
    user_material_to_update_dumped = materials_schema.dump(user_material_to_update)
    user_material_to_update_dumped.update(data)
    user_material_to_update.update(user_material_to_update_dumped)
    return user_material_to_update_dumped


@materials_api.route('/update_option_material/<int:option_id>', methods=['PUT'])
@Auth.auth_required
def update_material_by_option_id(option_id, user_connected_model, user_connected_schema):

    data, error = validate_data(materials_schema, request, return_dict=False)
    if error:
        return custom_response(data, 400)

    user_option_selected = user_connected_model.options.filter_by(id=option_id).first()
    if not user_option_selected:
        return custom_response("option not found", 400)
    user_material_to_update = user_option_selected.material

    if user_material_to_update:
        return custom_response(update_material(user_connected_schema, user_material_to_update, request, data), 200)

    return custom_response("material not found", 404)


@materials_api.route('/update_service_material/<int:service_id>', methods=['PUT'])
@Auth.auth_required
def update_material_by_service_id(service_id, user_connected_model, user_connected_schema):

    data, error = validate_data(materials_schema, request, return_dict=False)
    if error:
        return custom_response(data, 400)

    user_service_selected = user_connected_model.services.filter_by(id=service_id).first()
    if not user_service_selected:
        return custom_response("service not found", 400)
    user_material_to_update = user_service_selected.material

    if user_material_to_update:
        return custom_response(update_material(user_connected_schema, user_material_to_update, request, data), 200)

    return custom_response("material not found", 404)


def delete_material_technical_sheet(material):

    material_selected_schema = materials_schema.dump(material)
    technical_sheet = material_selected_schema['technical_sheet']
    if technical_sheet:
        technical_sheet_link_split_list = technical_sheet.split("/", 3)
        bucket_n, user_repo, filename = technical_sheet_link_split_list[3].split("/", 4)
        repository_name, keys = user_repo.split("_")
        kwargs = dict(bucket_name=bucket_n, repository_name=repository_name, delete=True, keys=keys, filename=filename)
        update_file_storage(**kwargs)
