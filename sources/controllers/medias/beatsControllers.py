#!/usr/bin/env python3
""" shebang """

from flask import g as auth
from flask import Blueprint
from sources.controllers import random_string
from preferences import defaultDataConf

from auth.authentification import Auth
from sources.models.users.user import User, UserSchema
from sources.models.medias.media import Media, MediaSchema
from sources.controllers.security.verification import Secure
from sources.models.profiles.profile import ProfileSchema
from sources.controllers.tools.tools import librosa_collect
from sources.controllers import update_medias_shared, update_file_storage
from sources.models import custom_response, add_in_storage as add_s, Percent
from sources.controllers.medias.mediaControllers import get_media, stream_song_public_url, get_all_song_by_beats_genre

beats_api = Blueprint('beats', __name__)
media_schema = MediaSchema()
profile_schema = ProfileSchema()
bucket_images = defaultDataConf.GOOGLE_BUCKET_IMAGES
bucket_beats = defaultDataConf.GOOGLE_BUCKET_BEATS
user_schema = UserSchema()
percent_isl_creative = 30
percent_tva = 20


def price_calculation(beat_maker_gain):
    """ this function determinate the price of beats """

    gain_beat_maker = beat_maker_gain
    price_purchased = float(100) * beat_maker_gain / 70.00
    gain_isl = Percent(price_purchased, percent_isl_creative).result
    tva = Percent(price_purchased, percent_tva).result

    return round(sum([gain_isl, tva, gain_beat_maker])) - 0.01


@beats_api.route('/uploadBeat', methods=['POST'])
@Auth.auth_required
@Secure.beats_verification_before_upload
def upload_beats(*args, **kwargs):
    """ function who upload beats """

    kwargs['data']['basic_price'] = price_calculation(kwargs['data']['basic_price'])
    kwargs['data']['silver_price'] = price_calculation(kwargs['data']['silver_price'])
    kwargs['data']['gold_price'] = price_calculation(kwargs['data']['gold_price'])
    if kwargs['data']['platinum_price']:
        kwargs['data']['platinum_price'] = price_calculation(kwargs['data']['platinum_price'])
    bpm_, time_ = librosa_collect(kwargs['uploaded_file_mp3'])
    if not kwargs['data']['bpm']:
        kwargs['data']['bpm'] = bpm_
    kwargs['data']['time'] = time_
    user_profile_info = profile_schema.dump(kwargs['user_connected_model'].profile)
    photo_file_type = kwargs['photo_file'].content_type
    kwargs['photo_file'].filename = random_string(string_length=10) + "." + photo_file_type.split('/')[1]
    if kwargs['photo_file']:
        link = add_s(bucket_images, kwargs['user_connected_schema'], kwargs['photo_file'], file_storage='beats/')
    else:
        link = user_profile_info.get("photo") if user_profile_info.get("photo") else None
    beat_link = add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_file_mp3'], beats="mp3_beats")
    add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_file_wave'], beats="wave_beats")
    add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_samples'], beats="stems_beats")
    kwargs['data']["photo"] = link
    kwargs['data']["storage_name"] = kwargs['uploaded_file_mp3'].filename
    kwargs['data']["user_id"] = kwargs['user_connected_schema']['id']
    kwargs['data']['beats_wave'] = kwargs['uploaded_file_wave'].filename
    kwargs['data']['stems'] = kwargs['uploaded_samples'].filename
    media = Media(kwargs['data'])
    update_medias_shared(kwargs['data'], kwargs['user_connected_model'], kwargs['user_connected_schema'])
    media.save()
    beats = media_schema.dump(media)
    beats['link'] = beat_link
    return custom_response(beats, 200)


