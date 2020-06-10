#!/usr/bin/env python3
""" shebang """

import os
import jwt
import socket
import datetime

from flask import request
from flask import g as auth
from sources.models import custom_response
from sources.models.users.user import User, UserSchema
from sources.models.revokeToken.tokenRevoke import RevokedTokenModel


class Auth:
    """ Auth Class """

    @staticmethod
    def generate_token(user_id):
        """ Generate Token Method """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), 'HS256').decode("utf-8")
        except Exception:
            return custom_response('Error in generating user token', 400)

    @staticmethod
    def decode_token(token):
        """ Decode token method """

        my_response = {'data': {}, 'error': {}}
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
            my_response['data'] = {'user_id': payload['sub']}
            return my_response
        except jwt.ExpiredSignatureError:
            return custom_response("token expired, login please", 400)
        except jwt.InvalidTokenError:
            return custom_response("Invalid token", 400)

    # decorator
    @staticmethod
    def auth_required(func):
        """ Auth decorator """

        def decorated_auth(*args, **kwargs):
            """ auth required decoration """
            try:
                socket.create_connection((socket.gethostbyname("www.google.com"), 80), 2)
            except OSError:
                return custom_response("Connection error", 404)
            if RevokedTokenModel.is_jti_blacklisted(request.headers.get('Isl-Token')):
                return custom_response('You Are logout, reconnect you please', 400)
            if 'Isl_Token' not in request.headers:
                return custom_response('Authentication token is not available, please login to get one', 400)
            token = request.headers.get('Isl-Token')
            data = Auth.decode_token(token)
            try:
                if data.status_code == 400:
                    return custom_response('token invalid', 400)
            except AttributeError:
                user_id = data['data']['user_id']
                check_user = User.get_one_user(user_id)
                if not check_user:
                    return custom_response('token invalid', 400)
                auth.user = {'id': user_id}
                kwargs['user_connected_model'] = check_user
                kwargs['user_connected_schema'] = UserSchema().dump(check_user)
                return func(*args, **kwargs)

        decorated_auth.__name__ = func.__name__
        return decorated_auth
