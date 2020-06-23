#!/usr/bin/env python3
""" shebang """

from ..app import mail
from ..models import add_in_storage

import os
import socket
import flask
from werkzeug.datastructures import FileStorage
from xhtml2pdf import pisa
from flask import render_template as r
from flask_mail import Message
from preferences import GOOGLE_BUCKET_INVOICE

template_mail = "Mail/"
reference_path_in_sources = "BeatsReferencePdf/"


def convert_html_to_pdf(html_source, output_filename):
    """

    :param html_source: the html file to convert
    :param output_filename: file handle to recieve result
    :return: return True on success and False on errors
    """
    # open output file for writing (truncated binary)
    result_file = open(os.path.join(flask.current_app.root_path, reference_path_in_sources + output_filename), "wb")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(html_source, dest=result_file)

    # close output file
    result_file.close()
    return pisa_status.err


def send_message_to_user(message_context):
    """ send a email """

    try:
        mail.send(message_context)
        return 1
    except socket.gaierror:
        return 0


def first_service(template, email,  name, service_title):
    """ Send Email after first service """

    msg = Message('Félicitation !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    msg.html = r(template_mail + template, name=name, service_title=service_title)
    return send_message_to_user(msg)


def payment_success(template, data, user_type, email):
    """ Send a email with command recap """

    msg = Message('Récaputilatif de commande !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    html_context = r(template_mail + template, data=data, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(data['reference'], html_context, msg)


def payment_refused(template, data, user_type, email):
    """ Send a email with command recap """

    msg = Message('Command réfusé !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    msg.html = r(template_mail + template, data=data, user_type=user_type)
    return send_message_to_user(msg)


def login_success(template, email, name, keys=None):
    """ Send Email because Login Success """

    msg = Message('Merci de votre inscription !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    if keys:
        msg.html = r(template_mail + template, email=email, name=name, keys=str(keys))
    else:
        msg.html = r(template_mail + template)
    return send_message_to_user(msg)


def reset_password(template, keys, email, name):
    """ Send Email because Password Reset """

    msg = Message('Demande de changement de mot de passe', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    msg.html = r(template_mail + template, keys=keys, name=name)
    return send_message_to_user(msg)


def password_updated(template, email, name):
    """ Password updated message """

    msg = Message('Changement de mot de passe avec succès', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    msg.html = r(template_mail + template, email=email, name=name)
    return send_message_to_user(msg)


def send_prestige(template, sender_name, sender_email, recipient_email, prestige, music):
    """ this is function for send prestige """

    msg = Message('Prestige money', sender='mahavonjy.cynthion@gmail.com', recipients=[recipient_email])
    msg.html = r(
        template_mail + template, sender_email=sender_email, sender_name=sender_name, prestige=prestige, music=music)
    return send_message_to_user(msg)


def canceled_by_auditor_after_accept(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email with refund details recap """

    msg = Message('Annulation de la reservation !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    html_context = r(template_mail + template, data=data, reference=reference, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(reference, html_context, msg, user_connected)


def accepted_reservation_by_artist(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email after artist accept reservation """

    msg = Message('Reservation Accepté !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
    html_context = r(template_mail + template, data=data, reference=reference, user_type=user_type)
    msg.html = html_context
    return send_message_with_attach(reference, html_context, msg, user_connected)


def canceled_reservation_by_artist(template, data, reference, email, user_type="customer", user_connected=None):
    """ Send a email after artist accept reservation """

    msg = Message('Reservation Refuser !', sender='mahavonjy.cynthion@gmail.com', recipients=[email])
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
            invoice_link = add_in_storage(GOOGLE_BUCKET_INVOICE, user_connected, file, req=True)
    os.remove(os.path.join(flask.current_app.root_path, reference_path_in_sources + recap_filename))
    send_message_to_user(msg)
    return invoice_link
