#! sources/Controller/Artists/Payment.py
""" shebang """

import stripe
import datetime
from googletrans import Translator
from flask import request, Blueprint
from auth.authentification import Auth
from preferences import BEATMAKING, KANTOBIZ
from sources.mail.SendMail import payment_success, payment_refused
from sources.models import custom_response
from sources.models.medias.media import Media
from sources.models.users.user import User
from sources.tools.tools import payment_stripe, Percent, random_string

payment_api = Blueprint('payment', __name__)
translator = Translator()
percent_purchase_price = 86.78
percent_isl_creative = 30
percent_artist_amount = 70
percent_tva = 20


def share_beats_price(beat_price):
    """ return artist_amount, tva, isl_amount """

    purchase_price = Percent(beat_price, percent_purchase_price).result
    isl_amount = round(Percent(purchase_price, percent_isl_creative).result, 2)
    tva = round(Percent(purchase_price, percent_tva).result, 2)
    artist_amount = round(Percent(purchase_price, percent_artist_amount).result, 2)

    return artist_amount, tva, isl_amount


def user_data_validator(func):
    """ decorator before payment """

    def validator():
        """ check if user data is in request """

        data = request.get_json()
        if not data.get("stripe_token"):
            return custom_response("no token stripe", 400)
        if not data.get("MyCarts"):
            return custom_response("send me the carts with key 'MyCarts'", 400)
        if not data.get("user_data"):
            return custom_response("send me the user information with key 'user_data'", 400)
        if not data["user_data"].get("name"):
            return custom_response("i need name in user information", 400)
        if not data["user_data"].get("email"):
            return custom_response("i need email in user information", 400)
        if not data["user_data"].get("address"):
            return custom_response("i need address in user information", 400)
        if not data["user_data"].get("city"):
            return custom_response("i need city in user information", 400)
        if not data["user_data"].get("postal_code"):
            return custom_response("i need postal_code in user information", 400)

        if data['user_data'].get('phone'):
            data['user_data']['phone'] = int(data['user_data'].get('phone'))
        else:
            data['user_data']['phone'] = None

        token = request.headers.get('Isl-Token')
        if token:
            data_ = Auth.decode_token(token)
            try:
                if data_.status_code == 400:
                    data["user_data"]["user_id"] = None
            except AttributeError:
                user_id = data_['data']['user_id']
                check_user = User.get_one_user(user_id)
                if not check_user:
                    data["user_data"]["user_id"] = None

        return func(data)

    return validator


@payment_api.route('/beatShop', methods=['POST'])
@user_data_validator
def purchase_beat(data):
    """

    :param data:  data is all user information
    :return: return true in payment success else, false
    """
    stripe.api_key = "sk_test_SnQS9gn3p2TRP7lrkjkpM5LN007eNS7Izg"
    payment_obj, payment_history_obj = {}, {}
    payment_reference, total_price, total_tva = random_string(20), 0.00, 0.00

    for beat_in_cart in data["MyCarts"]:
        artist_amount, tva, isl_amount = share_beats_price(beat_in_cart.get("price"))
        artist_id = Media.get_song_by_id(beat_in_cart.get("song_id")).user_id

        payment_obj['type'] = "beats"
        payment_obj['artist_id'] = artist_id
        payment_obj['amount'] = artist_amount
        payment_obj['reference'] = payment_reference
        payment_obj['licenses_name'] = beat_in_cart.get("licenses_name")
        # Payment(payment_obj).save()

        payment_history_obj['tva'] = tva
        payment_history_obj['type'] = "Beats"
        payment_history_obj['artist_id'] = artist_id
        payment_history_obj['reference'] = payment_reference
        payment_history_obj['isl_amount'] = isl_amount
        payment_history_obj['artist_amount'] = artist_amount
        payment_history_obj['ip_address'] = data['stripe_token']['client_ip']
        payment_history_obj['total_amount'] = beat_in_cart.get("price")
        payment_history_obj['licenses_name'] = beat_in_cart.get("licenses_name")
        payment_history_obj.update(data['user_data'])
        # PaymentHistory(payment_history_obj).save()

        total_tva += tva
        total_price += beat_in_cart.get("price")

    payment = payment_stripe(total_price, data['stripe_token']['id'], "Purchase Beats")
    if payment.paid:
        payment_success_send_email(data, payment_reference, total_price, total_tva)
        return custom_response("purchased", 200)
    payment_refused("PaymentRefused.html", data=data, user="customer")
    payment_refused("PaymentRefused.html", data=data, user="admin")
    return custom_response("payment refused", 400)


def payment_success_send_email(data, payment_reference, total_price, total_tva, command_information=None):
    """

    :param data: data is all user information
    :param payment_reference: the reference of the user payment
    :param total_price: total amount for paid
    :param total_tva: total tva
    :param command_information: all information with user and commant
    :return: true or false
    """

    if command_information is None:
        command_information = {}

    day = str(datetime.date.today().day)
    year = str(datetime.date.today().year)
    month = translator.translate(datetime.datetime.now().strftime("%B"), dest='fr').text.title()

    command_information['reference'] = payment_reference
    command_information['date'] = month + " " + day + ", " + year
    command_information['type'] = KANTOBIZ
    if data.get("MyCarts"):
        command_information['beats_command'] = data["MyCarts"]
        command_information['number_command'] = len(data["MyCarts"])
        command_information['type'] = BEATMAKING
    command_information['total_price'] = total_price
    command_information['total_tva'] = total_tva
    command_information['invoicing_address'] = {
        "name": data["user_data"]["name"],
        "lastname": data["user_data"]["lastname"],
        "email": data["user_data"]["email"],
        "address": data["user_data"]["address"],
        "city": data["user_data"]["city"],
        "postal_code": data["user_data"]["postal_code"],
        "phone": data["user_data"]["phone"]}

    _data = data["user_data"]
    auditor_email = _data.get("auditor_email")
    if auditor_email:
        payment_success('PaymentSuccessfull.html', data=command_information, user_type="customer", email=auditor_email)
    payment_success('PaymentSuccessfull.html', data=command_information, user_type="customer", email=_data["email"])
    payment_success('PaymentSuccessfull.html', data=command_information, user_type="admin", email=_data["artist_email"])
    return True
