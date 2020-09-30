#!/usr/bin/env python3
""" shebang """

import os
import re
import time
import json

import string
import random
import stripe
import librosa
import calendar
import itertools
import marshmallow
import cloudinary.uploader

from datetime import datetime
from functools import reduce
from sqlalchemy import func

from werkzeug.utils import secure_filename

from preferences import CLOUD_BEAT_STEMS, CLOUD_BEATS, CLOUD_IMAGES_FOLDERS

from sources.models.admirations.admirations import AdmireSchema
from sources.models.artists.materials.artistMaterials import MaterialsSchema
from sources.models.artists.options.artistOptions import OptionsSchema
from sources.models.artists.services.artistServices import ServiceSchema
from sources.models.medias.media import MediaSchema
from preferences.defaultData import allowed_cirque_or_child_options, \
    allowed_audio_visual_options, allowed_chant_and_music_options, allowed_beat_maker_options, \
    allowed_magician_options, allowed_comedian_options, allowed_dance_options, allowed_dj_options

media_schema = MediaSchema()
material_schema = MaterialsSchema()
service_schema = ServiceSchema()
option_schema = OptionsSchema()
admire_schema = AdmireSchema()


def upload_image(image_to_upload, cloud_folder, fileStorage_key, user_id):
    """ function who upload images to cloudinary """

    if cloud_folder not in CLOUD_IMAGES_FOLDERS:
        return None

    return cloudinary.uploader.upload(
        image_to_upload,
        public_id=fileStorage_key + str(user_id) + image_to_upload.filename.split(".")[0],
        folder=cloud_folder + "/" + fileStorage_key + str(user_id),
        resource_type='image'
    )['secure_url']


def upload_beats(file_to_upload, fileStorage_key, user_id, stems=False):
    """ function who upload beats to cloudinary """

    folder = CLOUD_BEATS
    if stems:
        folder = CLOUD_BEAT_STEMS

    return cloudinary.uploader.upload(
        file_to_upload,
        public_id=fileStorage_key + str(user_id) + file_to_upload.filename.split(".")[0],
        folder=folder + "/" + fileStorage_key + str(user_id),
        resource_type='auto'
    )['secure_url']


def destroy_beats(image_link, fileStorage_key, user_id):
    """ function who destroy images to cloudinary """

    file_named = image_link.split("/")[-1].split('.')[0]
    return cloudinary.uploader.destroy(
        public_id=CLOUD_BEATS + "/" + fileStorage_key + str(user_id) + "/" + file_named,
        resource_type='auto'
    )


def destroy_image(image_link, cloud_folder, fileStorage_key, user_id):
    """ function who destroy images to cloudinary """

    file_named = image_link.split("/")[-1].split('.')[0]
    return cloudinary.uploader.destroy(
        public_id=cloud_folder + "/" + fileStorage_key + str(user_id) + "/" + file_named,
        resource_type='image'
    )


def merge_suggestion(new_list):
    """

    :param new_list:
    :return: dict merged with suggestion alb for the user
    """
    return [dict(t) for t in {tuple(d.items()) for d in new_list}]


def check_user_options_and_services(user):
    list_of_options, list_of_services = [], []
    all_user_options = user.options.all()
    all_user_services = user.services.all()
    for service, option in itertools.zip_longest(all_user_services, all_user_options):
        if service:
            service_dumped = service_schema.dump(service)
            service_dumped['materials'] = material_schema.dump(service.material)
            list_of_services.append(service_dumped)
        if option:
            option_dumped = option_schema.dump(option)
            option_dumped['materials'] = material_schema.dump(option.material)
            list_of_options.append(option_dumped)
    return {"user_services": list_of_services, "user_options": list_of_options}


