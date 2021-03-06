#!/usr/bin/env python3
""" shebang """

import cloudinary.uploader
from ..app import mail

import os
import socket
import flask
from preferences.env import app_config
from werkzeug.datastructures import FileStorage
from xhtml2pdf import pisa
from flask import render_template as r
from flask_mail import Message
from preferences import CLOUD_INVOICE

template_mail = "Mail/"
reference_path_in_sources = "beatsReferencePdf/"
sender_mail = app_config[os.getenv('FLASK_ENV')].MAIL_USERNAME


def convert_html_to_pdf(html_source, output_filename):
    """

    :param html_source: the html file to convert
    :param output_filename: file handle to recieve result
    :return: return True on success and False on errors
    """
    # open output file for writing (truncated binary)
    try:
        result_file = open(os.path.join(flask.current_app.root_path, reference_path_in_sources + output_filename), "wb")

        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(html_source, dest=result_file)

        # close output file
        result_file.close()
        return pisa_status.err
    except FileNotFoundError:
        pass


def send_message_to_user(message_context):
    """ send a email """

    try:
        mail.send(message_context)
        return 1
    except socket.gaierror:
        return 0


def first_service(template, recipient_email, name, service_title):
    """ Send Email after first service """

    msg = Message('Félicitation !', sender=sender_mail, recipients=[recipient_email])
    msg.html = r(template_mail + template, name=name, service_title=service_title)
    return send_message_to_user(msg)


def payment_success(template, data, user_type, email):
    """ Send a email with command recap """

    msg = Message('Récaputilatif de commande !', sender=sender_mail, recipients=[email])
    html_context = r(template_mail + template, data=data, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(data['reference'], html_context, msg)


def payment_refused(template, data, user_type, email):
    """ Send a email with command recap """

    msg = Message('Command réfusé !', sender=sender_mail, recipients=[email])
    msg.html = r(template_mail + template, data=data, user_type=user_type)
    return send_message_to_user(msg)


def login_success(template, email, name, keys=None):
    """ Send Email because Login Success """

    msg = Message('Merci de votre inscription !', sender=sender_mail, recipients=[email])
    if keys:
        msg.html = r(template_mail + template, email=email, name=name, keys=str(keys))
    else:
        msg.html = r(template_mail + template)
    return send_message_to_user(msg)


def reset_password(template, keys, email, name):
    """ Send Email because Password Reset """

    msg = Message('Demande de changement de mot de passe', sender=sender_mail, recipients=[email])
    msg.html = r(template_mail + template, keys=keys, name=name)
    return send_message_to_user(msg)


def password_updated(template, email, name):
    """ Password updated message """

    msg = Message('Changement de mot de passe avec succès', sender=sender_mail, recipients=[email])
    msg.html = r(template_mail + template, email=email, name=name)
    return send_message_to_user(msg)


def send_prestige(
        template,
        reference,
        sender_name,
        sender_email,
        recipient_email,
        prestige,
        beat_title=None,
        service_title=None):
    """ this is function for send prestige """

    msg = Message('Prestige', sender=sender_mail, recipients=[recipient_email])
    msg.html = r(
        template_mail + template,
        prestige=prestige,
        sender_name=sender_name,
        sender_email=sender_email,
        service_title=service_title,
        beat_title=beat_title,
        reference=reference,
    )
    return send_message_to_user(msg)


def canceled_by_auditor_after_accept(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email with refund details recap """

    msg = Message('Annulation de la reservation !', sender=sender_mail, recipients=[email])
    html_context = r(template_mail + template, data=data, reference=reference, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(reference, html_context, msg, user_connected)


def accepted_reservation_by_artist(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email after artist accept reservation """

    msg = Message('Reservation Accepté !', sender=sender_mail, recipients=[email])
    html_context = r(template_mail + template, data=data, reference=reference, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(reference, html_context, msg, user_connected)


def canceled_reservation_by_artist(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email after artist accept reservation """

    msg = Message('Reservation Refuser !', sender=sender_mail, recipients=[email])
    html_context = r(template_mail + template, data=data, reference=reference, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(reference, html_context, msg, user_connected)


def send_message_with_attach(reference, html_context, msg, user_connected=None):
    invoice_link = ""
    recap_filename = "Ref_" + reference + ".pdf"
    convert_html_to_pdf(html_context, recap_filename)
    with flask.current_app.open_resource(reference_path_in_sources + recap_filename) as fp:
        msg.attach(reference_path_in_sources + recap_filename, "application/pdf", fp.read())
    if user_connected:
        with flask.current_app.open_resource(reference_path_in_sources + recap_filename, 'rb') as fp:
            file = FileStorage(fp)
            user_id = user_connected['id']
            fileStorage_key = user_connected['fileStorage_key']
            invoice_link = cloudinary.uploader.upload(
                file,
                public_id=fileStorage_key + str(user_id) + file.filename.split(".")[0],
                folder=CLOUD_INVOICE + "/" + fileStorage_key + str(user_id)
            )['secure_url']
    os.remove(os.path.join(flask.current_app.root_path, reference_path_in_sources + recap_filename))
    send_message_to_user(msg)
    return invoice_link
