#!/usr/bin/env python3
""" shebang """

from sources.controllers.medias.mediaControllers import stream_song_public_url, update_file_storage as up_ft
from sources.controllers.medias.albumSuggestion import top_album_and_suggestion as top_suggestion
from sources.models.admirations.admirations import AdmireSchema
from sources.models.medias.albums import Albums, AlbumSchema
from sources.security.verification import Secure
from sources.models.medias.media import Media, MediaSchema
from sources.tools.tools import validate_data
from sources.models.profiles.profile import ProfileSchema
from sources.models.search.basicSearch import document_delete
from sources.models.users.user import User, UserSchema
from auth.authentification import Auth
from preferences import defaultDataConf
from sources.controllers import random_string
from sources.models import custom_response
from flask import Blueprint, request
from google.cloud import storage
from flask import g as auth
import requests
import random
import os

album_api = Blueprint('album', __name__)
bucket_albums = defaultDataConf.GOOGLE_BUCKET_ALBUMS
bucket_images = defaultDataConf.GOOGLE_BUCKET_IMAGES
profile_schema = ProfileSchema()
admire_schema = AdmireSchema()
media_schema = MediaSchema()
albumSchema = AlbumSchema()
user_schema = UserSchema()


def create_dict(dat=None, user_=None, k=None, link=None, new_l=None, alb_inf=None, ext=None, title_t=None, info=None):
    """ create and return many dict """

    if alb_inf:
        album = dat
        album["number_songs"] = len(new_l)
        album["user_id"] = user_.get('id')
        album["keys"] = k
        album["album_photo"] = link if link else 0
        return album
    album_song = dat
    album_song["extension"] = ext
    album_song["Title"] = title_t
    album_song["album_id"] = info.get('id')
    album_song["Keys"] = k
    album_song["photo"] = link if link else 0
    return album_song


@album_api.route('/oneAlbums/<int:album_id>', methods=['GET'])
def get_songs_in_albums(album_id, get=None):
    """ Get all songs existing in album_id """

    one_dict, all_songs = [], Albums.get_album_id(album_id).medias.all()
    for song in all_songs:
        song_info = media_schema.dump(song)
        one_dict.append({
            "id": song_info.get('id'),
            "user_id": song_info.get('user_id'),
            "title": song_info.get('title'),
            "genre": song_info.get('genre'),
            "artist": song_info.get('artist'),
            "description": song_info.get('description'),
            "album_id": song_info.get('album_id'),
            "photo": song_info.get('photo'),
            "link": stream_song_public_url(True, song_info['id']),
        })
    if get:
        return one_dict
    return custom_response({"all_songs": one_dict}, 200)


@album_api.route('/uploadAlbums', methods=['POST'])
@Auth.auth_required
@Secure.album_before_upload
def upload_albums(user, ser_user, data, link, uploaded_file, f_type):
    """ Upload Album """

    albums, directory_name = f_type(uploaded_file), random_string()
    albums.extractall(directory_name)
    new_list, album, data_song, precaution, keys = [], {}, {}, 0, random.randint(1111, 9999) * 9999
    album = create_dict(dat=data, user_=ser_user, k=keys, link=link, new_l=new_list, alb_inf=True)
    try:
        album_info = Albums.get_album_id(data["album_id"])
        album_info.update(album)
    except KeyError:
        temp, album_save = ser_user, Albums(album)
        try:
            temp['album_shared'] += 1
        except TypeError:
            temp['album_shared'] = 1
        user.update(temp)
        album_save.save()
    album_info, h = Albums.get_album_info(keys), {"Isl-Token": request.headers.get('Isl_Token')}
    info, name_path = albumSchema.dump(album_info), albums.namelist()
    for n in name_path:
        try:
            index, rest = n.split('/', 1)
        except ValueError:
            new_list.append(n)
            continue
        if index + '/' == name_path[0]:
            count_temp = 0
            for f in rest:
                precaution += 1 if count_temp == 0 and f == '.' else 0
                count_temp += 1
            if precaution == 0:
                new_list.append(n)
            precaution = int()
    if len(new_list) < 2:
        pass
    else:
        new_list.remove(new_list[0])
    album["number_songs"] = len(new_list)
    album_info.update(album)
    for n in new_list:
        f = {'file': (os.path.basename(directory_name + '/' + n), open(directory_name + '/' + n, 'rb'))}
        try:
            _, name_of_file = n.split('/', 1)
        except ValueError:
            name_of_file = n
        title_temp, extension = name_of_file.rsplit('.', 1)
        data_song = create_dict(ext=extension, dat=data, title_t=title_temp, info=info, k=keys, link=link)
        upload_media = requests.post(request.host_url + 'api/medias/uploadMedia', files=f, headers=h, data=data_song)
        if upload_media.status_code != 200:
            return custom_response("Error Intern", 400)
    os.remove(directory_name)
    return custom_response("Albums added", 200)


