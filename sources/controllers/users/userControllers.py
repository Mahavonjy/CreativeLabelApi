#!/usr/bin/env python3
""" shebang """

from sources.controllers.artists.materials.materialsControllers import create_new_materials_for_new_services
from sources.controllers.artists.services.servicesControllers import check_galleries_files
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
from preferences.defaultDataConf import type_of_isl_artist
from sources.tools.tools import validate_data
from sources.controllers import create_artist_story
from preferences import USER_ARTIST_BEATMAKER
from auth.authentification import Auth
from sources.controllers import random_string
from sources.models import custom_response
from preferences.config import Production

from requests_oauthlib import OAuth2Session
from flask import request, Blueprint
from flask import session
import facebook as f
import random

user_api = Blueprint('users', __name__)
reset_pass_schema = ResetPassword()
keys_validator_schema = GetKeys()
profile_schema = ProfileSchema()
user_password = GetPassword()
user_schema = UserSchema()
user_social = UserSocial()
user_email = GetMail()


def token_return(token=None, name=None, email=None, photo=None):
    """ token return for my all register or login """

    return custom_response({'token': token, 'name': name, 'email': email, 'photo': photo}, 200)


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

    if not user_connected_schema['artist']:
        user_connected_schema['artist'] = 1
        user_connected_schema['user_type'] = type_name
        user_connected_schema["if_choice"] = 1
        user_connected_model.update(user_connected_schema)
        create_artist_story(user_connected_model.id)
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

        data["social"] = "google"
        data["fileStorage_key"] = random_string(10)
        data["name"] = user_data['family_name']
        data["social_id"] = user_data['id']
        data["email"] = user_data['email']
        data["photo"] = user_data['picture']
        user = User(data)
        create_profile(data)
        user.save()
        create_artist_story(user.id)
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
    args = {'fields': 'id, name, email, picture'}
    profile = graph.get_object('me', **args)
    data.clear()
    data["photo"] = profile['picture']['data']['url']
    data["name"], data["social_id"], data["social"] = profile['name'], profile['id'], "facebook"
    data["fileStorage_key"] = random_string(10)
    data["password"], data['email'] = None, profile.get('email')
    user_in_db = User.get_user_by_social_id(profile['id'])
    if user_in_db:
        token = Auth.generate_token(user_social.dump(user_in_db)["id"])
        return token_return(token, data.get('name'), data.get('email'))
    if data['email']:
        login_success('LoginSuccess.html', email=data.get('email'), name=data.get('name'))
    create_profile(data)
    profile_info = profile_schema.dump(Profiles.get_profile(data.get('social_id')))
    data['fileStorage_key'], data['profile_id'] = random_string(10), profile_info.get('id')
    # the user is artist
    data['artist'] = 1
    user = User(data)
    user.save()
    create_artist_story(user.id)
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
    user_in_db = User.get_user_by_email(data.get('email'))
    if user_in_db:
        user_in_db.update_password(data.get('password'))
        password_updated('PasswordUpdated.html', email=data.get('email'), name=user_in_db.name)
        return login(connect=data)
    return custom_response("Unauthorized", 400)


@user_api.route('/get_mail', methods=['POST'])
def get_mail():
    """ Get Email """

    data, error = validate_data(user_email, request)
    if error:
        return custom_response(data, 400)
    user = User.get_user_by_email(data.get('email'))
    if user:
        user_id = user_schema.dump(User.get_user_by_email(data.get('email')))['id']
        keys, reset_pass = random.randint(1111, 9999) * 9999, user.reset_password_key
        if reset_password('RequestPassword.html', keys, email=data.get('email'), name=user.name):
            if reset_pass:
                data_user = reset_pass_schema.dump(reset_pass[0])
                data_user['keys'], data_user['password_reset'] = keys, 1
                reset_pass[0].update(data_user)
            else:
                KeyResetPassword(dict(keys=keys, user_id=user_id, password_reset=1)).save()
            return custom_response('Email send', 200)
        return custom_response("Connexion Failed", 400)
    return custom_response("Email not Found", 400)


