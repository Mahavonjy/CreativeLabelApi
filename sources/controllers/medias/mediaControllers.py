#!/usr/bin/env python3
""" shebang """

import datetime
import requests
from flask import Blueprint, request, json
from google.cloud import storage

from auth.authentification import Auth
from sources.controllers import update_medias_shared, update_file_storage, create_artist_new_story_dict
from sources.controllers.medias.mediaBeatSuggestion import media_beat_suggestion
from sources.security.verification import Secure
from sources.models import custom_response, add_in_storage
from sources.models.admirations.admirations import Admiration, AdmireSchema
from sources.models.medias.albums import Albums, AlbumSchema
from sources.models.medias.media import Media, MediaSchema
from sources.models.medias.mediaListened import Listened, ListenedSchema
from sources.models.artists.history.history import ArtistHistory, ArtistHistorySchema
from sources.tools.tools import librosa_collect
from sources.models.profiles.profile import ProfileSchema
from sources.models.search.basicSearch import document_delete as d_delete
from sources.models.users.user import User, UserSchema
from preferences import defaultDataConf

media_api = Blueprint('media', __name__)
allowed_genre_musical = defaultDataConf.media_allowed_genre_musical
allowed_genres = defaultDataConf.media_allowed_Genres
bucket_audios = defaultDataConf.GOOGLE_BUCKET_AUDIOS
bucket_albums = defaultDataConf.GOOGLE_BUCKET_ALBUMS
bucket_images = defaultDataConf.GOOGLE_BUCKET_IMAGES
bucket_beats = defaultDataConf.GOOGLE_BUCKET_BEATS
month_story_schema = ArtistHistorySchema()
listened_schema = ListenedSchema()
profile_schema = ProfileSchema()
admire_schema = AdmireSchema()
media_schema = MediaSchema()
albumSchema = AlbumSchema()
user_schema = UserSchema()


def all_medias_in_genre(genre, genre_musical, with_link=False, not_json=False):
    """

    :param genre:
    :param genre_musical:
    :param with_link:
    :param not_json:
    :return: all song genre
    """

    all_songs, genre = Media.get_song_by_genre(genre, genre_musical), []
    for songs in all_songs:
        if with_link:
            media_ = media_schema.dump(songs)
            media_['link'] = stream_song_public_url(True, songs.id)
            genre.append(media_)
            continue
        genre.append(media_schema.dump(songs))
    if not_json:
        return genre
    return custom_response({"songs": genre}, 200)


@media_api.route('/oneMedia/<int:song_id>', methods=['GET'])
def get_one_media(song_id, get=None):
    """ Get One Media """

    song = Media.get_song_by_id(song_id)
    if not song:
        return custom_response("Song not found", 400)
    media = media_schema.dump(song)
    if get:
        return media
    return custom_response(media, 200)


@media_api.route('/all_medias', methods=['GET'])
def get_all_songs(get=0, false=None):
    """ List of All Musics """

    all_songs = Media.get_all_song_not_album(get)
    songs, count = {}, 0
    for row in all_songs:
        songs[count], count = media_schema.dump(row), count + 1
    if get or false:
        return songs
    return custom_response(songs, 200)


@media_api.route('/allMediaGenre', methods=['GET'])
def get_all_musicals_genres():
    """ Return all music genre in database with images"""

    with open('music_genres/' + "Genre_musical.json") as f:
        all_region = json.load(f)
    data, count = {}, 0
    for x in all_region:
        data[count], count = {"genre": x, "image": all_region[x]["image"]}, count + 1
    return custom_response(data, 200)