@album_api.route('/update/<int:album_id>', methods=['PUT'])
@Auth.auth_required
def update_album(album_id, user_connected_model, user_connected_schema):
    """ Upload Albums """

    def update_album_info():
        """ upload a new album """

        new_album_info = Albums.get_album_id(album_id)
        new_information = albumSchema.dump(album_info)
        new_information["album_name"] = data.get("album_name")
        new_information["artist"] = data.get("artist")
        new_information["description"] = data.get("description")
        new_information["genre"] = data.get("genre")
        new_information["genre_musical"] = data.get("genre_musical")
        new_information["stream_total"] = data.get("stream_total")
        all_songs_in_album = get_songs_in_albums(album_id, True)
        for song_index in all_songs_in_album:
            media = Media.get_song_by_id(song_index["id"])
            temp = media_schema.dump(media)
            temp["description"] = new_information["description"]
            temp["genre_musical"] = new_information["genre_musical"]
            temp["genre"] = new_information["genre"]
            temp["artist"] = new_information["artist"]
            media.update(temp)
        new_album_info.update(new_information)
        return True

    def update_url_photo(photo):
        """ update photo for all songs in albums """

        update_album_info()
        new_album_info, tmp = Albums.get_album_id(album_id), {}
        new_information = albumSchema.dump(new_album_info)
        tmp['bucket_name'] = bucket_images
        tmp['repository_name'], tmp['keys'] = "albums/" + user_connected_schema.get(
            'fileStorage_key'), user_connected_schema.get('id')
        tmp['song_name'], tmp['file'], tmp['get'], tmp['delete'] = photo.filename, photo, True, False
        url = up_ft(tmp)
        new_information["album_photo"], all_song_in_album = url, get_songs_in_albums(album_id, True)
        new_album_info.update(new_information)
        for song in all_song_in_album:
            media = Media.get_song_by_id(song["id"])
            media_song = media_schema.dump(media)
            media_song["photo"] = url
            media.update(media_song)
        return True

    def delete_album_information():
        """ Update album and song in album """

        repository_image, tmp, id_user = "albums/" + user_connected_schema.get(
            'fileStorage_key'), {}, user_connected_schema.get('id')
        repository_albums = user_connected_schema.get('fileStorage_key') + '_' + str(information["keys"]) + '_' + str(
            id_user)
        all_songs_in_album, bucket_image = Media.get_all_song_by_album_id(album_id), bucket_images

        try:
            _, name = information.get('album_photo').rsplit('/', 1)
            tmp['bucket_name'] = bucket_image
            tmp['repository_name'], tmp['keys'] = repository_image, user_connected_schema.get('id')
            tmp['song_name'], tmp['file'], tmp['delete'], tmp['get'] = name, None, True, False
            up_ft(tmp)
        except ValueError:
            pass
        except AttributeError:
            pass

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_albums)
        blobs = bucket.list_blobs(prefix=repository_albums)
        for blob in blobs:
            blob.delete()
        for song in all_songs_in_album:
            song = Media.get_song_by_id(media_schema.dump(song)["id"])
            song.delete()
        upload_file, h = request.files.get("file"), {"Isl_Token": request.headers.get("Isl_Token")}
        filename, data["album_id"] = upload_file.filename, album_id
        upload_file.save("sources/albumZip/" + filename)
        if request.files.get('photo'):
            upload_photo = request.files.get('photo')
            upload_photo.save(upload_photo.filename)
            f = {'file': (filename, open("sources/albumZip/" + filename, 'rb')),
                 'photo': (upload_photo.filename, open(upload_photo.filename, 'rb'))}
            os.remove(upload_photo.filename)
        else:
            f = {'file': (filename, open("sources/albumZip/" + filename, 'rb'))}
        upload_media = requests.post(request.host_url + 'api/albums/uploadAlbums', files=f, headers=h, data=data)
        if upload_media.status_code != 200:
            return False
        os.remove("sources/albumZip/" + filename)
        return True

    album_info = user_connected_model.albums.filter_by(id=album_id).first()
    if not album_info:
        return custom_response("album not exists", 400)
    information = albumSchema.dump(album_info)
    data, error = validate_data(albumSchema, request, False)
    if error:
        return custom_response(data, 400)
    up = delete_album_information() if request.files.get('file') else update_url_photo(request.files.get('photo')) \
        if request.files.get('photo') else update_album_info()
    response_return = custom_response("Updated", 200) if up else custom_response("Error Intern", 400)
    return response_return


@album_api.route('/delete/<int:album_id>', methods=['DELETE'])
@Auth.auth_required
def delete_album(album_id, user_connected_model, user_connected_schema):
    """ delete albums """

    user_id_ = user_connected_model.id
    album_info = user_connected_model.albums.filter_by(id=album_id).first()
    if not album_info:
        return custom_response("album not exists", 400)
    information, tmp = albumSchema.dump(album_info), {}
    if user_id_ == int(information.get('user_id')) or user_connected_model.right != 0:
        if information["album_photo"]:
            link_split_list = information["album_photo"].split("/", 3)
            _, _, user_repo, file_name = link_split_list[3].split("/", 4)
            repository_name, _ = user_repo.split("_")
            tmp['bucket_name'] = bucket_images
            tmp['repository_name'], tmp['keys'] = "albums/" + repository_name, user_id_
            tmp['song_name'], tmp['file'], tmp['delete'], tmp['get'] = file_name, None, True, False
            up_ft(tmp)
        repository = user_connected_model.fileStorage_key + '_' + str(information["keys"]) + '_' + str(user_id_)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_albums)
        blobs = bucket.list_blobs(prefix=repository)
        for blob in blobs:
            blob.delete()
        album_info.delete()
        document_delete("albums_and_songs", "songs", {"id": information['id']}, {"keys": information['keys']})
        return custom_response("Deleted", 200)
    return custom_response("Unauthorized", 400)


@album_api.route('/albums_suggestion', methods=['GET'])
@Auth.auth_required
def suggestion_album():
    """ get all latest medias shared by all user admire """

    user_id = auth.user.get('id')
    user_genre_list = User.get_one_user(user_id).user_genre_list
    return custom_response(top_suggestion(user_genre_list, user_id), 200)
