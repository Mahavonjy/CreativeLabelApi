#!/usr/bin/env python3
""" shebang """

from sources.controllers import add_albums_media_in_storage
from sources.models.medias.media import MediaSchema
from sources.models import custom_response, add_in_storage
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import validate_data
from sources.models.users.user import User, UserSchema
from sources.models.medias.albums import AlbumSchema
from preferences import defaultDataConf
from flask import request, Response
from flask import g as auth
import zipfile

profile_schema = ProfileSchema()
albumSchema = AlbumSchema()
media_schema = MediaSchema()
user_schema = UserSchema()


def _specific(photo_file, uploaded_file_mp3, uploaded_file_wave, uploaded_samples, key=False):
    """ beats file verification """

    if photo_file:
        type_photo = photo_file.content_type
        type_photo = type_photo.split('/', 1)[1]
        if type_photo.upper() not in defaultDataConf.media_allowed_Photos_Extensions:
            return "photo type is not supported"
    if not uploaded_file_mp3 and not key or not uploaded_file_wave and not key:
        return "send me the beats song (.mp3) & (.wave) in field"
    if not uploaded_samples and not key:
        return "send me the stems for this beat"
    try:
        file_type_mp3 = uploaded_file_mp3.content_type
        if file_type_mp3.split('/', 1)[1] not in defaultDataConf.media_allowed_Extensions:
            return "beats type is not a mp3 file or not a wave file"
    except AttributeError:
        pass
    try:
        file_type_samples = uploaded_samples.content_type
        if file_type_samples.split('/', 1)[1] != defaultDataConf.media_allowed_albums[0]:
            return "sample not supported"
    except AttributeError:
        pass

    return True