@media_api.route('/pres_listened/<int:song_id>', methods=['PUT'])
@Auth.auth_required
def increment_song_pres_listened(song_id, user_connected_model, user_connected_schema):
    """ increment number pres listen on this song """

    song = Media.get_song_by_id(song_id)
    if not song:
        return custom_response("Song not found", 200)
    media = media_schema.dump(song)
    media["pres_listened"] += 1
    song.update(media)
    now = datetime.datetime.now().strftime("%Y-%m")
    artist_story_on_this_month = ArtistHistory.get_by_user_id(media_schema.dump(song).get('user_id'))
    schema_artist_story_on_this_month = month_story_schema.dump(artist_story_on_this_month)
    if not schema_artist_story_on_this_month['months_story'].get(str(now)):
        schema_artist_story_on_this_month['months_story'].update(create_artist_new_story_dict())
    schema_artist_story_on_this_month['months_story'][str(now)]['month_pre_stream'] += 1
    artist_story_on_this_month.update(schema_artist_story_on_this_month)
    return custom_response("Pres listened", 200)


@media_api.route('/listened/<int:song_id>', methods=['PUT'])
@Auth.auth_required
def increment_song_view(song_id, user_connected_model, user_connected_schema):
    """ increment number view on this song """

    song = Media.get_song_by_id(song_id)
    if not song:
        return custom_response("Song not found", 200)
    listened = Listened.user_admire_song(song_id, user_connected_model.id)
    if listened:
        _listened = listened_schema.dump(listened)
        _listened['number_of_listening'] += 1
        listened.update(_listened)
        return custom_response("updated number_of_listening on this song", 200)
    new_song_listened = Listened(dict(user_id=user_connected_model.id, song_id=song_id))
    new_song_listened.save()
    now = datetime.datetime.now().strftime("%Y-%m")
    artist_story_on_this_month = ArtistHistory.get_by_user_id(media_schema.dump(song).get('user_id'))
    schema_artist_story_on_this_month = month_story_schema.dump(artist_story_on_this_month)
    if not schema_artist_story_on_this_month['months_story'].get(str(now)):
        schema_artist_story_on_this_month['months_story'].update(create_artist_new_story_dict())
    schema_artist_story_on_this_month['months_story'][str(now)]['month_stream'] += 1
    artist_story_on_this_month.update(schema_artist_story_on_this_month)
    media = media_schema.dump(song)
    media["number_play"] += 1
    song.update(media)
    return custom_response("listened", 200)


@media_api.route('/admire/<int:song_id>', methods=['POST'])
@Auth.auth_required
def new_media_admire(song_id, user_connected_model, user_connected_schema):
    """ your new song admire """

    song = Media.get_song_by_id(song_id)
    if not song:
        return custom_response("Song not found", 200)
    _song = media_schema.dump(song)
    admire_ = Admiration.user_admire_song(song_id, user_connected_model.id)
    if admire_:
        return custom_response("already liked", 400)
    new_song_admired = Admiration(dict(user_id=user_connected_model.id, song_id=song_id))
    new_song_admired.save()
    return custom_response("admired", 200)


@media_api.route('/uploadMedia', methods=['POST'])
@Auth.auth_required
@Secure.music_verification_before_upload
def upload_one_media(uploaded_file, photo_file, data, user_connected_model, user_connected_schema):
    """ Upload One Media """

    data['bpm'], data['time'] = librosa_collect(uploaded_file)
    user_profile_info = profile_schema.dump(user_connected_model.profile)
    if photo_file:
        link = add_in_storage(bucket_images, user_connected_schema, photo_file, file_storage='music/')
    else:
        link = user_profile_info.get("photo") if user_profile_info.get("photo") else None
    data["storage_name"], data["user_id"], data["photo"] = uploaded_file.filename, user_connected_schema.get('id'), link
    media = Media(data)
    update_medias_shared(data, user_connected_model, user_connected_schema)
    media.save()
    media = media_schema.dump(media)
    media['link'] = add_in_storage(bucket_audios, user_connected_schema, uploaded_file)
    return custom_response(media, 200)


@media_api.route('/single/<int:song_id>', methods=['GET'])
def get_media(song_id, not_json=False):
    """ Ge single media """

    media = Media.get_song_by_id(song_id)
    if not media:
        return custom_response("id not found", 400)
    media_song = media_schema.dump(media)
    generate_url = requests.get(request.host_url + 'api/medias/Streaming/' + str(media_song.get('id')))
    if generate_url.status_code != 200:
        return custom_response("error in function streaming", 400)
    link, data_song = json.loads(generate_url.text), {}
    data_song = media_song
    data_song["link"] = link
    if not_json:
        return data_song, media
    return custom_response(data_song, 200)


