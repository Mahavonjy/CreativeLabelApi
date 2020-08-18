#!/usr/bin/env python3
""" shebang """

from requests_toolbelt import MultipartEncoder

from sources.models.keyResetPassword.keyResetPasswords import KeyResetPassword
from sources.models.users.user import User
from sources.app import welcome
from sources.models import db
import unittest
import json


class Test(unittest.TestCase):

    def createTestAccount(self):
        name = "clientTest"
        email = "client.test@gmail.com"
        password = "qwerty"

        data_form_type = MultipartEncoder(fields={"name": name, "email": email, "password": password})
        response = self.app.post(
            'api/users/register', data=data_form_type, content_type=data_form_type.content_type
        )
        self.assertEqual(response.status_code, 200)

        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(email=email)
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)

        new_data = {"keys": keys_obj.keys, "email": email}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    # code that is executed before each test
    def setUp(self):
        app = welcome("development_test")
        self.app = app.test_client()

        with app.app_context():
            db.init_app(app)
            db.create_all()

        self._app = app

    # code that is executed after each test
    def tearDown(self):
        with self._app.app_context():
            db.drop_all()


if __name__ == '__main__':
    unittest.main()
