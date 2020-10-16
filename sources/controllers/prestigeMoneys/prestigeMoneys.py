#!/usr/bin/env python3
""" shebang """

from sources.models.artists.services.artistServices import Services
from sources.models.medias.media import Media
from sources.models.prestigeMoneys.prestigeMoneys import Prestige, PrestigeSchema
from sources.models.users.user import User, UserSchema
from sources.tools.tools import random_string
from auth.authentification import Auth
from sources.mail.SendMail import send_prestige
from sources.models import custom_response
from preferences import PRESTIGE_ALLOWED_TYPE
from flask import Blueprint

prestige_api = Blueprint('prestige', __name__)
prestige_schema = PrestigeSchema()


def prestige_data(sender_id=None, recipient_id=None, prestige=None, beat_id=None, service_id=None):
    """

    Args:
        sender_id:
        recipient_id:
        prestige:
        beat_id:
        service_id:

    Returns:

    """

    return dict(
        key_share=random_string(20),
        beat_id=beat_id,
        service_id=service_id,
        recipient_id=recipient_id,
        sender_id=sender_id,
        prestige=prestige
    )


@prestige_api.route('/<string:prestige>/beat/<int:beat_id>', methods=['POST'])
@prestige_api.route('/<string:prestige>/service/<int:service_id>', methods=['POST'])
@Auth.auth_required
def send_prestige_email(user_connected_model, user_connected_schema, prestige, beat_id=None, service_id=None):
    """

    Args:
        prestige:
        beat_id:
        service_id:
        user_connected_model:
        user_connected_schema:
    """

    if prestige not in list(PRESTIGE_ALLOWED_TYPE):
        return custom_response("prestige type not found", 400)

    prestige = PRESTIGE_ALLOWED_TYPE[prestige]
    mail_data = dict(template="prestige.html")

    if beat_id:
        beat = Media.get_song_by_id(beat_id)
        if not beat:
            return custom_response("beat not found", 400)

        recipient = User.get_one_user(beat.user_id)
        mail_data.update(dict(beat_title=beat.title))

    else:
        service = Services.get_by_service_id(service_id)
        if not service:
            return custom_response("service not found", 400)

        recipient = User.get_one_user(service.user_id)
        mail_data.update(dict(service_title=service.title))

    if user_connected_model.email == recipient.email:
        return custom_response('Unauthorized', 400)

    data = prestige_data(
        sender_id=user_connected_model.id,
        recipient_id=recipient.id,
        service_id=service_id,
        prestige=prestige,
        beat_id=beat_id,
    )
    mail_data.update(dict(
        reference=data['key_share'],
        sender_name=user_connected_model.name,
        sender_email=user_connected_model.email,
        recipient_email=recipient.email,
        prestige=prestige)
    )
    Prestige(data).save()
    send_prestige(**mail_data)

    return custom_response("success", 200)


@prestige_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_my_prestige_send(user_connected_model, user_connected_schema):
    """

    Args:
        user_connected_model:
        user_connected_schema:
    """

    all_prestige = {"sends": [], "receipted": []}
    sends = user_connected_model.prestige_sends.all()
    all_prestige["sends"] = [prestige_schema.dump(send) for send in sends]
    receipted = user_connected_model.prestige_receipts.all()
    all_prestige["receipted"] = [prestige_schema.dump(receipt) for receipt in receipted]

    return custom_response(all_prestige, 200)
