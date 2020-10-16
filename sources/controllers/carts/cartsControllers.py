#!/usr/bin/env python3
""" shebang """

import requests
from flask import g as auth
from flask import Blueprint, request

from preferences.defaultData import allowed_beats_license
from sources.models import custom_response
from auth.authentification import Auth
from sources.models.carts.cart import Carts, CartSchema
from sources.models.users.user import User, UserSchema
from sources.tools.tools import get_time, validate_data
from sources.models.medias.media import Media, MediaSchema

cart_api = Blueprint('carts', __name__)
media_schema = MediaSchema()
user_schema = UserSchema()
cart_schema = CartSchema()


def time_exceeds(func):
    """ my func is my arg """

    def decor(*args, **kwargs):
        """ my function who get is """

        user_cart = kwargs['user_connected_model'].carts.all()
        if request.method == "GET":
            kwargs['cart_list'] = []
            for row in user_cart:
                cart_info = cart_schema.dump(row)
                if not get_time(cart_info['created_at'], 30):
                    row.delete()
                    continue
                kwargs['cart_list'].append(cart_info)
        if request.method == "POST":
            for row in user_cart:
                cart_info = cart_schema.dump(row)
                if not get_time(cart_info['created_at'], 30):
                    row.delete()
                    continue
        return func(*args, **kwargs)

    decor.__name__ = func.__name__
    return decor


@cart_api.route('/addToCart', methods=['POST'])
@Auth.auth_required
@time_exceeds
def add_song_to_card(user_connected_model, user_connected_schema):
    """ add beat_id to cart """

    data, error = validate_data(cart_schema, request)
    if error:
        return custom_response(data, 400)

    if data['license'] not in allowed_beats_license:
        return custom_response("invalid license", 400)

    if user_connected_model.carts.filter_by(beat_id=data['beat_id'], license=data['license']).first():
        return custom_response("cart existing", 400)

    beat = media_schema.dump(Media.get_song_by_id(data['beat_id']))

    if not beat:
        return custom_response("beat not exist", 400)

    elif beat['user_id'] == user_connected_model.id:
        return custom_response("Unauthorized", 400)

    new_cart_data = dict(
        beat_id=data['beat_id'],
        price=beat[data['license'].replace('lease', 'price')],
        license=data['license'],
        user_id=user_connected_model.id
    )
    new_cart = Carts(new_cart_data)
    new_cart.save()
    return custom_response(cart_schema.dump(new_cart), 200)


@cart_api.route('/MyCart', methods=['GET'])
@Auth.auth_required
@time_exceeds
def get_my_cart(user_connected_model, user_connected_schema, cart_list):
    """ get all song in my cart """

    return custom_response(cart_list, 200)


@cart_api.route('/delete/<int:cart_id>', methods=['DELETE'])
@Auth.auth_required
def delete_in_my_cart(cart_id, user_connected_model, user_connected_schema):
    """ get all song in my cart """

    cart = user_connected_model.carts.filter_by(id=cart_id).first()
    if not cart:
        return custom_response("cart not existing", 400)
    cart.delete()
    return custom_response("deleted", 200)