@beats_api.route('/update/<int:song_id>', methods=['PUT'])
@Auth.auth_required
@Secure.beats_verification_before_update
def update_beats(song_id, **kwargs):
    """ function who update a beats """

    beats = media_schema.dump(kwargs['beats'])
    file_storage_key = kwargs['user_connected_schema']['fileStorage_key']
    kwargs['data']['photo'], beat_link = beats['photo'], ''

    if kwargs['photo_file']:
        _split_list = beats["photo"].split("/", 3)
        _, _, user_repo, file_name = _split_list[3].split("/", 4)
        repository_name, user_id = user_repo.split("_")
        update_file_storage(dict(
            bucket_name=bucket_images, repository_name="beats/" + repository_name,
            delete=True, keys=user_id, filename=file_name, file=None
        ))
        kwargs['data']['photo'] = add_s(
            bucket_images, kwargs['user_connected_schema'], kwargs['photo_file'], file_storage='beats/'
        )
    if kwargs['uploaded_samples']:
        update_file_storage(dict(
            bucket_name=bucket_beats, repository_name="stems_beats/" + file_storage_key,
            delete=True, keys=kwargs['user_connected_schema']['id'], filename=beats['stems'], file=None
        ))
        add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_samples'], beats="stems_beats")
        kwargs['data']['stems'] = kwargs['uploaded_samples'].filename
    if kwargs['uploaded_file_mp3']:
        update_file_storage(dict(
            bucket_name=bucket_beats, repository_name="mp3_beats/" + file_storage_key,
            delete=True, keys=kwargs['user_connected_schema']['id'], filename=beats['storage_name'], file=None
        ))
        beat_link = add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_file_mp3'], beats="mp3_beats")
        kwargs['data']['storage_name'] = kwargs['uploaded_file_mp3'].filename
    if kwargs['uploaded_file_wave']:
        update_file_storage(dict(
            bucket_name=bucket_beats, repository_name="wave_beats/" + file_storage_key,
            delete=True, keys=kwargs['user_connected_schema']['id'], filename=beats['beats_wave'], file=None
        ))
        add_s(bucket_beats, kwargs['user_connected_schema'], kwargs['uploaded_file_wave'], beats="wave_beats")
        kwargs['data']['beats_wave'] = kwargs['uploaded_file_wave'].filename
    beats.update(kwargs['data'])
    kwargs['beats'].update(beats)
    beats['link'] = beat_link

    return custom_response(beats, 200)


@beats_api.route('/delete/<int:song_id>', methods=['DELETE'])
@Auth.auth_required
def delete_beats(song_id, user_connected_model, user_connected_schema):
    """ delete a beats """

    user_ = User.get_one_user(auth.user.get('id'))
    media = user_.medias.filter_by(id=song_id).first()

    if media:
        ser_user = user_schema.dump(user_)
        beats = media_schema.dump(media)
        list_ = []
        # delete a beats mp3
        list_.extend([("bucket_name", bucket_beats), ("repository_name", "mp3_beats/" + ser_user['fileStorage_key'])])
        list_.extend([("delete", True), ("keys", ser_user['id']), ("filename", beats['storage_name']), ("file", None)])
        update_file_storage(dict(list_))
        # delete a beats photo
        try:
            _split_list = beats["photo"].split("/", 3)
            _, _, user_repo, file_name = _split_list[3].split("/", 4)
            repository_name, user_id = user_repo.split("_")
            update_file_storage(dict(
                bucket_name=bucket_images, repository_name="beats/" + repository_name,
                delete=True, keys=user_id, filename=file_name, file=None
            ))
        except AttributeError:
            pass
        # delete a beats stems
        update_file_storage(dict(
            bucket_name=bucket_beats, repository_name="stems_beats/" + ser_user['fileStorage_key'],
            delete=True, keys=ser_user['id'], filename=beats['stems'], file=None
        ))
        # delete a beats wave
        update_file_storage(dict(
            bucket_name=bucket_beats, repository_name="wave_beats/" + ser_user['fileStorage_key'],
            delete=True, keys=ser_user['id'], filename=beats['beats_wave'], file=None
        ))
        media.delete()
        return custom_response("delete", 200)
    return custom_response("file not found or deleted", 400)


"""
Here begins the beats suggestion functions
"""


def check_list_of_beats(list_of_beats_model, with_link=False):
    """ return list of beats with link """

    all_beats = []
    for beat in list_of_beats_model:
        if with_link:
            media_ = media_schema.dump(beat)
            media_['link'] = stream_song_public_url(True, beat.id)
            all_beats.append(media_)
            continue
        all_beats.append(media_schema.dump(beat))

    return all_beats


@beats_api.route('/OneBeat/<int:song_id>', methods=['GET'])
def get_one_beats(song_id):
    """ get one beats """

    try:
        the_beat, media = get_media(song_id=song_id, not_json=True)
        try:
            if the_beat.status_code == 400:
                return custom_response("not found", 400)
        except AttributeError:
            pass
    except TypeError:
        return custom_response("not found", 400)

    all_user_beats = User.get_one_user(media.user_id).medias.filter_by(album_id=None, genre_musical='beats').all()
    similar_beats = get_all_song_by_beats_genre(media.genre, not_json=True, with_link=False)
    return custom_response({
        "single_beat": the_beat,
        "all_artist_beats": [media_schema.dump(beat) for beat in all_user_beats],
        "similar_beats": [media_schema.dump(beat) for beat in similar_beats],
    }, 200)


