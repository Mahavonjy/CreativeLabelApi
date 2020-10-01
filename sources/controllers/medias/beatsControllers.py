#!/usr/bin/env python3
""" shebang """

import os

import cloudinary
from flask import request
from flask import g as auth
from flask import Blueprint, json
from preferences import CLOUD_IMAGES_BEATS_TYPE, defaultData, GOOGLE_BUCKET_BEATS

from auth.authentification import Auth
from sources.models.users.user import User, UserSchema
from sources.models.medias.media import Media, MediaSchema
from sources.security.verification import Secure
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import destroy_beats, destroy_image, librosa_collect, Percent, random_string, upload_beats, \
    upload_image
from sources.models import custom_response

beats_api = Blueprint('beats', __name__)
media_schema = MediaSchema()
profile_schema = ProfileSchema()
bucket_beats = GOOGLE_BUCKET_BEATS
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


def check_time_and_bpm(audio, data, update_bpm=False):

    audio.seek(0)
    bpm_, time_ = librosa_collect(audio)
    if not data.get('bpm', 0) or update_bpm:
        data['bpm'] = bpm_
    data['time'] = time_
    return data


@beats_api.route('/uploadBeat', methods=['POST'])
@Auth.auth_required
@Secure.beats_verification_before_upload
def upload_beat(user_connected_schema, user_connected_model, data, mp3, wave, photo, stems):
    """ function who upload beats """

    _u_model = user_connected_model
    data['basic_price'] = price_calculation(data['basic_price'])
    data['silver_price'] = price_calculation(data['silver_price'])
    data['gold_price'] = price_calculation(data['gold_price'])
    if data['platinum_price']:
        data['platinum_price'] = price_calculation(data['platinum_price'])

    photo.filename = random_string(string_length=10) + "." + photo.content_type.split('/')[1]
    link = _u_model.profile.photo
    if photo:
        link = upload_image(photo, CLOUD_IMAGES_BEATS_TYPE, _u_model.fileStorage_key, _u_model.id)

    data = check_time_and_bpm(mp3, data)
    mp3.seek(0)
    f_storage_id = {'fileStorage_key': _u_model.fileStorage_key, 'user_id': _u_model.id}
    data.update({
        'photo': link,
        'user_id': _u_model.id,
        'mp3': upload_beats(mp3, **f_storage_id),
        'stems': upload_beats(stems, **f_storage_id, stems=True),
        'wave': upload_beats(wave, **f_storage_id)
    })
    media = Media(data)
    media.save()
    return custom_response(media_schema.dump(media), 200)


@beats_api.route('/updateBeat/<int:song_id>', methods=['PUT'])
@Auth.auth_required
@Secure.beats_verification_before_update
def update_beats(song_id, user_connected_schema, user_connected_model, data, mp3, wave, photo, stems, beats):
    """ function who update a beats """

    _u_model = user_connected_model
    beats_to_update = media_schema.dump(beats)
    params = {'fileStorage_key': _u_model.fileStorage_key, 'user_id': _u_model.id}

    if photo:
        destroy_image(beats_to_update["photo"], CLOUD_IMAGES_BEATS_TYPE, **params)
        beats_to_update["photo"] = upload_image(photo, CLOUD_IMAGES_BEATS_TYPE, **params)

    if stems:
        destroy_beats(beats_to_update["stems"], **params, stems=True)
        beats_to_update["stems"] = upload_beats(stems, **params, stems=True)

    if mp3:
        beats_to_update = check_time_and_bpm(mp3, beats_to_update, update_bpm=True)
        mp3.seek(0)
        destroy_beats(beats_to_update["mp3"], **params)
        beats_to_update["mp3"] = upload_beats(mp3, **params)

    if wave:
        destroy_beats(beats_to_update["wave"], **params)
        beats_to_update["wave"] = upload_beats(wave, **params)

    beats_to_update.update(data)
    beats.update(beats_to_update)
    return custom_response(media_schema.dump(beats), 200)


