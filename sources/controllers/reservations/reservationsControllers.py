#!/usr/bin/env python3
""" shebang """

import stripe
import datetime
from auth.authentification import Auth
from preferences import KANTOBIZ, PENDING, DECLINED, ACCEPTED
from sources.controllers.artists.payments.paymentsControllers import payment_success_send_email, translator
from sources.tools.tools import check_all_user_payment_history, check_reservation_info_with_service_info, \
    payment_stripe, random_string, validate_data
from sources.mail.SendMail import payment_refused, canceled_by_auditor_after_accept, accepted_reservation_by_artist, \
    canceled_reservation_by_artist
from sources.models.artists.history.paymentHistory import PaymentHistory, PaymentHistorySchema
from sources.models.reservations.reservation import Reservations, ReservationSchema, ReservationRSchema
from sources.models.artists.services.artistServices import Services, ServiceSchema
from sources.models import custom_response
from flask import Blueprint, request
from sources.models.users.user import User, UserSchema

reservation_api = Blueprint('reservations', __name__)
service_schema = ServiceSchema()
payment_history_schema = PaymentHistorySchema()
reservation_basic_schema = ReservationRSchema()
reservation_schema = ReservationSchema()
user_schema = UserSchema()
percent_isl_creative = 20.00
percent_tva = 20.00
day = str(datetime.date.today().day)
year = str(datetime.date.today().year)
month = translator.translate(datetime.datetime.now().strftime("%B"), dest='fr').text.title()


@reservation_api.route('/check_total_price', methods=['POST'])
def check_price_details(price=None, ht_price=None):
    """ return artist_amount, tva, isl_amount """

    data = request.get_json()

    if not data.get("price") and not ht_price:
        return custom_response("need price", 400)

    if not ht_price:
        price = data.get("price")

    ht_price = ht_price or price
    tva = round(float(ht_price * (1 + percent_tva / 100.00)) - ht_price, 2)
    isl_amount = round(float(ht_price * (1 + percent_isl_creative / 100.00)) - ht_price, 2)

    if price:
        return custom_response({
            "tva": tva,
            "ht_price": ht_price,
            "isl_amount": isl_amount,
            "total_amount": float(ht_price + isl_amount + tva),
        }, 200)
    return ht_price, tva, isl_amount


@reservation_api.route('/new', methods=['POST'])
@Auth.auth_required
def create_a_new_reservation(user_connected_model, user_connected_schema):
    """ """

    data, error = validate_data(reservation_schema, request)
    if error:
        return custom_response(data, 400)

    payment_reference = random_string(20)
    stripe.api_key = "sk_test_SnQS9gn3p2TRP7lrkjkpM5LN007eNS7Izg"
    artist_amount, total_tva, isl_amount = check_price_details(ht_price=data["total_amount"])
    total_amount = float(isl_amount + total_tva + artist_amount)

    payment_history_obj = {
        "paid": False,
        "tva": total_tva,
        "name": data["name"],
        "email": data["email"],
        "city": data["city"],
        "postal_code": data["postal_code"],
        "phone": data["phone"],
        'address': data["address"],
        'type': KANTOBIZ,
        'buyer_id': user_connected_model.id,
        'artist_id': data["artist_owner_id"],
        'reference': payment_reference,
        'isl_amount': isl_amount,
        'artist_amount': artist_amount,
        'ip_address': None,
        'total_amount': total_amount
    }

    payment_history_to_save = PaymentHistory(payment_history_obj)
    payment_history_to_save.save()

    artist = User.get_one_user(data["artist_owner_id"])
    data["artist_email"] = artist.email

    # payment = payment_stripe(total_amount, data['stripe_token']['id'], "Purchase Service KantoBiz")

    if data["email"] != user_connected_schema["email"]:
        data["auditor_email"] = user_connected_schema["email"]

    # if payment.paid:
    new_reservation = Reservations({
        "event": data["event"],
        "status": PENDING,
        "address": data["address"],
        "total_amount": total_amount,
        "event_date": data["event_date"],
        "services_id": data["services_id"],
        "artist_owner_id": data["artist_owner_id"],
        "options_id_list": data["options_id_list"],
        "payment_history_id": payment_history_to_save.id,
        "auditor_who_reserve_id": user_connected_model.id,
        "refund_policy": artist.condition_globals[0].refund_policy
    })
    new_reservation.save()
    payment_success_send_email({"user_data": data}, payment_reference, total_amount, total_tva)
    return custom_response(reservation_basic_schema.dump(new_reservation), 200)

    # auditor_email = data.get("auditor_email")
    # if auditor_email:
    #     payment_refused('PaymentRefused.html', data=data, user_type="customer", email=auditor_email)
    # payment_refused("PaymentRefused.html", data=data, user_type="customer", email=data["email"])
    # payment_refused("PaymentRefused.html", data=data, user_type="admin", email=data["artist_email"])
    # return custom_response("payment refused", 400)


