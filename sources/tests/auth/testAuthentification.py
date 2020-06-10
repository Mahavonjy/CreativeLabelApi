#!/usr/bin/env python3
""" shebang """

from sources.tests.testParent.testParent import ParentTest
from sources.models.keyResetPassword.keyResetPasswords import KeyResetPassword
from sources.models.users.user import User
import json


class TestAuthentification(ParentTest):

    def test_register(self):
        """ Test my function register.
            Register function include too the function validation_keys(), token_return
            in Controller User.py
        """

        # Check if name is out of data and return error name
        data = {"email": "testing@gmail.com", "password": "qwerty"}
        response = self.app.post(
            'api/users/register', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['name'][0], 'Missing data for required field.')

        # Check if email is out of data and return error for email
        del data['email']
        data['name'] = 'testing'
        response = self.app.post(
            'api/users/register', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['email'][0], 'Missing data for required field.')

        # Check if password is out of data and return error for password
        del data['password']
        data['email'] = 'testing@gmail.com'
        response = self.app.post(
            'api/users/register', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['password'][0], 'Missing data for required field.')

        # Now i test register with success and return 200 in status
        data['password'] = "qwerty"
        response = self.app.post(
            'api/users/register', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned['token'])
        self.assertEqual(json_returned['name'], data["name"])
        self.assertEqual(json_returned['email'], data["email"])
        self.assertEqual(json_returned['photo'], None)

        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(json_returned['email'])
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)
            key = keys_obj.keys

        # If my key is not valid
        # Check if keys is out of data and return error for keys
        new_data = {"email": data["email"]}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['keys'][0], 'Missing data for required field.')

        # Check if email is out of data and return error for email
        new_data = {"keys": key}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['email'][0], 'Missing data for required field.')

        # Check if key no validate
        new_data = {"keys": 00000, "email": data["email"]}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned, "Keys invalid")

        # Check if key validate
        new_data['keys'] = key
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned, "validate")

        # Check if key already used
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned, "already used")

    def test_login(self):
        """ Test my function login.
        """