class Secure:
    """ Decorator class """

    @staticmethod
    def beats_verification_before_upload(func):
        """ this is function decorated """

        def beats_secure(*args, **kwargs):
            """ Get a beats type and other verification """

            ser_user = user_schema.dump(User.get_one_user(auth.user.get('id')))
            if ser_user['user_type'] == "beatmaker" or ser_user['right'] != 0:
                data, error = validate_data(media_schema, request, False)
                if error:
                    return custom_response(data, 400)
                if not (data.get("basic_price") and data.get("silver_price") and data.get("gold_price")):
                    return custom_response("i need basic, silver and gold price", 400)
                if data["genre_musical"] != defaultDataConf.media_allowed_genre_musical[1] \
                        or data["genre"] not in defaultDataConf.media_allowed_Genres:
                    return custom_response("genre or genre_musical not supported", 400)
                photo_file = request.files.get('photo')
                uploaded_samples = request.files.get('stems')
                uploaded_file_mp3, uploaded_file_wave = request.files.get("file"), request.files.get("beats_wave")
                response = _specific(photo_file, uploaded_file_mp3, uploaded_file_wave, uploaded_samples)
                if isinstance(response, str):
                    return custom_response(response, 400)
                kwargs['uploaded_samples'] = uploaded_samples
                kwargs['data'], kwargs['uploaded_file_mp3'] = data, uploaded_file_mp3
                kwargs['uploaded_file_wave'], kwargs['photo_file'] = uploaded_file_wave, photo_file
                return func(*args, **kwargs)

            return custom_response("Unauthorized", 400)

        return beats_secure

    @staticmethod
    def beats_verification_before_update(func):
        """ this is function decorated """

        def beats_secure_before_update(*args, **kwargs):
            """ Get a beats type and other verification """

            user = User.get_one_user(auth.user.get('id'))
            beats = user.medias.filter_by(id=kwargs['song_id']).first()
            if beats:
                data, error = validate_data(media_schema, request, False)
                if error:
                    return custom_response(data, 400)
                photo_file = request.files.get('photo')
                uploaded_samples = request.files.get('stems')
                uploaded_file_mp3, uploaded_file_wave = request.files.get("file"), request.files.get("beats_wave")
                response = _specific(photo_file, uploaded_file_mp3, uploaded_file_wave, uploaded_samples, key=True)
                if isinstance(response, str):
                    return custom_response(response, 400)
                kwargs['beats'], kwargs['data'] = beats, data
                kwargs['photo_file'], kwargs['uploaded_samples'], kwargs['up'] = photo_file, uploaded_samples, {}
                kwargs['uploaded_file_mp3'], kwargs['uploaded_file_wave'] = uploaded_file_mp3, uploaded_file_wave
                return func(*args, **kwargs)
            return custom_response("beats not found", 400)

        beats_secure_before_update.__name__ = func.__name__
        return beats_secure_before_update

    @staticmethod
    def music_verification_before_upload(func):
        """ this is function decorated """

        def audio_secure(uploaded_file, photo_file, data, user_connected_model, user_connected_schema):
            """ Get music type or photo type and others """

            ser_user = user_schema.dump(User.get_one_user(auth.user.get('id')))
            if ser_user['artist'] and ser_user['user_type'] == "artist_musician" or ser_user['right'] != 0:
                data, error = validate_data(media_schema, request, False)
                if error:
                    if add_albums_media_in_storage(data):
                        return Response(status=200)
                    return custom_response(data, 400)
                uploaded_file = request.files.get("file")
                if not uploaded_file:
                    return custom_response("send me the song", 400)
                # if Media.get_song_by_storage_name(uploaded_file.filename):
                #     return custom_response("File exist", 200)
                file_type = uploaded_file.content_type
                if file_type.split('/', 1)[1] not in defaultDataConf.media_allowed_Extensions:
                    return custom_response("Not accept file type, the File Accepted is mp3, wave, mpeg", 400)
                photo_file = request.files.get('photo')
                if request.files.get('photo'):
                    type_photo = photo_file.content_type
                    if type_photo.split('/', 1)[1] not in defaultDataConf.media_allowed_Photos_Extensions:
                        return custom_response("photo type is not supported", 400)
                if data["title"] is "" or data["artist"] is "" or data["genre"] is "" or data["genre_musical"] is "":
                    return custom_response("title, artist, genre and genre_musical cannot be null", 400)
                if data["genre_musical"] != defaultDataConf.media_allowed_genre_musical[0] \
                        or data["genre"] not in defaultDataConf.media_allowed_Genres:
                    return custom_response("genre or genre_musical not supported", 400)
                return func(uploaded_file, photo_file, data, user_connected_model, user_connected_schema)
            return custom_response("Unauthorized", 400)

        return audio_secure

    @staticmethod
    def music_before_update(func):
        """ this is function decorated """

        def music_secure(*args, **kwargs):
            """ Get music id type and other verification """

            data, error = validate_data(media_schema, request, False)
            if error:
                return custom_response(data, 400)
            user = User.get_one_user(auth.user.get('id'))
            ser_user, song = user_schema.dump(user), user.medias.filter_by(id=kwargs["song_id"]).first()
            if not song:
                return custom_response("Song not found", 404)
            kwargs["up_file"], kwargs['up'] = request.files.get('file'), {}
            kwargs["data"], kwargs["ser_user"], kwargs["song"] = data, ser_user, song
            return func(*args, **kwargs)

        return music_secure

    @staticmethod
    def album_before_upload(func):
        """ this is function decorated """

        def album_secure():
            """ all secure before upload album """

            user = User.get_one_user(auth.user.get('id'))
            ser_user = user_schema.dump(user)
            user_profile_info = profile_schema.dump(user.profile)
            if not ser_user['artist'] or ser_user['user_type'] != "artist_musician":
                return custom_response("Unauthorized", 400)
            data, error = validate_data(albumSchema, request, False)
            if data.get('genre_musical') == "beats":
                if not data.get('price'):
                    return custom_response("Price is required", 400)
            response_return = data if error else "File Empty" if not request.files.get('file') else 0
            if response_return:
                return custom_response(response_return, 400)
            uploaded_file = request.files.get('file')
            try:
                photo_file = request.files['photo'] if request.files['photo'] else None
                type_photo = photo_file.content_type if photo_file else None
                _, file_type = type_photo.rsplit('/', 1)
                if file_type not in defaultDataConf.media_allowed_Photos_Extensions:
                    return custom_response("photo type is not supported", 400)
                link = add_in_storage(defaultDataConf.GOOGLE_BUCKET_IMAGES, ser_user, photo_file, 'albums/')
            except KeyError:
                link = user_profile_info["photo"] if user_profile_info["photo"] else 0
            if zipfile.is_zipfile(uploaded_file):
                return func(user, ser_user, data, link, uploaded_file, zipfile.ZipFile)
            return custom_response("Album type not supported", 400)

        return album_secure
