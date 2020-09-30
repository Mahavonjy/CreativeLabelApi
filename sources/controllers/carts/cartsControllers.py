#!/usr/bin/env python3
""" shebang """

import requests
from flask import g as auth
from flask import Blueprint, request
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

        user_cart = User.get_one_user(auth.user.get('id')).Carts.all()
        if request.method == "GET":
            kwargs['cart_list'] = []
            for row in user_cart:
                cart_info = cart_schema.dump(row)
                if not get_time(cart_info['created_at'], 30):
                    row.delete()
                    continue
                media = media_schema.dump(Media.get_song_by_id(cart_info.get('song_id')))
                generate_url = requests.get(request.host_url + 'api/medias/Streaming/' + str(media.get('id')))
                if generate_url.status_code != 200:
                    return custom_response("error in function streaming", 400)
                cart_info['link'], cart_info['media'] = generate_url.text, media
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
    """ add song_id to cart """

    data, error = validate_data(cart_schema, request)
    if error:
        return custom_response(data, 400)

    if user_connected_model.Carts.filter_by(song_id=data['song_id'], licenses_name=data['licenses_name']).first():
        return custom_response("cart existing", 400)

    media = media_schema.dump(Media.get_song_by_id(data['song_id']))
    if not media["genre_musical"] == "beats" or media['user_id'] == user_connected_model.id:
        return custom_response("Unauthorized", 400)

    new_cart_data = dict(
        song_id=data['song_id'], price=data["price"], licenses_name=data['licenses_name'],
        user_id=user_connected_model.id)
    new_c = Carts(new_cart_data)
    new_c.save()
    return custom_response(cart_schema.dump(new_c), 200)


@cart_api.route('/MyCart', methods=['GET'])
@Auth.auth_required
@time_exceeds
def get_my_cart(**kwargs):
    """ get all song in my cart """

    return custom_response(kwargs['cart_list'], 200)


@cart_api.route('/delete/<int:cart_id>', methods=['DELETE'])
@Auth.auth_required
def delete_in_my_cart(cart_id, user_connected_model, user_connected_schema):
    """ get all song in my cart """

    cart = user_connected_model.Carts.filter_by(id=cart_id).first()
    if not cart:
        return custom_response("cart not existing", 400)
    cart.delete()
    return custom_response("deleted", 200)
