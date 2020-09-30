#!/usr/bin/env python3
""" shebang """

from statistics import mean

from sources.models.artists.services.artistServices import Services
from sources.models.reservations.reservation import ReservationRSchema, Reservations
from sources.models.users.user import UserSchema
from flask import Blueprint, request, Response
from sources.models import custom_response
from auth.authentification import Auth
from sources.models.admirations.admirations import AdmireSchema
from sources.models.profiles.profile import Profiles, ProfileSchema
from sources.models.users.user import User, UserSocial
from preferences import CLOUD_IMAGES_PROFILES_TYPE, USER_AUDITOR_PRO
from sources.models.bankingDetails.banking import BankingSchema
from sources.models.artists.conditions.globals import ConditionGlobalSchema
from sources.tools.tools import check_all_user_payment_history, check_reservation_info_with_service_info, destroy_image, \
    upload_image, validate_data, \
    check_user_options_and_services
from sources.models.keyResetPassword.keyResetPasswords import ResetPassword
from sources.models.artists.history.paymentHistory import PaymentHistorySchema

profile_api = Blueprint('profile', __name__)
reservation_basic_schema = ReservationRSchema()
payment_history_schema = PaymentHistorySchema()
condition_globals_schema = ConditionGlobalSchema()
admiration_schema = AdmireSchema()
reset_password = ResetPassword()
profile_schema = ProfileSchema()
UserSocial_schema = UserSocial()
banking_schema = BankingSchema()
user_schema = UserSchema()


def create_profile(data):
    """ Create User Profile """

    profile = Profiles.get_profile(email=data.get("email"))
    if data.get("social_id"):
        profile = Profiles.get_profile(social_id=data.get("social_id"))
    if profile:
        profile.update(data)
        return profile.id
    profile = Profiles(data)
    profile.save()
    return profile.id


@profile_api.route('/my_profile', methods=['GET'])
@Auth.auth_required
def show_profile(user_connected_model, user_connected_schema):
    """ Get my Profile """

    profile = user_connected_model.profile or Profiles.get_profile(social_id=user_connected_model.social_id)

    user_condition_globals, reservation_booking_list, reservation_list, notes = {}, [], [], 0.00
    if user_connected_model.user_type != USER_AUDITOR_PRO:
        user_condition_globals = condition_globals_schema.dump(user_connected_model.condition_globals[0])
        user_reservation_list = user_connected_model.reservation_list.all()
        if user_reservation_list:
            reservation_list = [
                check_reservation_info_with_service_info(reservation_basic_schema, Services, User, r)
                for r in user_reservation_list]
    else:
        notes = mean(User.get_one_user(user_connected_model.id).stars[0].note or [0])

    user_booking_list = user_connected_model.booking_list.all()
    if user_booking_list:
        reservation_booking_list = [
            check_reservation_info_with_service_info(reservation_basic_schema, Services, User, r)
            for r in user_booking_list]

    user_banking = user_connected_model.banking
    if user_banking:
        user_banking = banking_schema.dump(user_banking[0])

    return custom_response({
        "notes": notes,
        "role": user_connected_schema['user_type'],
        "my_followings": len(user_connected_model.user.all()),
        "my_followers": len(user_connected_model.admire.all()),
        "my_profile": profile_schema.dump(profile),
        "conditions": user_condition_globals,
        "banking": user_banking or {},
        "reservations_list": reservation_list,
        "reservations_booking_list": reservation_booking_list,
        "payment_history": check_all_user_payment_history(
            user_connected_model, payment_history_schema, User, Reservations
        ),
    }, 200)


@profile_api.route('/check_other_profile/<int:profile_id>', methods=['GET'])
def check_special_profile(profile_id):
    """ Get Special Profile """

    user_profile = Profiles.get_profile(profile_id=profile_id)
    if not user_profile:
        return custom_response("Profile not found", 400)

    user_profile, user_ = profile_schema.dump(user_profile), None
    if user_profile.get('email'):
        user_ = User.get_user_by_email(user_profile.get('email'))
    else:
        user_ = User.get_user_by_email(user_profile.get('social_id'))

    user_data_needed = {
        **check_user_options_and_services(user_),
        "user_id": user_.id,
        "role": user_.user_type,
        "beats_shared": user_.medias.filter_by(genre_musical='beats').count(),
        "followings": user_.user.count(),
        "followers": user_.admire.count()
    }
    user_beats = user_.medias.filter_by(genre_musical='beats').all()
    return custom_response({
        "profile_checked": user_profile,
        "user_data": user_data_needed,
        # "user_beats": [media_schema.dump(beat) for beat in user_beats]
    }, 200)


@profile_api.route('/updateProfile', methods=['PUT'])
@Auth.auth_required
def update_profile(user_connected_model, user_connected_schema):
    """ Update my profile """

    data, error = validate_data(profile_schema, request, False)
    if error:
        return custom_response(data, 400)

    if not data.get("email") or not data.get("name"):
        return custom_response("email and name is required", 400)

    if data['email'] != user_connected_model.email and User.get_user_by_email(data['email']):
        return custom_response("email exist", 400)

    user_profile = user_connected_model.profile or Profiles.get_profile(social_id=user_connected_model.social_id)
    p_dumped = profile_schema.dump(user_profile)

    data.update(p_dumped)
    _u_model = user_connected_model
    p_photo = request.files.get('photo')
    if p_photo:
        if p_dumped["photo"]:
            destroy_image(p_dumped["photo"], CLOUD_IMAGES_PROFILES_TYPE, _u_model.fileStorage_key, _u_model.id)
        data['photo'] = upload_image(p_photo, CLOUD_IMAGES_PROFILES_TYPE, _u_model.fileStorage_key, _u_model.id)

    c_photo = request.files.get('cover_photo')
    if c_photo:
        if p_dumped["cover_photo"]:
            destroy_image(p_dumped["cover_photo"], CLOUD_IMAGES_PROFILES_TYPE, _u_model.fileStorage_key, _u_model.id)
        data['cover_photo'] = upload_image(c_photo, CLOUD_IMAGES_PROFILES_TYPE, _u_model.fileStorage_key, _u_model.id)

    user_connected_schema["name"], user_connected_schema["email"] = data['name'], data['email']
    user_connected_model.update(user_connected_schema)
    user_profile.update(data)
    new_user_profile = user_connected_model.profile or Profiles.get_profile(social_id=user_connected_model.social_id)
    return custom_response(profile_schema.dump(new_user_profile), 200)