@media_api.route('/Streaming/<int:song_id>', methods=['GET'])
def stream(song_id):
    """ get stream link song """

    if get_one_media(song_id, get=True):
        return custom_response(stream_song_public_url(True, song_id), 200)
    return custom_response('Do not song in Database', 400)


@media_api.route('/genre/music/<string:genre>', methods=['GET'])
def get_all_song_by_music_genre(genre, not_json=False):
    """ Get all song not beats genre """

    if genre in allowed_genres:
        if not_json:
            return all_medias_in_genre(genre, "music", with_link=True, not_json=True)
        return all_medias_in_genre(genre, "music", with_link=True)
    return custom_response("Not genre existing in database", 400)


@media_api.route('/genre/beats/<string:genre>', methods=['GET'])
def get_all_song_by_beats_genre(genre, not_json=False, with_link=True):
    """ Get all song beats genre"""

    if genre in allowed_genres:
        if not_json:
            return all_medias_in_genre(genre, "music", with_link=with_link, not_json=True)
        return all_medias_in_genre(genre, "beats", with_link=True)
    return custom_response("Not genre existing in database", 400)


@media_api.route('/delete/<int:song_id>', methods=['DELETE'])
@Auth.auth_required
def delete_media(song_id, user_connected_model, user_connected_schema):
    """ Delete one song """

    media, args = user_connected_model.medias.filter_by(id=song_id).first(), {}
    if media:
        args['delete'] = True
        media_song = media_schema.dump(media)
        if media_song["photo"]:
            link_split_list = media_song["photo"].split("/", 3)
            _, _, user_repo, file_name = link_split_list[3].split("/", 4)
            repository_name, user_id = user_repo.split("_")
            repository_name = "music/" + repository_name
            args['bucket_name'], args['repository_name'] = bucket_images, repository_name
            args['keys'], args['filename'], args['file'] = user_id, file_name, None
            update_file_storage(args)
        args['bucket_name'], args['repository_name'] = bucket_audios, user_connected_model.fileStorage_key
        args['keys'], args['filename'], args['file'] = user_connected_model.id, media_song["storage_name"], None
        update_file_storage(args)
        media.delete()
        d_delete("albums_and_songs", "songs", {"id": media_song['id']}, {"storage_name": media_song['storage_name']})
        return custom_response("Deleted", 200)
    return custom_response("file not found or deleted", 400)


@media_api.route('/all_user_songs_and_albums', methods=['GET'])
@Auth.auth_required
def get_all_user_songs_and_albums(user_connected_model, user_connected_schema):
    """ get all user song information in database """

    beats = []
    user_beats = user_connected_model.medias.filter_by(album_id=None, genre_musical="beats").all()

    if user_beats:
        beats.append([media_schema.dump(beat) for beat in user_beats])

    return custom_response({"beats": beats[0] if len(beats) != 0 else beats}, 200)


@media_api.route('/medias_suggestion/<string:music_type>', methods=['GET'])
@Auth.auth_required
def get_all_latest_medias_for_users(music_type, user_connected_model, user_connected_schema):
    """ get all latest medias shared by all user admire """

    if music_type not in allowed_genre_musical:
        return custom_response("music type not allowed", 400)

    user_genre_list = user_connected_model.user_genre_list
    return custom_response(media_beat_suggestion(user_genre_list, music_type, user_connected_model.id), 200)


@media_api.route('/add_users_genre', methods=['POST'])
@Auth.auth_required
def add_user_genre_admire(user_connected_model, user_connected_schema):
    """ add new list of genre admire user"""

    data = request.get_json()
    if not data.get("user_genre_list"):
        return custom_response("user genre list not found", 400)
    user_connected_schema["user_genre_list"] = data.get("user_genre_list")
    user_connected_model.update(user_connected_schema)
    return custom_response("Added successful", 200)


