#!/usr/bin/env python3
""" shebang """

from sources.controllers.artists.materials.materialsControllers import create_new_materials_for_new_services
from sources.controllers.artists.services.servicesControllers import check_galleries_files
from sources.controllers.users import token_return
from sources.models.users.user import User, UserSchema, GetMail, GetPassword, UserSocial
from sources.models.keyResetPassword.keyResetPasswords import KeyResetPassword, ResetPassword, GetKeys
from sources.controllers.artists.contractBeatMaking.contractBeatmaking import create_all_default_contract
from sources.controllers.artists.condtitions.conditionsControllers import generate_condition_globals
from sources.mail.SendMail import login_success, reset_password, password_updated, first_service
from sources.controllers.stars.starsControllers import generate_basic_stars
from sources.models.profiles.profile import Profiles, ProfileSchema
from sources.models.artists.services.artistServices import Services
from sources.models.revokeToken.tokenRevoke import RevokedTokenModel
from sources.controllers.profiles.profilesControllers import create_profile
from preferences.defaultData import type_of_isl_artist
from sources.tools.tools import random_int, random_string, validate_data
from preferences import USER_ARTIST_BEATMAKER, USER_AUDITOR_PRO
from auth.authentification import Auth
from sources.models import custom_response
from preferences.env import Production

from requests_oauthlib import OAuth2Session
from flask import request, Blueprint
from flask import session
import facebook as f

user_api = Blueprint('users', __name__)
reset_pass_schema = ResetPassword()
keys_validator_schema = GetKeys()
profile_schema = ProfileSchema()
user_password = GetPassword()
user_schema = UserSchema()
user_social = UserSocial()
user_email = GetMail()


@user_api.route('/register', methods=['POST'])
def register():
    """ Create User Function """

    data, error = validate_data(user_schema, request, return_dict=False)
    if error:
        return custom_response(data, 400)

    if User.get_user_by_email(data.get('email')):
        return custom_response("Email already exist", 400)

    data.update({'fileStorage_key': random_string(10), 'profile_id': create_profile(data)})
    new_user = User(data)
    new_user.save()
    keys = random_int()
    KeyResetPassword(dict(keys=keys, user_id=new_user.id)).save()
    generate_basic_stars(user_id=new_user.id)
    if data.get('services'):
        generate_condition_globals(new_user.id)
        if data.get('user_type') == USER_ARTIST_BEATMAKER:
            create_all_default_contract(new_user.id)
        data['services']['user_id'] = new_user.id
        data['services']['galleries'] = check_galleries_files(request, new_user)
        data['services']['materials_id'] = create_new_materials_for_new_services()
        new_service = Services(data['services'])
        new_service.save()
        generate_basic_stars(service_id=new_service.id)
        first_service('FirstService.html', data["email"], data["name"], data['services']["title"])
    login_success('LoginSuccess.html', data["email"], data["name"], keys)
    return token_return(Auth.generate_token(new_user.id), data.get('name'), data.get('email'))


@user_api.route('/if_token_valide', methods=['GET'])
@Auth.auth_required
def check_if_token_is_valid(user_connected_model, user_connected_schema):
    """ Check if token user is valid or not """

    return custom_response("token valid", 200)


@user_api.route('/if_choice_user_status', methods=['GET'])
@Auth.auth_required
def if_choice_user_status(user_connected_model, user_connected_schema):
    """ Check if user already chosen status or not """

    if user_connected_model.user_genre_list:
        return custom_response("success", 200)
    return custom_response("no choice music genre", 400)


@user_api.route('/update_user_to/<string:type_name>', methods=['PUT'])
@Auth.auth_required
def update_user_to_artist_or_manager(type_name, user_connected_model, user_connected_schema):
    """ Update user to artist """

    if type_name not in [k.get('name') for k in type_of_isl_artist]:
        return custom_response("artist type not Allowed", 400)

    if user_connected_schema['user_type'] == USER_AUDITOR_PRO:
        user_connected_schema['user_type'] = type_name
        user_connected_schema["if_choice"] = 1
        user_connected_model.update(user_connected_schema)
        if type_name == USER_ARTIST_BEATMAKER:
            create_all_default_contract(user_connected_model.id)
        generate_condition_globals(user_connected_model.id)
        return custom_response("User status changed to artist", 200)

    return custom_response("You are already artist right now", 400)


@user_api.route('/gCallback', methods=['POST'])
def callback():
    """ My Callback function for google login and register """

    google = OAuth2Session(Production.CLIENT_ID, token=request.get_json())
    resp = google.get(Production.USER_INFO)
    if resp.status_code == 200:
        user_data, data = resp.json(), {}
        user_in_db = User.get_user_by_social_id(user_data['id'])
        if user_in_db:
            token = Auth.generate_token(user_in_db.id)
            _user_profile = Profiles.get_profile(social_id=user_data['id'])
            return token_return(token, user_in_db.name, user_in_db.email, _user_profile.photo)

        if User.get_user_by_email(user_data['email']):
            return custom_response("Email already exist", 400)

        data.update({
            'social': "google",
            'name': user_data['family_name'],
            'social_id': user_data['id'],
            'fileStorage_key': random_string(10),
            'email': user_data['email'],
            'photo': user_data['picture']
        })
        user = User(data)
        create_profile(data)
        user.save()
        create_all_default_contract(user.id)
        token = Auth.generate_token(user.id)
        generate_basic_stars(user_id=user.id)
        login_success('LoginSuccess.html', email=data['email'], name=data["name"])
        return token_return(token, data.get('name'), data.get('email'), data.get('photo'))

    return custom_response("Unauthorized, Could not fetch your information.", 400)