@beats_api.route('/random', methods=['GET'])
def get_random_beats(json_response=False):
    """ get 10 beats random in DB """

    all_beats = check_list_of_beats(Media.randomize_beats())
    if json_response:
        return all_beats
    return custom_response({"random": all_beats}, 200)


@beats_api.route('/increasing', methods=['GET'])
def get_increasing_beats(json_response=False):
    """ get 10 beats random in DB """

    all_beats = check_list_of_beats(Media.increasing_beats())
    if json_response:
        return all_beats
    return custom_response({"increasing": all_beats}, 200)


@beats_api.route('/descending', methods=['GET'])
def get_descending_beats(json_response=False):
    """ get 10 beats random in DB """

    all_beats = check_list_of_beats(Media.descending_beats())
    if json_response:
        return all_beats
    return custom_response({"descending": all_beats}, 200)


@beats_api.route('/topBeatmaker', methods=['GET'])
def get_top_beat_maker_beats(json_response=False):
    """ get 10 beats random in DB """

    beat_artist = []
    for beat in Media.top_beats_3_last_month():
        artist_profile = profile_schema.dump(User.get_one_user(beat.user_id).profile)
        artist_profile['number_of_beats'] = User.get_one_user(beat.user_id).beats_shared
        if artist_profile not in beat_artist:
            beat_artist.append(artist_profile)
    if json_response:
        return beat_artist
    return custom_response({"top_beatmaker": beat_artist}, 200)


@beats_api.route('/topBeats', methods=['GET'])
def get_top_beats(json_response=False):
    """ top beat at the three last month """

    all_beats = check_list_of_beats(Media.top_beats_3_last_month())
    if json_response:
        return all_beats
    return custom_response({"top_beats": all_beats}, 200)


@beats_api.route('/LatestBeats', methods=['GET'])
def get_top_latest_beats(json_response=False):
    """ get 10 beats random in DB """

    all_beats = check_list_of_beats(Media.ten_last_beats())
    if json_response:
        return all_beats
    return custom_response({"latest_beats": all_beats}, 200)


@beats_api.route('/discoveryBeats', methods=['GET'])
def african_discovery_beats(json_response=False):
    """ Check african specific beat style """

    all_beats, _beats = Media.african_discovery_beats(), []
    if all_beats[0]:
        try:
            for beat in [beats for beats in all_beats]:
                _beats.append(media_schema.dump(beat[0]))
        except IndexError:
            pass

    if json_response:
        return _beats
    return custom_response({"discovery_beats": _beats}, 200)


@beats_api.route('/NewBeatMakers', methods=['GET'])
def all_new_beat_maker_in_the_six_last_month(json_response=False):
    """ new beatMaker in the six last month with one or plus beats shared """

    artist_profile = [profile_schema.dump(_user.profile) for _user in User.all_beat_maker_in_three_last_month()]
    if json_response:
        return artist_profile
    return custom_response({"new_beatMaker": artist_profile}, 200)


@beats_api.route('/IslPlaylist', methods=['GET'])
def isl_beats_playlist(json_response=False):
    """ Isl beats playlist """

    _all_beats, all_beats = Media.isl_playlist_beats(), []
    if _all_beats:
        all_beats = check_list_of_beats(Media.isl_playlist_beats())

    if json_response:
        return all_beats
    return custom_response({"isl_playlist": all_beats}, 200)


@beats_api.route('/AllSuggestion', methods=['GET'])
def all_beats_suggestion_tried():
    """ tried all function of suggestion and trie it """

    return custom_response(dict(
        random=get_random_beats(json_response=True),
        top_beatmaker=get_top_beat_maker_beats(json_response=True),
        latest_beats=get_top_latest_beats(json_response=True),
        discovery_beats=african_discovery_beats(json_response=True),
        new_beatMaker=all_new_beat_maker_in_the_six_last_month(json_response=True),
        isl_playlist=isl_beats_playlist(json_response=True)
    ), 200)


"""
End beats suggestion functions
"""


@beats_api.route('/pricing', methods=['GET'])
@Auth.auth_required
def get_beats_pricing(user_connected_model, user_connected_schema):
    """ get beats pricing order """

    pricing = defaultDataConf.beats_pricing
    for contract in pricing:
        user_contract = user_connected_model.ContractBeat.filter_by(contract_name=contract + "_lease").first()
        if user_contract and user_contract.enabled:
            pricing[contract] = user_contract.price
    return custom_response(pricing, 200)
