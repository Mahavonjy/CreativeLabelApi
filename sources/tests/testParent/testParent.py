#!/usr/bin/env python3
""" shebang """
import os
import unittest

import cloudinary

from preferences import ANIMATOR, USER_ARTIST_DJ
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

    # code that is executed before each test
    def setUp(self):

        app = welcome("development_test")
        self.app = app.test_client()
        with app.app_context():
            # app.config.MAIL_USERNAME = os.getenv('MAIL_DEV_USERNAME_API')
            # app.config.MAIL_PASSWORD = os.getenv('MAIL_DEV_PASSWORD_API')
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
