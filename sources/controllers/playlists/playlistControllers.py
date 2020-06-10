#!/usr/bin/env python3
""" shebang """

import json
import google
import requests
from flask import Blueprint, request
from flask import g as auth
from google.cloud import storage
from sources.tools.tools import validate_data

from sources.models import custom_response
from auth.authentification import Auth
from sources.models.medias.media import Media, MediaSchema
from sources.models.playlists.playlist import Playlists, PlaylistSchema
from sources.models.users.user import User, UserSchema
from preferences import defaultDataConf

playlist_api = Blueprint('playlist', __name__)
secure_photo = defaultDataConf.media_allowed_Photos_Extensions
bucket_images = defaultDataConf.GOOGLE_BUCKET_IMAGES
playlist_schema = PlaylistSchema()
user_schema = UserSchema()
mediaSchema = MediaSchema()


def playlist_secure(func):
    """ decor """

    def func_edit(*args, **kwargs):
        """ all verification before continue """

        user = User.get_one_user(auth.user.get('id'))
        playlist = user.playlists.filter_by(id=kwargs['playlist_id']).first()
        song = Media.get_song_by_id(kwargs['song_id'])
        if not playlist or not song:
            return custom_response("playlist or Song not found", 400)
        playlist_data = playlist_schema.dump(playlist)
        list_of_song_id_in_playlist = playlist_data['song_id_list']
        if request.method == "POST":
            if int(kwargs['song_id']) in list_of_song_id_in_playlist:
                return custom_response("song exist", 400)
        elif request.method == "DELETE":
            if int(kwargs['song_id']) not in list_of_song_id_in_playlist:
                return custom_response("song not found", 200)
        kwargs['model_media'] = song
        kwargs['playlist_model'] = playlist
        kwargs['playlist_data'] = playlist_data
        return func(*args, **kwargs)

    func_edit.__name__ = func.__name__
    return func_edit


def update_media_playlist(kwargs, fill_in_playlist=False):
    """ update <in_playlist> in media table for one song """

    if fill_in_playlist:
        kwargs['song']['in_playlist'] += 1
    else:
        kwargs['song']['in_playlist'] -= 1
    kwargs['model_media'].update(kwargs['song'])
    kwargs['playlist_model'].update(kwargs['playlist_data'])


@playlist_api.route('/create', methods=['POST'])
@Auth.auth_required
def create_playlist(user_connected_model, user_connected_schema):
    """ Here is function who create new Playlist in database """

    data, error = validate_data(playlist_schema, request, False)
    if error:
        return custom_response(data, 400)

    data["user_id"], upload_photo = user_connected_model.id, request.files.get('photo')
    if_exist = user_connected_model.playlists.filter_by(name=data.get('name')).first()
    if if_exist:
        return custom_response("playlist exist", 400)
    if upload_photo:
        data['photo_storage_name'] = upload_photo.filename
        type_photo = upload_photo.content_type
        type_photo = type_photo.split('/')[1]
        if type_photo.upper() not in secure_photo:
            return custom_response("photo type is not supported", 400)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_images)
        b_n = "playlists/" + user_connected_model.fileStorage_key + '_' + \
              str(data["user_id"]) + '/' + upload_photo.filename
        blob = bucket.blob(b_n)
        blob.upload_from_string(upload_photo.read(), content_type=upload_photo.content_type)
        blob.make_public()
        data['photo'] = blob.public_url
    Playlists(data).save()
    return custom_response("created", 200)


@playlist_api.route('/addInPlaylist/<int:playlist_id>/<int:song_id>', methods=['POST'])
@Auth.auth_required
@playlist_secure
def add_song(playlist_id, song_id, **kwargs):
    """ Add song in playlist """

    kwargs['playlist_data']['song_id_list'].append(int(song_id))
    kwargs['song'] = mediaSchema.dump(kwargs['model_media'])
    update_media_playlist(kwargs, True)
    return custom_response("song added", 200)