@beats_api.route('/delete/<int:song_id>', methods=['DELETE'])
@Auth.auth_required
def delete_beats(song_id, user_connected_model, user_connected_schema):
    """ delete a beats """

    user_ = user_connected_model
    beat = user_.medias.filter_by(id=song_id).first()

    if beat:
        params = {'fileStorage_key': user_.fileStorage_key, 'user_id': user_.id}
        beat_to_delete = media_schema.dump(beat)

        if beat_to_delete['photo']:
            destroy_image(beat_to_delete["photo"], CLOUD_IMAGES_BEATS_TYPE, **params)

        if beat_to_delete["stems"]:
            destroy_beats(beat_to_delete["stems"], **params, stems=True)

        if beat_to_delete["mp3"]:
            destroy_beats(beat_to_delete["mp3"], **params)

        if beat_to_delete["wave"]:
            destroy_beats(beat_to_delete["wave"], **params)

        beat.delete()
        return custom_response("deleted", 200)
    return custom_response("beat not found or deleted", 400)


"""
Here begins the beats suggestion functions
"""


def check_list_of_beats(list_of_beats_model, with_link=False):
    """ return list of beats with link """

    all_beats = []
    for beat in list_of_beats_model:
        if with_link:
            media_ = media_schema.dump(beat)
            # media_['link'] = stream_song_public_url(True, beat.id)
            all_beats.append(media_)
            continue
        all_beats.append(media_schema.dump(beat))

    return all_beats


@beats_api.route('/OneBeat/<int:song_id>', methods=['GET'])
def get_one_beats(song_id):
    """ get one beats """

    # try:
        # the_beat, media = get_media(song_id=song_id, not_json=True)
        # try:
        #     if the_beat.status_code == 400:
        #         return custom_response("not found", 400)
        # except AttributeError:
        #     pass
    # except TypeError:
    #     return custom_response("not found", 400)

    # all_user_beats = User.get_one_user(media.user_id).medias.filter_by(genre_musical='beats').all()
    # similar_beats = get_all_song_by_beats_genre(media.genre, not_json=True, with_link=False)
    return custom_response({
        # "single_beat": the_beat,
        # "all_artist_beats": [media_schema.dump(beat) for beat in all_user_beats],
        # "similar_beats": [media_schema.dump(beat) for beat in similar_beats],
    }, 200)


@beats_api.route('/allMediaGenre', methods=['GET'])
def get_all_musicals_genres():
    """ Return all music genre in database with images"""

    with open('music_genres/' + "Genre_musical.json") as f:
        all_region = json.load(f)
    data, count = {}, 0
    for x in all_region:
        data[count], count = {"genre": x, "image": all_region[x]["image"]}, count + 1
    return custom_response(data, 200)


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
        artist_profile['number_of_beats'] = User.get_one_user(beat.user_id)\
                                                .medias.filter_by(genre_musical='beats').count(),
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
        # top_beatmaker=get_top_beat_maker_beats(json_response=True),
        # latest_beats=get_top_latest_beats(json_response=True),
        # discovery_beats=african_discovery_beats(json_response=True),
        # new_beatMaker=all_new_beat_maker_in_the_six_last_month(json_response=True),
        # isl_playlist=isl_beats_playlist(json_response=True)
    ), 200)


"""
End beats suggestion functions
"""


@beats_api.route('/pricing', methods=['GET'])
@Auth.auth_required
def get_beats_pricing(user_connected_model, user_connected_schema):
    """ get beats pricing order """

    pricing = defaultData.beats_pricing
    for contract in pricing:
        user_contract = user_connected_model.ContractBeat.filter_by(contract_name=contract + "_lease").first()
        if user_contract and user_contract.enabled:
            pricing[contract] = user_contract.price
    return custom_response(pricing, 200)
