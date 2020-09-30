#!/usr/bin/env python3
""" shebang """

from sources.models.partnership.partnership import Partner, PartnerSchema
from sources.models.users.user import UserSchema
from sources.tools.tools import destroy_image, upload_image, validate_data
from auth.authentification import Auth
from preferences import CLOUD_IMAGES_PARTNERS_TYPE, defaultData
from sources.models import custom_response
from flask import Blueprint, request

partner_api = Blueprint('partners', __name__)
secure_photo = defaultData.media_allowed_Photos_Extensions
partner_schema = PartnerSchema()
user_schema = UserSchema()


@partner_api.route("/addNewPartner", methods=['POST'])
@Auth.auth_required
def add_new_partner(user_connected_model, user_connected_schema):
    """ add new partner """

    if user_connected_model.right == 2:
        data, error = validate_data(partner_schema, request, False)
        if error:
            return custom_response(data, 400)

        if Partner.partner_by_name(data['name']):
            return custom_response("partner existing", 400)

        logo_img = request.files.get("logo")
        if not logo_img:
            return custom_response("i need logo image", 400)

        _u_model = user_connected_model
        type_photo = logo_img.content_type
        if type_photo.rsplit('/', 1)[1] not in secure_photo:
            return custom_response("photo type is not supported", 400)
        data['logo'] = upload_image(logo_img, CLOUD_IMAGES_PARTNERS_TYPE, _u_model.fileStorage_key, _u_model.id)
        data['user_id'] = user_connected_model.id
        new_partners = Partner(data)
        new_partners.save()
        return custom_response("created", 200)
    return custom_response("Unauthorized", 400)


@partner_api.route("/<int:partner_id>", methods=['GET'])
def show_an_partner(partner_id):
    """ show new partner """

    query_ = Partner.partner_by_id(partner_id)
    return custom_response(partner_schema.dump(query_) if query_ else "not exist", 200)


@partner_api.route("/update/<int:partner_id>", methods=['PUT'])
@Auth.auth_required
def update_an_partner(partner_id, user_connected_model, user_connected_schema):
    """ add new partner """

    if user_connected_model.right == 2:
        data, error = validate_data(partner_schema, request, False)
        if error:
            return custom_response(data, 400)
        query_ = Partner.partner_by_id(partner_id)
        partner = partner_schema.dump(query_)
        logo_img, data['logo'] = request.files.get("logo"), partner['logo']
        if logo_img:
            _u_model = user_connected_model
            type_photo = logo_img.content_type
            if type_photo.rsplit('/', 1)[1] not in secure_photo:
                return custom_response("photo type is not supported", 400)
            destroy_image(partner['logo'], CLOUD_IMAGES_PARTNERS_TYPE, _u_model.fileStorage_key, _u_model.id)
            data['logo'] = upload_image(logo_img, CLOUD_IMAGES_PARTNERS_TYPE, _u_model.fileStorage_key, _u_model.id)
        query_.update(data)
        return custom_response("updated", 200)
    return custom_response("Unauthorized", 400)


@partner_api.route("/delete/<int:partner_id>", methods=['DELETE'])
@Auth.auth_required
def delete_an_partner(partner_id, user_connected_model, user_connected_schema):
    """ delete a partner """

    partner = Partner.partner_by_id(partner_id)
    if user_connected_model.right == 2 and partner:
        _u_model = user_connected_model
        destroy_image(partner.logo, CLOUD_IMAGES_PARTNERS_TYPE, _u_model.fileStorage_key, _u_model.id)
        partner.delete()
        return custom_response("deleted", 200)
    return custom_response("Unauthorized", 400)