def librosa_collect(file):
    """

    :param file:
    :return: dict of time and bpm
    """

    dirname = random_string()
    file.save(secure_filename(dirname + file.filename))
    y, sr = librosa.load(dirname + file.filename)
    bpm, beats_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats_times = librosa.frames_to_time(beats_frames, sr=sr)
    time_ = time.strftime('%H:%M:%S', time.gmtime(int(round(beats_times[-1]))))
    try:
        tm = time_[3:] if time_.split(":")[0] == "00" else time_
    except TypeError:
        tm = None
    os.remove(dirname + file.filename)
    return bpm, tm


# calculate the percent value
class Percent:
    """ calc percent """

    def __init__(self, base=None, percentage=None):
        self.result = float(base) * float(percentage) / float(100)


def check_reservation_info_with_service_info(reservation_basic_schema, Services, User, data_to_dump, req=None):
    tmp = reservation_basic_schema.dump(data_to_dump)
    tmp["title"] = Services.get_by_service_id(tmp["services_id"]).title
    tmp["artist_name"] = User.get_one_user(tmp["artist_owner_id"]).name
    tmp["auditor_name"] = User.get_one_user(tmp["auditor_who_reserve_id"]).name
    if req:
        return {"reservations": tmp}
    return tmp


def check_all_user_payment_history(user_connected_model, p_h_schema, User, Reservations):
    payment_history_obj = []
    payment_list = user_connected_model.purchased_history.all() + user_connected_model.purchase_history.all()
    if payment_list:
        for p in payment_list:
            p_h_obj = p_h_schema.dump(p)
            p_h_obj["buyer_name"] = User.get_one_user(p_h_obj["buyer_id"]).name
            p_h_obj["artist_name"] = User.get_one_user(p_h_obj["artist_id"]).name
            try:
                reservation_tmp = Reservations.get_reservation_by_payment_history_id(p_h_obj["id"])
                p_h_obj["event"] = reservation_tmp.event
                p_h_obj["invoice"] = reservation_tmp.invoice
                p_h_obj["services_id"] = reservation_tmp.services_id
            except AttributeError:
                p_h_obj["event"] = ""
            payment_history_obj.append(p_h_obj)
    return payment_history_obj


def payment_stripe(total_price, stripe_token_id, description):
    """

    :param total_price: this is a amount for user paid
    :param stripe_token_id: token for payment stripe
    :param description: some description payment
    :return: return result off creating stripe charge
    """

    return stripe.Charge.create(
        amount=int(total_price * 100),
        currency="eur",
        description=description,
        source=stripe_token_id
    )


def check_validations_errors(resp, key):
    new_resp = resp[key]
    new_key = list(new_resp)[0]
    tmp = new_resp[new_key][0].replace('Field', key)
    if not bool(new_resp[new_key][0].find('Field')):
        tmp = tmp.replace('Field', key)
        return tmp.replace('data', new_key), True
    if not bool(tmp.find('data')):
        tmp = tmp.replace('data', new_key)
    if not bool(tmp.find(new_key)):
        pass
    else:
        tmp = new_key + " " + tmp
    return tmp.replace('field', key), True


def random_int():
    return random.randint(1111, 9999) * 9999


def random_string(string_length=100):
    """Generate a random string of fixed length """

    return ''.join(random.choice(string.ascii_lowercase) for i in range(string_length))


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
                *convert_dict_to_sql_json(
                    None, list(reduce(lambda x, y: x + y, value.items()))
                )
            )

    return data_list


# compare time created_at with now time
def get_time(created_at, min_value: int) -> bool:
    """ compare created time and now """

    now_time = datetime.datetime.now()
    date, rest = created_at.split('T')
    hour, _ = rest.split('.')
    hours, min_, sec = hour.split(":")
    year, month, day = date.split('-', 3)
    date_for_created_cart = datetime.datetime(int(year), int(month), int(day), int(hours), int(min_), int(sec))
    x = now_time - date_for_created_cart
    return divmod(x.days * 86400 + x.seconds, 60)[0] <= min_value


