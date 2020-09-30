#!/usr/bin/env python3
""" shebang """
from preferences.defaultData import media_allowed_Extensions, media_allowed_Genres, media_allowed_Photos_Extensions
from sources.models.medias.media import MediaSchema
from sources.models import custom_response
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import upload_beats, validate_data
from sources.models.users.user import User, UserSchema
from preferences import FILE_ZIPPED, MUSICAL_GENRE_BEATS, MUSICAL_GENRE_MUSIC, USER_ARTIST_BEATMAKER
from flask import request, Response
from flask import g as auth

profile_schema = ProfileSchema()
media_schema = MediaSchema()
user_schema = UserSchema()


def _specific(photo, mp3, wave, stems, key=False):
    """ beats file verification """

    if not photo:
        return "photo required"

    type_photo = photo.content_type
    if type_photo.split('/', 1)[1].upper() not in media_allowed_Photos_Extensions:
        return "photo type is not supported"

    if not mp3 and not key or not wave and not key:
        return "send me the beats song (.mp3) & (.wave) in field"

    if not stems and not key:
        return "stems required"

    try:
        file_type_mp3 = mp3.content_type
        if file_type_mp3.split('/', 1)[1] not in media_allowed_Extensions:
            return "beats type is not a mp3 file or not a wave file"
    except AttributeError:
        pass
    try:
        file_type_samples = stems.content_type
        if file_type_samples.split('/', 1)[1] != FILE_ZIPPED:
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

            _u_schema = kwargs['user_connected_schema']
            if _u_schema['user_type'] == USER_ARTIST_BEATMAKER or _u_schema['right'] != 0:
                data, error = validate_data(media_schema, request, False)
                if error:
                    return custom_response(data, 400)

                if not (data.get("basic_price") and data.get("silver_price") and data.get("gold_price")):
                    return custom_response("i need basic, silver and gold price", 400)

                if data["genre_musical"] != MUSICAL_GENRE_BEATS or data["genre"] not in media_allowed_Genres:
                    return custom_response("genre or genre_musical not supported", 400)

                photo = request.files.get('photo')
                mp3 = request.files.get("file")
                wave = request.files.get("beats_wave")
                response = _specific(photo, mp3, wave, request.files.get('stems'))
                if isinstance(response, str):
                    return custom_response(response, 400)

                f_storage_id = {'fileStorage_key': _u_schema['fileStorage_key'], 'user_id': _u_schema['id']}
                data['link'] = upload_beats(request.files.get("file"), **f_storage_id)
                # data['beats_wave'] = upload_beats(request.files.get("beats_wave"), **f_storage_id)
                data['stems'] = upload_beats(request.files.get('stems'), **f_storage_id, stems=True)
                kwargs.update({'data': data, 'mp3_filename': mp3.filename, 'wave': request.files.get("beats_wave"), 'photo': photo})
                return func(**kwargs)

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
