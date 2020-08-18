#!/usr/bin/env python3
""" shebang """

import os
import re
import time
import json
import librosa
import calendar
import itertools
import marshmallow
from datetime import datetime

from sources.controllers import random_string
from sources.models.admirations.admirations import AdmireSchema
from sources.models.artists.materials.artistMaterials import MaterialsSchema
from sources.models.artists.options.artistOptions import OptionsSchema
from sources.models.artists.services.artistServices import ServiceSchema
from sources.models.medias.albums import Albums, AlbumSchema
from sources.models.medias.media import Media, MediaSchema
from sources.models.users.user import User
from sqlalchemy import desc

albumSchema = AlbumSchema()
media_schema = MediaSchema()
material_schema = MaterialsSchema()
service_schema = ServiceSchema()
option_schema = OptionsSchema()
admire_schema = AdmireSchema()


def merge_suggestion(new_list):
    """

    :param new_list:
    :return: dict merged with suggestion album for the user
    """
    return [dict(t) for t in {tuple(d.items()) for d in new_list}]


def by_user_genre_list(genre_list, type_):
    """

    :param genre_list:
    :param type_:
    :return: album tried by user admiration
    """
    schema = albumSchema if type_ == "album" else media_schema
    query_ = Albums.get_album_genre if type_ == "album" else Media.get_song_by_genre
    user_list_genre, albs_in_dict = genre_list, []
    try:
        all_ = [query_(genre) for genre in user_list_genre]
    except TypeError:
        all_ = [query_(type_, genre) for genre in user_list_genre]

    for index in all_:
        if len(index) == 1:
            albs_in_dict.append(schema.dump(index[0]))
            continue
        for alb in index:
            albs_in_dict.append(schema.dump(alb))

    return albs_in_dict


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


def by_all_user_admire(user_id, type_):
    """

    :param user_id:
    :param type_:
    :return: return the album tried
    """
    schema, result = albumSchema if type_ == "album" else media_schema, []
    data_classed, all_user_admire = [], User.get_one_user(user_id).user.all()
    for a_u in all_user_admire:
        if type_ == "album" and admire_schema.dump(a_u)['admire_id']:
            result = User.get_one_user(admire_schema.dump(a_u)['admire_id']) \
                .albums.order_by(desc(Albums.created_at)).limit(1).all()
        elif type_ == "medias" and admire_schema.dump(a_u)['admire_id']:
            result = User.get_one_user(admire_schema.dump(a_u)['admire_id']) \
                .medias.filter_by(album_song=False, genre_musical="music") \
                .order_by(desc(Media.created_at)).limit(1).all()
        data_classed += [schema.dump(row) for row in result]
    return data_classed


def librosa_collect(file):
    """

    :param file:
    :return: dict of time and bpm
    """

    dirname = random_string()
    file.save(dirname)
    y, sr = librosa.load(dirname)
    bpm, beats_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats_times = librosa.frames_to_time(beats_frames, sr=sr)
    time_ = time.strftime('%H:%M:%S', time.gmtime(int(round(beats_times[-1]))))
    try:
        tm = time_[3:] if time_.split(":")[0] == "00" else time_
    except TypeError:
        tm = None
    os.remove(dirname)
    return bpm, tm


def check_validations_errors(resp, key):
    new_resp = resp[key]
    new_key = list(new_resp)[0]
    tmp = new_resp[new_key][0].replace('Field', key)
    if not bool(new_resp[new_key][0].find('Field')):
        tmp = tmp.replace('Field', key)
        return tmp.replace('data', new_key), True
    tmp = tmp.replace('data', new_key) if not bool(tmp.find('data')) else new_key + " " + tmp
    return tmp.replace('field', key), True


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
            data['services'] = json.loads(data['services'])
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
