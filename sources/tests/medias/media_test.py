#!/usr/bin/env python3
""" shebang """

import os
import time

from preferences import BLUES_ALLOWED
from sources.tests.testParent.testParent import Test
from requests_toolbelt import MultipartEncoder
import json


class TestMedia(Test):
    headers = None
    mp3_file = None
    wave_file = None
    zip_file = None
    photo_file = None
    path = os.getcwd()
    directory = "/sources/tests/medias/media_file_test/"
    photo_name = "image_allowed_test.png"
    mp3_name = "media_allowed_test.mp3"
    wave_name = "media_wave_allowed_test.wav"
    zip_name = "zipfile_test.zip"
    beat = {
        "title": "beats_test",
        "artist": "artist_test",
        "description": "artist_test",
        "artist_tag": "artist_test",
        "bpm": b'0',
        "genre": "test_genre",
        "basic_price": b'12',
        "silver_price": b'13',
        "gold_price": b'13',
        "platinum_price": b'23'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add image for test
        directory_name = self.path + self.directory + self.photo_name
        self.photo_file = (os.path.basename(directory_name), open(directory_name, 'rb'), "image/png")
        # add audio mp3 for test
        directory_name = self.path + self.directory + self.mp3_name
        self.mp3_file = (os.path.basename(directory_name), open(directory_name, 'rb'), "audio/mp3")
        # add audio wave for test
        directory_name = self.path + self.directory + self.wave_name
        self.wave_file = (os.path.basename(directory_name), open(directory_name, 'rb'), "audio/wav")
        # add zipfle for test
        directory_name = self.path + self.directory + self.zip_name
        self.zip_file = (os.path.basename(directory_name), open(directory_name, 'rb'), "application/zip")

    def check_uploadBeat_error(self, error_message=None, status_code=400):
        data_form_type = MultipartEncoder(fields=self.beat)
        resp = self.app.post(
            'api/beats/uploadBeat',
            headers=self.headers,
            content_type=data_form_type.content_type,
            data=data_form_type
        )
        self.assertEqual(resp.status_code, status_code)
        json_returned = json.loads(resp.get_data(as_text=True))
        if status_code == 200:
            self.assertIn(self.mp3_name, json_returned['mp3'])
            self.assertIn(self.wave_name, json_returned['wave'])
            self.assertIn(self.zip_name, json_returned['stems'])
            return
        self.assertEqual(json_returned, error_message)

    def test_upload_beat(self):
        """ """

        self.headers = {"Isl-Token": self.check_beatMaker_token()}
        self.check_uploadBeat_error(error_message='genre not supported')
        self.beat['genre'] = BLUES_ALLOWED
        self.check_uploadBeat_error(error_message='photo required')

        self.beat.update({'photo': self.mp3_file})
        self.check_uploadBeat_error(error_message='photo type is not supported')

        self.beat.update({'photo': self.photo_file})
        self.check_uploadBeat_error(error_message='send me the beats song (.mp3) & (.wave) in field')

        self.beat.update({'beats_wave': self.mp3_file})
        self.check_uploadBeat_error(error_message='send me the beats song (.mp3) & (.wave) in field')

        self.beat.update({'file': self.wave_file})
        self.check_uploadBeat_error(error_message='stems required')

        self.beat.update({'stems': self.mp3_file})
        self.check_uploadBeat_error(error_message='mp3 file not allowed')

        self.beat.update({'file': self.mp3_file})
        self.check_uploadBeat_error(error_message='wave file not allowed')

        self.beat.update({'beats_wave': self.wave_file})
        self.check_uploadBeat_error(error_message='stems not supported')

        directory_png = self.path + self.directory + self.photo_name
        png = (os.path.basename(directory_png), open(directory_png, 'rb'), "image/png")
        directory_mp3 = self.path + self.directory + self.mp3_name
        mp3 = (os.path.basename(directory_mp3), open(directory_mp3, 'rb'), "audio/mp3")
        directory_wave = self.path + self.directory + self.wave_name
        wav = (os.path.basename(directory_wave), open(directory_wave, 'rb'), "audio/wav")
        directory_zip = self.path + self.directory + self.zip_name
        _zip = (os.path.basename(directory_zip), open(directory_zip, 'rb'), "application/zip")
        self.beat.update({'photo': png, 'file': mp3, 'beats_wave': wav, 'stems': _zip})
        self.check_uploadBeat_error(status_code=200)

    def create_beat_test(self):
        """ """

        self.headers = {"Isl-Token": self.check_beatMaker_token()}
        self.beat['genre'] = BLUES_ALLOWED
        self.beat.update({
            'photo': self.photo_file,
            'file': self.mp3_file,
            'beats_wave': self.wave_file,
            'stems': self.zip_file
        })
        data_form_type = MultipartEncoder(fields=self.beat)
        resp = self.app.post(
            'api/beats/uploadBeat',
            headers=self.headers,
            content_type=data_form_type.content_type,
            data=data_form_type
        )
        self.assertEqual(resp.status_code, 200)

    def test_update_beat(self):
        """ """

        self.create_beat_test()
        self.check_update_beat_errors(beat_id="20", error_message='beat not found or deleted')
        del self.beat['photo']
        del self.beat['file']
        del self.beat['beats_wave']
        del self.beat['stems']

        self.beat.update({'photo': self.mp3_file})
        self.check_update_beat_errors(error_message='photo type is not supported')

        del self.beat['photo']
        self.beat.update({'beats_wave': self.mp3_file})
        self.check_update_beat_errors(error_message='wave file not allowed')

        del self.beat['beats_wave']
        self.beat.update({'file': self.wave_file})
        self.check_update_beat_errors(error_message='mp3 file not allowed')

        del self.beat['file']
        self.beat.update({'stems': self.mp3_file})
        self.check_update_beat_errors(error_message='stems not supported')

        # success
        del self.beat['stems']
        self.beat.update({
            "title": "toto",
            "artist": "tata",
            "description": "titi",
            "artist_tag": "tete",
            "bpm": b'40',
            "genre": BLUES_ALLOWED,
            "basic_price": b'16',
            "silver_price": b'67',
            "gold_price": b'89',
            "platinum_price": b'90'
        })

        directory_png = self.path + self.directory + self.photo_name
        png = (os.path.basename(directory_png), open(directory_png, 'rb'), "image/png")
        directory_mp3 = self.path + self.directory + self.mp3_name
        mp3 = (os.path.basename(directory_mp3), open(directory_mp3, 'rb'), "audio/mp3")
        directory_wave = self.path + self.directory + self.wave_name
        wav = (os.path.basename(directory_wave), open(directory_wave, 'rb'), "audio/wav")
        directory_zip = self.path + self.directory + self.zip_name
        _zip = (os.path.basename(directory_zip), open(directory_zip, 'rb'), "application/zip")
        self.beat.update({'photo': png, 'file': mp3, 'beats_wave': wav, 'stems': _zip})
        json_returned = self.check_update_beat_errors(status_code=200)
        self.assertEqual(json_returned['bpm'], 40.0)
        self.assertEqual(json_returned['title'], self.beat['title'])
        self.assertEqual(json_returned['artist'], self.beat['artist'])
        self.assertEqual(json_returned['description'], self.beat['description'])
        self.assertEqual(json_returned['artist_tag'], self.beat['artist_tag'])
        self.assertEqual(json_returned['genre'], self.beat['genre'])
        self.assertEqual(json_returned['basic_price'], 16.0)
        self.assertEqual(json_returned['silver_price'], 67.0)
        self.assertEqual(json_returned['gold_price'], 89.0)
        self.assertEqual(json_returned['platinum_price'], 90.0)

    def test_delete_beat(self):
        """ """

        self.create_beat_test()
        resp = self.app.delete('api/beats/delete/20', headers=self.headers, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, "beat not found or deleted")

        resp = self.app.get('api/medias_search/beat/1', headers=self.headers, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.delete('api/beats/delete/1', headers=self.headers, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.delete('api/beats/delete/1', headers=self.headers, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, "beat not found or deleted")

    def check_update_beat_errors(self, beat_id="1", error_message=None, status_code=400):
        """ """

        data_form_type = MultipartEncoder(fields=self.beat)
        resp = self.app.put(
            'api/beats/updateBeat/' + beat_id,
            headers=self.headers,
            content_type=data_form_type.content_type,
            data=data_form_type
        )
        try:
            self.assertEqual(resp.status_code, status_code)
        except AssertionError:
            raise ValueError(json.loads(resp.get_data(as_text=True)))
        json_returned = json.loads(resp.get_data(as_text=True))
        if status_code == 200:
            return json_returned
        self.assertEqual(json_returned, error_message)
