#!/usr/bin/env python3
""" shebang """

import os
import unittest

import cloudinary

from preferences import ANIMATOR, BLUES_ALLOWED, USER_ARTIST_DJ
from sources.app import welcome
from sources.models import db

from requests_toolbelt import MultipartEncoder
import json
from preferences import AFROBEAT_ALLOWED, USER_ARTIST_BEATMAKER
from sources.models.keyResetPassword.keyResetPasswords import KeyResetPassword
from sources.models.users.user import User


class Test(unittest.TestCase):

    _app = None
    basic_env = None
    name = "clientTest"
    email = "client.test@gmail.com"
    password = "qwerty"
    service_title = "test"
    service_price = 2.2
    service_hidden = False
    user_type = USER_ARTIST_DJ
    service_refund_policy = "flexible"
    service_country = "Madagascar"
    service_thematics = [ANIMATOR]
    service_description = "test description"
    service_reference_city = "test"
    service_travel_expenses = {"from": 0, "to": 0}
    service_number_of_artists = 2
    service_preparation_time = 3.1
    service_duration_of_the_service = 3.1
    service_events = ["Mariage", "Anniversaire"]
    service_special_dates = {}
    service_galleries = ["fo", "li"]
    service_others_city = ["fo", "li"]
    service_unit_of_the_preparation_time = "min"
    service_unit_duration_of_the_service = "sec"
    service_test = {
        "title": service_title,
        "price": service_price,
        "hidden": service_hidden,
        "refund_policy": service_refund_policy,
        "country": service_country,
        "thematics": service_thematics,
        "description": service_description,
        "reference_city": service_reference_city,
        "travel_expenses": service_travel_expenses,
        "number_of_artists": service_number_of_artists,
        "preparation_time": service_preparation_time,
        "events": service_events,
        "galleries": service_galleries,
        "others_city": service_others_city,
        "duration_of_the_service": service_duration_of_the_service,
        "special_dates": service_special_dates,
        "unit_duration_of_the_service": service_unit_duration_of_the_service,
        "unit_of_the_preparation_time": service_unit_of_the_preparation_time,
    }

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

    def create_artist_beat_and_auditor_pro(self):
        """ """

        email = "auditor@gmail.com"
        directory_png = self.path + self.directory + self.photo_name
        photo = (os.path.basename(directory_png), open(directory_png, 'rb'), "image/png")
        directory_mp3 = self.path + self.directory + self.mp3_name
        mp3 = (os.path.basename(directory_mp3), open(directory_mp3, 'rb'), "audio/mp3")
        directory_wave = self.path + self.directory + self.wave_name
        beats_wave = (os.path.basename(directory_wave), open(directory_wave, 'rb'), "audio/wav")
        directory_zip = self.path + self.directory + self.zip_name
        stems = (os.path.basename(directory_zip), open(directory_zip, 'rb'), "application/zip")
        self.beat.update({'photo': photo, 'file': mp3, 'beats_wave': beats_wave, 'stems': stems})
        self.create_beat_test(update_beat=False)
        self.createTestAccount(email=email)
        data = {"email": email, "password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        return json_returned['token']

    def createTestAccount(self, email=None):
        """ """

        data_form_type = MultipartEncoder(fields={
            "name": self.name,
            "email": email or self.email,
            "password": self.password
        })
        response = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(response.status_code, 200)

        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(email=email or self.email)
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)

        new_data = {"keys": keys_obj.keys, "email": email or self.email}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def check_beatMaker_token(self):
        """ """

        self.service_test['thematics'] = [AFROBEAT_ALLOWED]
        data = {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "user_type": USER_ARTIST_BEATMAKER,
            "services": json.dumps(self.service_test),
        }
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        token = json.loads(resp.get_data(as_text=True))['token']
        self.assertEqual(resp.status_code, 200)
        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(self.email)
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)
        new_data = {'email': self.email, 'keys': keys_obj.keys}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        return token

    def create_beat_test(self, update_beat=True):
        """ """

        self.headers = {"Isl-Token": self.check_beatMaker_token()}
        self.beat['genre'] = BLUES_ALLOWED
        if update_beat:
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

    # code that is executed before each test
    def setUp(self):

        app = welcome("development_test")
        self.app = app.test_client()
        with app.app_context():
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET")
            )
            db.drop_all()
            db.init_app(app)
            db.create_all()

        self._app = app

    # code that is executed after each test
    def tearDown(self):

        with self._app.app_context():
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
