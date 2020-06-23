#! sources/Controller/__init__.py
"""shebang"""

import random
from functools import reduce

import google
import string
import datetime

from flask import g as auth
from google.cloud import storage
from flask import request, Blueprint
from sqlalchemy import func

from sources.models import add_in_storage
from sources.models.medias.media import Media
from sources.models.users.user import User, UserSchema
from sources.models.medias.media import MediaSchema
from sources.models.artists.history.history import ArtistHistory, ArtistHistorySchema
from preferences import defaultDataConf

refresh_all_api = Blueprint('Refresh', __name__)
user_schema = UserSchema()
media_schema = MediaSchema()
user_history_schema = ArtistHistorySchema()


def add_albums_media_in_storage(data):
    """ This song is in Albums uploading """

    try:
        ser_user = user_schema.dump(User.get_one_user(auth.user.get('id')))
        uploaded_file = request.files.get('file')
        filename, data_song = uploaded_file.filename, request.form
        temp = dict(data_song)
        temp["storage_name"] = filename
        temp["album_id"] = data['album_id']
        temp["user_id"] = ser_user['id']
        media, bucket_name, keys = Media(temp), defaultDataConf.GOOGLE_BUCKET_ALBUMS, request.form['Keys']
        add_in_storage(bucket_name, ser_user, uploaded_file, album_song=keys, extension=request.form['extension'])
        media.save()
        return True
    except KeyError:
        return False


def random_string(string_length=100):
    """Generate a random string of fixed length """

    return ''.join(random.choice(string.ascii_lowercase) for i in range(string_length))


def create_artist_story(user_id):
    """ create a new artist story """

    ArtistHistory(dict(user_id=user_id, months_story=create_artist_new_story_dict())).save()


def create_artist_new_story_dict(key=None):
    """

    :return: a dict of user month story
    """
    key = datetime.datetime.now().strftime("%Y-%m") if not key else key
    return {
        str(key): {
            "month_stream": 0,
            "month_pre_stream": 0,
            "month_admirers": 0,
            "prestige": [],
            "paid": False
        }
    }


def update_month_history(user_id, month_pre_stream=None, month_admirers=None, month_stream=None, reverse=False):
    """ update in story table, increment on decrement """

    now = datetime.datetime.now().strftime("%Y-%m")
    story_k = ArtistHistory.get_by_user_id(user_id)
    _story = user_history_schema.dump(story_k)

    if not _story['months_story'].get(str(now)):
        _story['months_story'].update(create_artist_new_story_dict())
    if month_stream:
        _story['months_story'][str(now)]['month_stream'] += 1
    if month_pre_stream:
        _story['months_story'][str(now)]['month_pre_stream'] += 1
    if month_admirers and not reverse:
        _story['months_story'][str(now)]['month_admirers'] += 1
    elif month_admirers and reverse and _story['month_admirers'] > 0:
        _story['months_story'][str(now)]['month_admirers'] -= 1

    story_k.update(_story)


def update_file_storage(args: dict):
    """ Update one file in google cloud storage """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(args['bucket_name'])
    blob = bucket.blob(args['repository_name'] + '_' + str(args['keys']) + '/' + args['filename'])
    try:
        blob.delete()
    except google.api_core.exceptions.NotFound:
        pass
    if args['delete']:
        return True
    blob = bucket.blob(args['repository_name'] + '_' + str(args['keys']) + '/' + args['file'].filename)
    blob.upload_from_string(args['file'].read(), content_type=args['file'].content_type)
    if args['get']:
        blob.make_public()
        return blob.public_url
    return True


def convert_dict_to_sql_json(data_dict=None, data_list=None):
    """

    @param data_list: dict to transform
    @param data_dict: list to transform
    @return: tuple of key and value
    """

    if data_dict:
        data_list = list(reduce(lambda x, y: x + y, data_dict.items()))

    for index, value in enumerate(data_list):
        if isinstance(value, dict):
            data_list[index] = func.json_build_object(
                *convert_dict_to_sql_json(None, list(reduce(lambda x, y: x + y, value.items())))
            )

    return data_list