@media_api.route('/update_users_genre', methods=['PUT'])
@Auth.auth_required
def update_user_genre_admire(user_connected_model, user_connected_schema):
    """ update list of genre admire user """

    data = request.get_json()
    if not data.get("user_genre_list"):
        return custom_response("user genre list not found", 400)
    user_connected_schema['user_genre_list'] = data.get("user_genre_list")
    user_connected_model.update(user_connected_schema)
    return custom_response("Updated successful", 200)


@media_api.route('/updateMedia/<int:song_id>', methods=['PUT'])
@Auth.auth_required
@Secure.music_before_update
def update_one_media(song_id, **kwargs):
    """ Update Song """

    kwargs['up']['keys'] = kwargs['ser_user']['id']
    info_base_song = media_schema.dump(kwargs['song'])
    if kwargs['up_file']:
        if info_base_song["storage_name"] != kwargs['up_file'].filename:
            kwargs['up']['filename'], kwargs['up']['file'] = kwargs['up_file'].filename, kwargs['up_file']
            kwargs['data']["storage_name"] = kwargs['up_file'].filename
            kwargs['up']['bucket_name'], kwargs['up']['get'] = bucket_audios, False
            kwargs['up']['repository_name'], kwargs['up']['delete'] = kwargs['ser_user']['fileStorage_key'], False
            update_file_storage(kwargs['up'])
        else:
            kwargs['data']["storage_name"] = info_base_song.get('storage_name')
    else:
        kwargs['data']["storage_name"] = info_base_song.get('storage_name')
    if request.files.get('photo'):
        uploaded_photo = request.files.get('photo')
        link_split_list = info_base_song["photo"].split("/", 3)
        _, _, user_repo, file_name = link_split_list[3].split("/", 4)
        repository_name, user_id = user_repo.split("_")
        repository_name, kwargs['up']['bucket_name'] = "music/" + repository_name, bucket_images
        kwargs['up']['repository_name'], kwargs['up']['delete'] = repository_name, True
        kwargs['up']['keys'], kwargs['up']['filename'], kwargs['up']['file'] = user_id, file_name, None
        update_file_storage(kwargs['up'])
        kwargs['up']['delete'] = False
        kwargs['up']['repository_name'] = 'music/' + kwargs['ser_user']['fileStorage_key']
        kwargs['up']['bucket_name'], kwargs['up']['file'], kwargs['up']['get'] = bucket_images, uploaded_photo, True
        kwargs['data']['photo'] = update_file_storage(kwargs['up'])
    kwargs['data']["admire"] = info_base_song["admire"]
    kwargs['song'].update(kwargs['data'])
    return custom_response("Update", 200)


@media_api.route('/stream_public/<int:song_id>', methods=['GET'])
def stream_song_public_url(private=None, song_id=None):
    """ Streaming song online """

    if private and not song_id:
        return custom_response("send me the song id", 400)
    media = Media.get_song_by_id(song_id)
    if media:
        data_s = media_schema.dump(media)
        user_info, storage_client = user_schema.dump(User.get_one_user(data_s['user_id'])), storage.Client()
        file_storage = user_info.get('fileStorage_key') + '_' + str(user_info.get('id'))
        if data_s['album_id']:
            bucket = storage_client.get_bucket(bucket_albums)
            alb_key = albumSchema.dump(Albums.get_album_id(data_s['album_id']))["keys"]
            file_storage = user_info.get('fileStorage_key') + '_' + str(alb_key)
            blob = bucket.blob(file_storage + '_' + str(user_info.get('id')) + '/' + data_s['storage_name'])
        elif data_s['genre_musical'] == "beats":
            bucket = storage_client.get_bucket(bucket_beats)
            blob = bucket.blob("mp3_beats/" + file_storage + '/' + data_s['storage_name'])
        else:
            bucket = storage_client.get_bucket(bucket_audios)
            blob = bucket.blob(file_storage + '/' + data_s['storage_name'])
        if private:
            return blob.generate_signed_url(expiration=datetime.timedelta(hours=1))
        blob.make_public()
        return custom_response(blob.public_url, 200)
    return custom_response('do not song in database', 400)