@user_api.route('/register', methods=['POST'])
def register():
    """ Create User Function """

    data, error = validate_data(user_schema, request, return_dict=False)
    if error:
        return custom_response(data, 400)
    if User.get_user_by_email(data.get('email')):
        return custom_response("Email already exist", 400)
    create_profile(data)
    profile_id = profile_schema.dump(Profiles.get_profile(data.get('email')))['id']
    data['fileStorage_key'], data['profile_id'], keys = random_string(10), profile_id, random.randint(1111, 9999) * 9999
    User(data).save()
    user = user_schema.dump(User.get_user_by_email(data.get('email')))
    KeyResetPassword(dict(keys=keys, user_id=user.get('id'))).save()
    generate_basic_stars(user_id=user.get('id'))
    if data.get('services'):
        create_artist_story(user.get('id'))
        generate_condition_globals(user.get('id'))
        if data.get('user_type') == USER_ARTIST_BEATMAKER:
            create_all_default_contract(user.get('id'))
        data['artist'] = 1
        data['services']['user_id'] = user.get('id')
        data['services']['galleries'] = check_galleries_files(request, user)
        data['services']['materials_id'] = create_new_materials_for_new_services()
        new_service = Services(data['services'])
        new_service.save()
        generate_basic_stars(service_id=new_service.id)
        first_service('FirstService.html', data["email"], data["name"], data['services']["title"])
    login_success('LoginSuccess.html', data["email"], data["name"], keys)
    return token_return(Auth.generate_token(user.get('id')), data.get('name'), data.get('email'))


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
def login(connect=None):
    """ function for login in api """

    if connect:
        if not isinstance(connect, dict):
            return custom_response('argument type not supportable', 400)
        if 'email' not in connect or 'password' not in connect:
            return custom_response('i need email an password keys', 400)
        user = User.get_user_by_email(connect.get('email'))
        if not user.check_hash(connect.get('password')):
            return custom_response('invalid password', 400)
        ser_user = user_schema.dump(user)
        token = Auth.generate_token(ser_user.get('id'))
        if ser_user.get('email'):
            u_profile = profile_schema.dump(Profiles.get_profile(ser_user.get('email')))
            if u_profile['photo']:
                return token_return(token, ser_user['name'], connect['email'], u_profile['photo'])
        return token_return(token, ser_user['name'], connect['email'])

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
        if_profile_exist = Profiles.get_profile(ser_user.get('email'))
        user_profile = profile_schema.dump(if_profile_exist)
        if user_profile.get('photo'):
            return token_return(token, ser_user['name'], data['email'], user_profile['photo'])
    return custom_response({'token': token, 'name': ser_user['name'], 'email': data['email']}, 200)


@user_api.route('/logout', methods=['DELETE'])
@Auth.auth_required
def logout(user_connected_model, user_connected_schema):
    """ add token in blacklist """

    RevokedTokenModel(request.headers['Isl_Token']).save()
    return custom_response('logout', 200)


# All admin function is here

def up(val, user_connected_model, user_connected_schema):
    user_connected_schema["right"] = val
    user_connected_model.update(user_connected_schema)


@user_api.route('/admin_users', methods=['GET'])
@Auth.auth_required
def get_all_users_admin(user_connected_model, user_connected_schema):
    """ Get a all user """

    if user_connected_model.right != 0:
        users, count, one_dict = User.get_all_users(), int(), {}
        for row in users:
            ser_user = user_schema.dump(row)
            if ser_user.get('right') == 1:
                one_dict[count] = {
                    "id": ser_user.get('id'),
                    "name": ser_user.get('name'),
                    "email": ser_user.get('email'),
                    "right": ser_user.get('right'),
                    "created_at": ser_user.get('created_at'),
                    "modified_at": ser_user.get('modified_at')
                }
                count += 1
        return custom_response(one_dict, 200)
    return custom_response("Unauthorized", 400)


@user_api.route('/admin_users_update/<int:user_id>', methods=['PUT'])
@Auth.auth_required
def update_admin(user_id, user_connected_model, user_connected_schema):
    """ Update Admin users """

    if user_connected_model.right == 2:
        new_user = User.get_one_user(user_id)
        ser_user = user_schema.dump(new_user)
        if ser_user.get('right') == 0:
            up(1, user_connected_model, user_connected_schema)
        elif ser_user.get('right') == 1:
            up(0, user_connected_model, user_connected_schema)
        else:
            return custom_response('Unauthorized', 400)
        return custom_response("changed", 200)
    return custom_response('Unauthorized', 404)