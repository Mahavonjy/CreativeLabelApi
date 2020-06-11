#!/usr/bin/env python3
""" shebang """

from sources.models.partnership.partnership import Partner, PartnerSchema
from sources.models.users.user import UserSchema
from sources.tools.tools import validate_data
from auth.authentification import Auth
from preferences import defaultDataConf, GOOGLE_BUCKET_IMAGES
from sources.models import custom_response
from sources.models import add_in_storage
from flask import Blueprint, request
from google.cloud import storage
import google

partner_api = Blueprint('partners', __name__)
secure_photo = defaultDataConf.media_allowed_Photos_Extensions
bucket_images = GOOGLE_BUCKET_IMAGES
partner_schema = PartnerSchema()
user_schema = UserSchema()


def update_photo(logo_img, partner, ser_user, delete=False):
    """ update photo in storage """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_images)
    b_n = "/".join(partner['logo'].split('/')[-3:])
    blob = bucket.blob(b_n)

    try:
        blob.delete()
    except TypeError:
        pass
    except google.api_core.exceptions.NotFound:
        pass

    if delete:
        return
    return add_in_storage(bucket_images, ser_user, logo_img, "partners/")


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
        type_photo = logo_img.content_type
        file_type = type_photo.rsplit('/', 1)[1]
        if file_type not in secure_photo:
            return custom_response("photo type is not supported", 400)
        data['logo'] = add_in_storage(bucket_images, user_connected_schema, logo_img, "partners/")
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
            type_photo = logo_img.content_type
            file_type = type_photo.rsplit('/', 1)[1]
            if file_type not in secure_photo:
                return custom_response("photo type is not supported", 400)
            data['logo'] = update_photo(logo_img, partner, user_connected_schema)
        query_.update(data)
        return custom_response("updated", 200)
    return custom_response("Unauthorized", 400)


@partner_api.route("/delete/<int:partner_id>", methods=['DELETE'])
@Auth.auth_required
def delete_an_partner(partner_id, user_connected_model, user_connected_schema):
    """ delete a partner """

    if user_connected_model.right == 2:
        query_ = Partner.partner_by_id(partner_id)
        update_photo(None, partner_schema.dump(query_), None, True)
        query_.delete()
        return custom_response("deleted", 200)
    return custom_response("Unauthorized", 400)