def validate_data(_schema, requested, return_dict=True):
    """

    @param requested: the data
    @param _schema: marshmallow schmema for my validation
    @param return_dict: if the data is a form or Json
    :return: json or error message
    """

    try:
        if return_dict:
            return _schema.load(requested.get_json()), False

        data = requested.form.to_dict(flat=True)
        if data.get("services") and data.get("password"):
            if not data.get("user_type"):
                return "I need user_type", True
            data['services'] = json.loads(data['services'])
            user_type_ = data.get('user_type')
            thematics = data.get('services').get('thematics')
            if thematics:
                for thematic in thematics:
                    if user_type_ == "dj" and thematic not in allowed_dj_options or \
                            user_type_ == "dancers" and thematic not in allowed_dance_options or \
                            user_type_ == "comedian" and thematic not in allowed_comedian_options or \
                            user_type_ == "magician" and thematic not in allowed_magician_options or \
                            user_type_ == "beatmaker" and thematic not in allowed_beat_maker_options or \
                            user_type_ == "artist_musician" and thematic not in allowed_chant_and_music_options or \
                            user_type_ == "audiovisual_specialist" and thematic not in allowed_audio_visual_options or \
                            user_type_ == "street_artists" and thematic not in allowed_cirque_or_child_options:
                        return user_type_ + " type don't match with thematics", True
            return _schema.load(data), False

        if data.get('services_id_list') and len(data.get('services_id_list')) != 0:
            data['services_id_list'] = re.sub(r'\"', '',
                                              data['services_id_list'][2:len(data['services_id_list']) - 2]).split(",")
        if data.get('list_of_materials'):
            tmp_list = re.sub(r'\"', '', data['list_of_materials'][2:len(data['list_of_materials']) - 2]).split(",")
            data['list_of_materials'] = tmp_list

        if data.get('events') and data.get('others_city') and data.get('thematics') and data.get('special_dates'):
            data['events'] = re.sub(r'\"', '', data['events'][2:len(data['events']) - 2]).split(",")
            data['thematics'] = re.sub(r'\"', '', data['thematics'][2:len(data['thematics']) - 2]).split(",")
            data['others_city'] = re.sub(r'\"', '', data['others_city'][2:len(data['others_city']) - 2]).split(",")

            if data.get('galleries'):
                data['galleries'] = re.sub(r'\"', '', data['galleries'][2:len(data['galleries']) - 2]).split(",")
            data['special_dates'] = json.loads(data['special_dates'])

        if data.get("travel_expenses"):
            data['travel_expenses'] = json.loads(data['travel_expenses'])

        return _schema.load(data), False

    except marshmallow.exceptions.ValidationError as resp:
        resp = resp.messages
        key = list(resp)[0]
        try:
            if type(resp[key][0]) is list:
                resp[key][0] = resp[key][0][0]

            if not bool(resp[key][0].find('Field')):
                return resp[key][0].replace('Field', key), True
            elif not bool(resp[key][0].find('field')):
                return resp[key][0].replace('field', key), True

            return key + ': ' + resp[key][0], True

        except KeyError:
            return check_validations_errors(resp, key)

        except AttributeError:
            return check_validations_errors(resp, key)


def remove_in_indexed_list_by_event_date(obj, event_dt):
    event_dt = datetime.fromtimestamp(calendar.timegm(event_dt.timetuple()))
    event_dt = event_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    list_of_dt = list(obj["special_dates"])
    ifBreak = False
    for _dt in list_of_dt:
        if bool(_dt.find('-')):
            str_start, str_end = _dt.split("-")
            dt_start = datetime.strptime(str_start, '%m/%d/%Y')
            dt_end = datetime.strptime(str_end, '%m/%d/%Y')
            if dt_start <= event_dt <= dt_end and obj["special_dates"][_dt]["hidden"]:
                ifBreak = True
                break
            continue

        dt_start = datetime.strptime(_dt, '%m/%d/%Y')
        if dt_start == event_dt and obj["special_dates"][_dt]["hidden"]:
            ifBreak = True
            break

    return ifBreak