@playlist_api.route('/deleteSongInPlaylist/<int:playlist_id>/<int:song_id>', methods=['DELETE'])
@Auth.auth_required
@playlist_secure
def delete_song(playlist_id, song_id, **kwargs):
    """ Delete song in playlist_id """

    kwargs['playlist_data']['song_id_list'].remove(int(song_id))
    kwargs['song'] = mediaSchema.dump(kwargs['model_media'])
    update_media_playlist(kwargs)
    return custom_response("song deleted", 200)


@playlist_api.route('/userPlaylist', methods=['GET'])
@Auth.auth_required
def get_user_playlist(user_connected_model, user_connected_schema):
    """ get all user playlist created """

    user_playlist, all_playlist = user_connected_model.playlists, []
    for playlist in user_playlist:
        all_playlist.append(playlist_schema.dump(playlist))
    return custom_response({"users_playlist": all_playlist}, 200)


@playlist_api.route('/Playlist/<int:playlist_id>', methods=['GET'])
@Auth.auth_required
def get_playlist_songs(playlist_id, user_connected_model, user_connected_schema):
    """ get playlist song """

    if_playlist_exist = user_connected_model.playlists.filter_by(id=playlist_id).first()
    if not if_playlist_exist:
        return custom_response("Playlist not exist", 400)
    playlist_info = playlist_schema.dump(if_playlist_exist)
    all_song = []
    for song_id in playlist_info['song_id_list']:
        get_song = requests.get(request.host_url + 'api/medias/single/' + str(song_id))
        all_song.append(json.loads(get_song.text))
    return custom_response({"songs": all_song}, 200)


@playlist_api.route('/update/<int:playlist_id>', methods=['PUT'])
@Auth.auth_required
def update_playlist(playlist_id, user_connected_model, user_connected_schema):
    """ Update one playlist """

    data, error = validate_data(playlist_schema, request, False)
    if error:
        return custom_response(data, 400)

    if_playlist_exist, u_i = user_connected_model.playlists.filter_by(id=playlist_id).first(), user_connected_schema
    if not if_playlist_exist:
        return custom_response("Playlist Not exist", 400)
    pl_info, upload_photo = playlist_schema.dump(if_playlist_exist), request.files.get('photo')
    if upload_photo:
        type_photo = upload_photo.content_type
        file_type = type_photo.split('/')[1][0]
        if file_type not in secure_photo:
            return custom_response("photo type is not supported", 400)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_images)
        b_n = "playlists/" + u_i['fileStorage_key'] + '_' + str(u_i['id']) + '/' + pl_info['photo_storage_name']
        blob = bucket.blob(b_n)
        try:
            blob.delete()
        except TypeError or google.api_core.exceptions.NotFound:
            pass
        blob = bucket.blob("playlists/" + u_i['fileStorage_key'] + '_' + str(u_i['id']) + '/' + upload_photo.filename)
        blob.upload_from_string(upload_photo.read(), content_type=upload_photo.content_type)
        blob.make_public()
        pl_info['photo_storage_name'], pl_info["photo"] = upload_photo.filename, blob.public_url
    if_playlist_exist.update(dict(pl_info, **data))
    return custom_response("Updated", 200)


@playlist_api.route('/delete/<playlist_id>', methods=['DELETE'])
@Auth.auth_required
def delete_playlist(playlist_id, user_connected_model, user_connected_schema):
    """ Delete one playlist """

    if_playlist_exist, u_i = user_connected_model.playlists.filter_by(id=playlist_id).first(), user_connected_schema
    if not if_playlist_exist:
        return custom_response("Playlist Not exist", 400)
    playlist_info = playlist_schema.dump(if_playlist_exist)
    if playlist_info.get('photo'):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_images)
        b_n = "playlists/" + u_i['fileStorage_key'] + '_' + str(u_i['id']) + '/' + playlist_info['photo_storage_name']
        blob = bucket.blob(b_n)
        try:
            blob.delete()
        except google.api_core.exceptions.NotFound:
            pass
    if_playlist_exist.delete()
    return custom_response("Deleted", 200)
