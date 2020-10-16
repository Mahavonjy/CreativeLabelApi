#!/usr/bin/env python3
""" shebang """

from flask import request
from preferences.defaultData import allowed_beat_maker_options, media_allowed_Photos_Extensions
from sources.models.medias.media import MediaSchema
from sources.models import custom_response
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import validate_data
from sources.models.users.user import UserSchema
from preferences import ALLOWED_MUSIC_MP3, ALLOWED_MUSIC_MPEG, ALLOWED_MUSIC_WAV, ALLOWED_MUSIC_WAVE, \
    ALLOWED_MUSIC_X_WAV, FILE_ZIPPED, USER_ARTIST_BEATMAKER

profile_schema = ProfileSchema()
media_schema = MediaSchema()
user_schema = UserSchema()


def extract_file(req):
    return {
        'photo': req.files.get('photo'),
        'mp3': req.files.get("file"),
        'stems': req.files.get('stems'),
        'wave': req.files.get("beats_wave"),
    }


def _specific(photo=None, mp3=None, wave=None, stems=None, update=False):
    """ beats file verification """

    if not photo and not update:
        return "photo required"

    if photo:
        type_photo = photo.content_type
        if type_photo.split('/', 1)[1].upper() not in media_allowed_Photos_Extensions:
            return "photo type is not supported"

    if not mp3 and not update or not wave and not update:
        return "send me the beats song (.mp3) & (.wave) in field"

    if not stems and not update:
        return "stems required"

    try:
        if mp3:
            file_type_mp3 = mp3.content_type
            if file_type_mp3.split('/', 1)[1] not in [ALLOWED_MUSIC_MPEG, ALLOWED_MUSIC_MP3]:
                return "mp3 file not allowed"

        if wave:
            file_type_wave = wave.content_type
            if file_type_wave.split('/', 1)[1] not in [ALLOWED_MUSIC_WAVE, ALLOWED_MUSIC_WAV, ALLOWED_MUSIC_X_WAV]:
                return "wave file not allowed"
    except AttributeError:
        pass

    try:
        if stems:
            file_type_samples = stems.content_type
            if file_type_samples.split('/', 1)[1] != FILE_ZIPPED:
                return "stems not supported"
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

                if data["genre"] not in allowed_beat_maker_options:
                    return custom_response("genre not supported", 400)

                extracted_file = extract_file(request)
                msg = _specific(**extracted_file)
                if isinstance(msg, str):
                    return custom_response(msg, 400)

                kwargs.update(extracted_file)
                kwargs.update({'data': data})
                return func(**kwargs)

            return custom_response("Unauthorized", 400)

        return beats_secure

    @staticmethod
    def beats_verification_before_update(func):
        """ this is function decorated """

        def beats_secure_before_update(*args, **kwargs):
            """ Get a beats type and other verification """

            beats = kwargs['user_connected_model'].medias.filter_by(id=kwargs['song_id']).first()
            if beats:
                data, error = validate_data(media_schema, request, False)
                if error:
                    return custom_response(data, 400)

                extracted_file = extract_file(request)
                msg = _specific(**extracted_file, update=True)
                if isinstance(msg, str):
                    return custom_response(msg, 400)

                kwargs.update(extracted_file)
                kwargs.update({'beats': beats, 'data': data})
                return func(*args, **kwargs)
            return custom_response("beat not found or deleted", 400)

        beats_secure_before_update.__name__ = func.__name__
        return beats_secure_before_update
