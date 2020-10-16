#!/usr/bin/env python3
""" shebang """

from flask import Blueprint, json
from preferences import CLOUD_IMAGES_BEATS_TYPE, defaultData

from auth.authentification import Auth
from sources.models.admirations.admirations import Admiration, AdmireSchema
from sources.models.elastic.fillInElastic import document_delete
from sources.models.users.user import User, UserSchema
from sources.models.medias.media import Media, MediaSchema
from sources.security.verification import Secure
from sources.models.profiles.profile import ProfileSchema
from sources.tools.tools import check_dict_keys, destroy_beats, destroy_image, librosa_collect, Percent, \
    random_string, upload_beats, upload_image
from sources.models import custom_response, es

beats_api = Blueprint('beats', __name__)
media_schema = MediaSchema()
profile_schema = ProfileSchema()
admiration_schema = AdmireSchema()
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
    b_rm = media_schema.dump(beats)
    params = {'fileStorage_key': _u_model.fileStorage_key, 'user_id': _u_model.id}

    if photo:
        destroy_image(b_rm["photo"], CLOUD_IMAGES_BEATS_TYPE, **params)
        b_rm["photo"] = upload_image(photo, CLOUD_IMAGES_BEATS_TYPE, **params)

    if stems:
        destroy_beats(b_rm["stems"], **params, stems=True)
        b_rm["stems"] = upload_beats(stems, **params, stems=True)

    if mp3:
        b_rm = check_time_and_bpm(mp3, b_rm, update_bpm=True)
        mp3.seek(0)
        destroy_beats(b_rm["mp3"], **params)
        b_rm["mp3"] = upload_beats(mp3, **params)

    if wave:
        destroy_beats(b_rm["wave"], **params)
        b_rm["wave"] = upload_beats(wave, **params)

    document_delete(index="beats", doc_type="songs", first_={"id": song_id}, second_={"created_at": b_rm['created_at']})
    b_rm.update(data)
    beats.update(b_rm)
    return custom_response(media_schema.dump(beats), 200)


@beats_api.route('/delete/<int:song_id>', methods=['DELETE'])
@Auth.auth_required
def delete_beats(song_id, user_connected_model, user_connected_schema):
    """ delete a beats """

    user_ = user_connected_model
    beat = user_.medias.filter_by(id=song_id).first()

    if beat:
        params = {'fileStorage_key': user_.fileStorage_key, 'user_id': user_.id}
        beat_to_rm = media_schema.dump(beat)

        if beat_to_rm['photo']:
            destroy_image(beat_to_rm["photo"], CLOUD_IMAGES_BEATS_TYPE, **params)

        if beat_to_rm["stems"]:
            destroy_beats(beat_to_rm["stems"], **params, stems=True)

        if beat_to_rm["mp3"]:
            destroy_beats(beat_to_rm["mp3"], **params)

        if beat_to_rm["wave"]:
            destroy_beats(beat_to_rm["wave"], **params)

        document_delete(
            index="beats",
            doc_type="songs",
            first_={"id": song_id},
            second_={"created_at": beat_to_rm['created_at']}
        )
        beat.delete()
        return custom_response("deleted", 200)
    return custom_response("beat not found or deleted", 400)


@beats_api.route('/admire_beat/<int:beat_to_admire_id>', methods=['POST'])
@Auth.auth_required
def add_new_admiration_user(beat_to_admire_id, user_connected_model, user_connected_schema):
    """ User add new admiration """

    if not Media.get_song_by_id(beat_to_admire_id):
        return custom_response("Beat not found", 400)

    admire_info = user_connected_model.all_admires.filter_by(beat_id=beat_to_admire_id).first()

    if admire_info:
        return custom_response("exist", 400)

    Admiration(dict(user_id=user_connected_model.id, beat_id=beat_to_admire_id)).save()
    return custom_response("Added", 200)


@beats_api.route('/delete_admire_beat/<int:beat_do_not_admire_id>', methods=['DELETE'])
@Auth.auth_required
def delete_admiration_user(beat_do_not_admire_id, user_connected_model, user_connected_schema):
    """ User delete admiration """

    admire_info = user_connected_model.all_admires.filter_by(beat_id=beat_do_not_admire_id).first()
    if not admire_info:
        return custom_response("Not found", 400)

    admire_info.delete()
    return custom_response("deleted", 200)


@beats_api.route('/all_user_beats_admire/<int:user_id>', methods=['GET'])
def all_beats_admiration(user_id):
    """ get all beats user admiration """

    user = User.get_one_user(user_id)
    if not user:
        return custom_response("user do not exist", 400)

    all_beats = []
    all_admiration = user.all_admires.filter_by(admire_id=None).all()

    for admire in all_admiration:
        _beat = media_schema.dump(admire.beat)
        all_beats.append(_beat)

    return custom_response(all_beats, 200)


@beats_api.route('/my_admire', methods=['GET'])
@Auth.auth_required
def all_my_admiration_beats(user_connected_model, user_connected_schema):
    """ """

    return all_beats_admiration(user_connected_model.id)


@beats_api.route('/my_beats', methods=['GET'])
@Auth.auth_required
def all_user_beats(user_connected_model, user_connected_schema):
    """ return all user beats """

    beats = es.search(
        index="beats",
        doc_type="songs",
        body={
            "query": {
                "bool": {
                    "must": [
                        {"match": {"user_id": user_connected_model.id}}
                    ]
                }
            }
        }
    )

    _all_beats = []
    for beat in beats['hits']['hits']:
        _all_beats.append(check_dict_keys(beat['_source'], ['wave', 'stems'], True))

    return custom_response({"beats": _all_beats}, 200)


@beats_api.route('/allMediaGenre', methods=['GET'])
def get_all_musicals_genres():
    """ Return all music genre in database with images"""

    with open('music_genres/' + "Genre_musical.json") as f:
        all_region = json.load(f)
    data, count = {}, 0
    for x in all_region:
        data[count], count = {"genre": x, "image": all_region[x]["image"]}, count + 1
    return custom_response(data, 200)


@beats_api.route('/pricing', methods=['GET'])
@Auth.auth_required
def get_beats_pricing(user_connected_model, user_connected_schema):
    """ get user pricing order """

    pricing = defaultData.beats_pricing
    for contract in pricing:
        user_contract = user_connected_model.ContractBeat.filter_by(contract_name=contract + "_lease").first()
        if user_contract and user_contract.enabled:
            pricing[contract] = user_contract.price
    return custom_response(pricing, 200)
