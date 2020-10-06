#!/usr/bin/env python3
""" shebang """

from preferences import CLOUD_IMAGES_SERVICES_TYPE
from sources.controllers.artists.materials.materialsControllers import create_new_materials_for_new_services, \
    delete_material_technical_sheet
from sources.controllers.stars.starsControllers import check_service_stars, generate_basic_stars
from sources.mail.SendMail import first_service
from sources.models.artists.options.artistOptions import OptionsSchema
from sources.models.artists.services.artistServices import ServiceSchema, Services
from sources.models.artists.materials.artistMaterials import Materials, MaterialsSchema
from sources.models.elastic.fillInElastic import document_delete
from sources.models.users.user import User
from sources.tools.tools import convert_dict_to_sql_json, destroy_image, upload_image, validate_data, \
    check_user_options_and_services
from auth.authentification import Auth
from sources.models import custom_response
from flask import Blueprint, request
from sqlalchemy import func

from sources.models.stars.noteStars import Stars

artist_services_api = Blueprint('artist_services', __name__)
material_schema = MaterialsSchema()
service_schema = ServiceSchema()
option_schema = OptionsSchema()


def return_services(service_dumped, service_dumped_not_dumped):
    service_dumped['materials'] = material_schema.dump(service_dumped_not_dumped.material)
    return service_dumped


def check_galleries_files(req, user):
    galleries = []
    requested_files = req.files

    for row in requested_files:
        galleries.append(upload_image(req.files.get(row), CLOUD_IMAGES_SERVICES_TYPE, user.fileStorage_key, user.id))

    return galleries


@artist_services_api.route('/my_services', methods=['GET'])
@Auth.auth_required
def display_all_artist_services(user_connected_model, user_connected_schema):
    """ Check all user services """

    return custom_response(check_user_options_and_services(user_connected_model), 200)


@artist_services_api.route('/newService', methods=['POST'])
@Auth.auth_required
def create_new_service(user_connected_model, user_connected_schema):
    """ Create a new service by artist """

    data, error = validate_data(service_schema, request, return_dict=False)
    if error:
        return custom_response(data, 400)

    all_user_services = user_connected_model.services.all()
    for service in all_user_services:
        if service.title == data['title'] and service.reference_city == data['reference_city'] \
                or service.title == data['title'] and service.events == data['events']:
            return custom_response("same title and reference_city", 400)

    new_galleries = check_galleries_files(request, user_connected_model)
    data['galleries'] = list(set(data.get("galleries", []) + new_galleries))
    if len(data['galleries']) == 0:
        return custom_response("i need galleries", 400)

    if not data.get("travel_expenses"):
        data["travel_expenses"] = user_connected_model.condition_globals[0].travel_expenses
    else:
        data['travel_expenses'] = func.json_build_object(*convert_dict_to_sql_json(data['travel_expenses']))

    data['user_id'] = user_connected_schema["id"]
    data['materials_id'] = create_new_materials_for_new_services()
    if len(all_user_services) == 0:
        first_service('FirstService.html', user_connected_schema["email"], user_connected_schema["name"], data["title"])

    new_service = Services(data)
    new_service.save()
    generate_basic_stars(service_id=new_service.id)
    return custom_response(return_services(service_schema.dump(new_service), new_service), 200)


@artist_services_api.route('/update/<int:services_id>', methods=['PUT'])
@Auth.auth_required
def update_service(services_id, user_connected_model, user_connected_schema):
    """ Update one service by artist """

    _u_model = user_connected_model
    service_to_update = _u_model.services.filter_by(id=services_id).first()
    if service_to_update:
        data, error = validate_data(service_schema, request, return_dict=False)
        if error:
            return custom_response(data, 400)
        new_galleries = check_galleries_files(request, _u_model)
        if len(new_galleries) != 0:
            data['galleries'] = list(set(data.get("galleries", []) + new_galleries))
        if data['special_dates']:
            data['special_dates'] = func.json_build_object(*convert_dict_to_sql_json(data['special_dates']))

        for link in service_to_update.galleries:
            if link not in data['galleries']:
                destroy_image(link, CLOUD_IMAGES_SERVICES_TYPE, _u_model.fileStorage_key, _u_model.id)
        service_to_update.update(data)
        return custom_response(return_services(service_schema.dump(service_to_update), service_to_update), 200)
    return custom_response("service not found", 200)


@artist_services_api.route('/delete/<int:services_id>', methods=['DELETE'])
@Auth.auth_required
def delete_one_artist_services(services_id, user_connected_model, user_connected_schema):
    """ Delete one user services """

    s_to_delete = user_connected_model.services.filter_by(id=services_id).first()
    if s_to_delete:
        _u_model = user_connected_model
        delete_material_technical_sheet(s_to_delete.material, user_connected_model)
        stars = Stars.get_stars_by_service_id(s_to_delete.id)
        stars.delete()
        for link in s_to_delete.galleries:
            destroy_image(link, CLOUD_IMAGES_SERVICES_TYPE, _u_model.fileStorage_key, _u_model.id)
        s_to_delete.delete()
        document_delete("services", "prestations", {"id": s_to_delete.id}, {"created_at": s_to_delete.created_at})
        return custom_response("deleted", 200)
    return custom_response("service not found", 200)


@artist_services_api.route('/<int:service_id>', methods=['GET'])
def search_user_service_by_id(service_id):
    service_checked = Services.get_by_service_id(service_id)

    if not service_checked:
        return custom_response("service not found", 400)

    service_checked = service_schema.dump(service_checked)
    material_id = service_checked["materials_id"]
    service_checked["materials"] = material_schema.dump(Materials.get_by_materials_id(material_id))
    service_checked["artist_name"] = User.get_one_user(service_checked["user_id"]).name
    service_checked["notes"] = check_service_stars(service_checked["id"])
    _options = User.get_one_user(service_checked["user_id"]).options.all()
    service_checked["options"] = []
    for option in _options:
        if service_checked["id"] in option.services_id_list:
            service_checked["options"].append(option_schema.dump(option))

    return custom_response({"service": service_checked}, 200)