@user_api.route('/login/authorized', methods=['POST'])
def facebook_authorized():
    """Authorize facebook login."""

    data = request.get_json()
    session['facebook_token'] = {"Type": data['token_type'], "access_token": data['accessToken']}
    graph = f.GraphAPI(data['accessToken'])
    profile = graph.get_object('me', **{'fields': 'id, name, email, picture'})
    data.clear()
    data = dict(
        photo=profile['picture']['data']['url'],
        name=profile['name'],
        social_id=profile['id'],
        social="facebook",
        password=None,
        email=profile.get('email'),
        fileStorage_key=random_string(10),
    )
    user_in_db = User.get_user_by_social_id(profile['id'])
    if user_in_db:
        token = Auth.generate_token(user_social.dump(user_in_db)["id"])
        return token_return(token, data.get('name'), data.get('email'))

    if data['email']:
        login_success('LoginSuccess.html', email=data.get('email'), name=data.get('name'))

    create_profile(data)
    profile_info = profile_schema.dump(Profiles.get_profile(data.get('social_id')))
    data['fileStorage_key'], data['profile_id'] = random_string(10), profile_info.get('id')
    user = User(data)
    user.save()
    create_all_default_contract(user.id)
    return token_return(Auth.generate_token(user_schema.dump(user)['id']), data.get('name'), data.get('email'))


@user_api.route('/get_if_keys_validate', methods=['POST'])
def validation_keys():
    """ get if user keys is validate for reset password """

    data, error = validate_data(keys_validator_schema, request)
    if error:
        return custom_response(data, 400)

    reset_pass = User.get_user_by_email(data.get('email')).reset_password_key
    try:
        if reset_pass_schema.dump(reset_pass[0])["keys"] == int(data["keys"]):
            reset_pass[0].delete()
            return custom_response("validate", 200)
        return custom_response("Keys invalid", 400)
    except IndexError:
        return custom_response("already used", 400)


@user_api.route('/reset_password', methods=['PUT'])
def reset_password_after_validate_keys():
    """ Reset Password """

    data, error = validate_data(user_password, request)
    if error:
        return custom_response(data, 400)

    if not data.get('password'):
        return custom_response("Password could not be null", 400)

    user_in_db = User.get_user_by_email(data.get('email'))
    if user_in_db:
        user_in_db.update_password(data.get('password'))
        password_updated('PasswordUpdated.html', email=data.get('email'), name=user_in_db.name)
        return custom_response("password changed", 200)

    return custom_response("Unauthorized", 400)


@user_api.route('/get_mail', methods=['POST'])
def get_mail():
    """ Get Email """

    data, error = validate_data(user_email, request)
    if error:
        return custom_response(data, 400)

    user = User.get_user_by_email(data.get('email'))
    if user:
        keys = random_int()
        reset_pass = user.reset_password_key
        user_id = user_schema.dump(User.get_user_by_email(data.get('email')))['id']

        if reset_password('RequestPassword.html', keys, email=data.get('email'), name=user.name):
            if reset_pass:
                data_user = reset_pass_schema.dump(reset_pass[0])
                data_user.update({'keys': keys, 'password_reset': 1})
                reset_pass[0].update(data_user)
            else:
                KeyResetPassword(dict(keys=keys, user_id=user_id, password_reset=1)).save()

            return custom_response('Email send', 200)

        return custom_response("Connexion Failed", 400)

    return custom_response("Email not Found", 400)


@user_api.route('/check_password', methods=['POST'])
@Auth.auth_required
def check_user_password(user_connected_model, user_connected_schema):

    data = request.get_json()
    if not data.get("password"):
        return custom_response("send me the password", 404)

    if not user_connected_model.check_hash(data.get("password")):
        return custom_response("not matched", 400)

    return custom_response("matched", 200)


@user_api.route('/login', methods=['POST'])
def login():
    """ function for login in api """

    data, error = validate_data(user_password, request)
    if error:
        return custom_response(data, 400)

    user = User.get_user_by_email(data['email'])

    try:
        if user.reset_password_key:
            return custom_response("Active your account", 400)

    except AttributeError:
        pass

    try:
        response = 'invalid email' if not user else 'invalid password' if not user.check_hash(data['password']) else 0
        if response:
            return custom_response(response, 400)

    except TypeError:
        pass

    ser_user = user_schema.dump(user)
    token = Auth.generate_token(ser_user.get('id'))
    if ser_user['email']:
        user_profile = profile_schema.dump(Profiles.get_profile(ser_user.get('email')))

        if user_profile.get('photo'):
            return token_return(token, ser_user['name'], data['email'], user_profile['photo'])

    return custom_response({'token': token, 'name': ser_user['name'], 'email': data['email']}, 200)


@user_api.route('/logout', methods=['DELETE'])
@Auth.auth_required
def logout(user_connected_model, user_connected_schema):
    """ add token in blacklist """

    RevokedTokenModel(request.headers['Isl_Token']).save()
    return custom_response('logout', 200)
