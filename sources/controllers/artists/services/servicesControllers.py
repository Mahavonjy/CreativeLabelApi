#!/usr/bin/env python3
""" shebang """

from sources.controllers import convert_dict_to_sql_json
from sources.controllers.artists.materials.materialsControllers import create_new_materials_for_new_services, \
    delete_material_technical_sheet
from sources.controllers.stars.starsControllers import check_service_stars, generate_basic_stars
from sources.mail.SendMail import first_service
from sources.models.artists.options.artistOptions import OptionsSchema
from sources.models.artists.services.artistServices import ServiceSchema, Services
from sources.models.artists.materials.artistMaterials import Materials, MaterialsSchema
from sources.models.users.user import User
from sources.tools.tools import validate_data, check_user_options_and_services
from preferences import GOOGLE_BUCKET_IMAGES
from auth.authentification import Auth
from sources.models import custom_response
from sources.models import add_in_storage
from flask import Blueprint, request
from sqlalchemy import func

from sources.models.stars.noteStars import Stars

artist_services_api = Blueprint('artist_services', __name__)
material_schema = MaterialsSchema()
service_schema = ServiceSchema()
option_schema = OptionsSchema()
bucket_name = GOOGLE_BUCKET_IMAGES


def return_services(service_dumped, service_dumped_not_dumped):

    service_dumped['materials'] = material_schema.dump(service_dumped_not_dumped.material)
    return service_dumped


def check_galleries_files(requested, user):

    galleries = []
    requested_files = requested.files

    for gallery in requested_files:
        galleries.append(add_in_storage(bucket_name, user, requested.files.get(gallery), "services/"))

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
    data['galleries'] = list(set(data.get("galleries", []) + check_galleries_files(request, user_connected_schema)))
    if len(data['galleries']) == 0:
        return custom_response("i need galleries", 400)
    if not data.get("travel_expenses"):
        data["travel_expenses"] = user_connected_model.condition_globals[0].travel_expenses
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

    service_to_update = user_connected_model.services.filter_by(id=services_id).first()
    if service_to_update:
        data, error = validate_data(service_schema, request, return_dict=False)
        if error:
            return custom_response(data, 400)
        new_galleries = check_galleries_files(request, user_connected_schema)
        if len(new_galleries) != 0:
            data['galleries'] = list(set(data.get("galleries", []) + new_galleries))
        if data['special_dates']:
            data['special_dates'] = func.json_build_object(*convert_dict_to_sql_json(data['special_dates']))
        service_to_update.update(data)
        return custom_response(return_services(service_schema.dump(service_to_update), service_to_update), 200)
    return custom_response("service not found", 200)


@artist_services_api.route('/delete/<int:services_id>', methods=['DELETE'])
@Auth.auth_required
def display_one_artist_services(services_id, user_connected_model, user_connected_schema):
    """ Delete one user services """

    user_service_to_delete = user_connected_model.services.filter_by(id=services_id).first()
    if user_service_to_delete:
        delete_material_technical_sheet(user_service_to_delete.material)
        stars = Stars.get_stars_by_service_id(user_service_to_delete.id)
        stars.delete()
        user_service_to_delete.delete()
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