@reservation_api.route('/artist_decline/<int:reservation_id>', methods=['PUT'])
@Auth.auth_required
def artist_decline_reservation(reservation_id, user_connected_model, user_connected_schema):
    """

    Args:
        reservation_id:
        user_connected_model:
        user_connected_schema:

    Returns:

    """

    user_reservation = user_connected_model.reservation_list.filter_by(id=reservation_id).first()
    if user_reservation:
        reservation_s = reservation_basic_schema.dump(user_reservation)

        if reservation_s["status"] == DECLINED:
            return custom_response("already declined", 400)

        if reservation_s["status"] == ACCEPTED:
            # refund
            service_s = service_schema.dump(user_reservation.service)
            payment_history_0bj = payment_history_schema.dump(user_reservation.payment_history)
            reference = payment_history_0bj["reference"]

            data = {
                "service": service_s,
                "date": month + " " + day + ", " + year,
                "auditor": user_schema.dump(User.get_one_user(reservation_s["auditor_who_reserve_id"])),
                "reservation": reservation_s,
                "artist_name": user_connected_model.name,
                "artist_email": user_connected_model.email,
                "invoicing_address": payment_history_0bj
            }

            invoice = canceled_reservation_by_artist(
                "PaymentRefundByArtistRefused.html", data=data, reference=reference,
                user_type="customer", email=payment_history_0bj["email"], user_connected=user_connected_schema)

            canceled_reservation_by_artist(
                "PaymentRefundByArtistRefused.html", data=data, reference=reference,
                user_type="artist", email=user_connected_model.email)

            reservation_s["status"] = DECLINED
            reservation_s["invoice"] = invoice
            user_reservation.update(reservation_s)
            payment_history_0bj["refund"] = True
            user_reservation.payment_history.update(payment_history_0bj)
            return custom_response_after_update(user_connected_model, user_reservation)

        reservation_s["status"] = DECLINED
        user_reservation.update(reservation_s)
        return custom_response(
            check_reservation_info_with_service_info(reservation_basic_schema, Services, User, user_reservation, True
                                                     ), 200)
    return custom_response("reservation not found", 404)


@reservation_api.route('/artist_accept/<int:reservation_id>', methods=['PUT'])
@Auth.auth_required
def artist_accept_reservation(reservation_id, user_connected_model, user_connected_schema):
    """

    Args:
        reservation_id:
        user_connected_model:
        user_connected_schema:

    Returns:

    """

    user_reservation = user_connected_model.reservation_list.filter_by(id=reservation_id).first()
    if user_reservation:
        reservation_s = reservation_basic_schema.dump(user_reservation)

        if reservation_s["status"] == DECLINED:
            return custom_response("already declined", 400)

        if reservation_s["status"] == ACCEPTED:
            return custom_response("already accepted", 400)

        # refund
        service_s = service_schema.dump(user_reservation.service)
        payment_history_0bj = payment_history_schema.dump(user_reservation.payment_history)
        reference = payment_history_0bj["reference"]

        data = {
            "service": service_s,
            "date": month + " " + day + ", " + year,
            "auditor": user_schema.dump(User.get_one_user(reservation_s["auditor_who_reserve_id"])),
            "reservation": reservation_s,
            "artist_name": user_connected_model.name,
            "artist_email": user_connected_model.email,
            "invoicing_address": payment_history_0bj
        }

        reservation_s["invoice"] = accepted_reservation_by_artist(
            "ArtistAcceptReservation.html", data=data, reference=reference,
            user_type="customer", email=payment_history_0bj["email"], user_connected=user_connected_schema)

        accepted_reservation_by_artist(
            "ArtistAcceptReservation.html", data=data, reference=reference,
            user_type="artist", email=user_connected_model.email)

        reservation_s["status"] = ACCEPTED
        user_reservation.update(reservation_s)
        payment_history_0bj["service_fee"] = True
        user_reservation.payment_history.update(payment_history_0bj)
        return custom_response_after_update(user_connected_model, user_reservation)
    return custom_response("reservation not found", 404)


@reservation_api.route('/auditor_decline/<int:reservation_id>', methods=['PUT'])
@Auth.auth_required
def auditor_decline_reservation(reservation_id, user_connected_model, user_connected_schema):
    """

    Args:
        reservation_id:
        user_connected_model:
        user_connected_schema:

    Returns:

    """

    user_reservation = user_connected_model.booking_list.filter_by(id=reservation_id).first()

    if user_reservation:
        reservation_s = reservation_basic_schema.dump(user_reservation)

        if reservation_s["status"] == DECLINED:
            return custom_response("already declined", 400)

        if reservation_s["status"] == ACCEPTED:
            service_s = service_schema.dump(user_reservation.service)
            artist = User.get_one_user(service_s["user_id"])
            payment_history_0bj = payment_history_schema.dump(user_reservation.payment_history)
            reference = payment_history_0bj["reference"]

            data = {
                "service": service_s,
                "refunded": 0.00,
                "date": month + " " + day + ", " + year,
                "auditor": user_connected_schema,
                "reservation": reservation_s,
                "artist_name": artist.name,
                "artist_email": artist.email,
                "invoicing_address": payment_history_0bj
            }

            # do not forget refund
            reservation_s["invoice"] = canceled_by_auditor_after_accept(
                "CanceledByAuditorAfterAccept.html", data=data, reference=reference,
                user_type="customer", email=payment_history_0bj["email"], user_connected=user_connected_schema)

            canceled_by_auditor_after_accept(
                "CanceledByAuditorAfterAccept.html", data=data, reference=reference,
                user_type="artist", email=artist.email)

            reservation_s["status"] = DECLINED
            payment_history_0bj["refund"] = True
            user_reservation.payment_history.update(payment_history_0bj)
            user_reservation.update(reservation_s)
            return custom_response_after_update(user_connected_model, user_reservation)

        reservation_s["status"] = DECLINED
        user_reservation.update(reservation_s)
        return custom_response_after_update(user_connected_model, user_reservation)

    return custom_response("reservation not found", 404)


def custom_response_after_update(user_connected_model, user_reservation):
    """

    Args:
        user_connected_model:
        user_reservation:

    Returns:

    """

    tmp = check_reservation_info_with_service_info(reservation_basic_schema, Services, User, user_reservation, True)
    tmp.update({"payment_history": check_all_user_payment_history(
        user_connected_model, payment_history_schema, User, Reservations)})
    return custom_response(tmp, 200)
