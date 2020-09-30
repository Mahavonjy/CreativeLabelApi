#!/usr/bin/env python3
""" shebang """

from sources.models import custom_response


def token_return(token=None, name=None, email=None, photo=None):
    """ token return for my all register or login """

    return custom_response({'token': token, 'name': name, 'email': email, 'photo': photo}, 200)
