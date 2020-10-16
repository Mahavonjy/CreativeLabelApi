#!/usr/bin/env python3
""" shebang """

import cloudinary.uploader
from flask import Blueprint, request

from auth.authentification import Auth
from sources.tools.tools import validate_data
from sources.models import custom_response
from preferences import CLOUD_TECHNICAL_SHEET as CTS
from sources.models.artists.materials.artistMaterials import Materials, MaterialsSchema

materials_api = Blueprint('materials', __name__)
materials_schema = MaterialsSchema()


def create_new_materials_for_new_services():
    """ create new materials """

    new_material = Materials({"list_of_materials": []})
    new_material.save()
    return new_material.id


def update_material(_u_schema, user_material_to_update, requested, data):
    """

    Args:
        _u_schema:
        user_material_to_update:
        requested:
        data:

    Returns:

    """

    technical_sheet = requested.files.get('technical_sheet')
    if technical_sheet:
        fileStorage_key = _u_schema['fileStorage_key']
        user_id = _u_schema['id']
        data["technical_sheet"] = cloudinary.uploader.upload(
            technical_sheet,
            public_id=fileStorage_key + str(user_id) + technical_sheet.filename.split(".")[0],
            folder=CTS + "/" + fileStorage_key + str(user_id)
        )['secure_url']
    user_material_to_update_dumped = materials_schema.dump(user_material_to_update)
    user_material_to_update_dumped.update(data)
    user_material_to_update.update(user_material_to_update_dumped)
    return user_material_to_update_dumped


@materials_api.route('/update_option_material/<int:option_id>', methods=['PUT'])
@Auth.auth_required
def update_material_by_option_id(option_id, user_connected_model, user_connected_schema):
    """

    Args:
        option_id:
        user_connected_model:
        user_connected_schema:

    Returns:

    """

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
    """

    Args:
        service_id:
        user_connected_model:
        user_connected_schema:

    Returns:

    """

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


def delete_material_technical_sheet(material, _u_model):
    """

    Args:
        material:
        _u_model:
    """

    user_id = _u_model.user_id
    fileStorage_key = _u_model.fileStorage_key
    technical_sheet = materials_schema.dump(material).get('technical_sheet', None)
    if technical_sheet:
        file_named = technical_sheet.split("/")[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id=CTS + "/" + fileStorage_key + str(user_id) + "/" + file_named)
