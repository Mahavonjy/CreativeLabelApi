#!/usr/bin/env python3
""" shebang """

from preferences import USER_ARTIST_BEATMAKER
from sources.models.artists.beatMakers.contractBeatmaking.contractBeatmaking import ContractBeatMaking
from sources.models.artists.conditions.globals import ConditionGlobals
from sources.tests.testParent.testParent import Test
from requests_toolbelt import MultipartEncoder
from sources.models.keyResetPassword.keyResetPasswords import KeyResetPassword
from sources.models.users.user import User
from auth.authentification import Auth
import json


class TestAuthentification(Test):

    def get_user_data_by_token(self, token):
        data = Auth.decode_token(token)
        self.assertEqual(type(data), dict)
        with self._app.app_context():
            user = User.get_one_user(data['data']["user_id"])
        return user

    def check_keys_validate(self):

        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(self.email)
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)

        # If my key is not valid
        # Check if keys is out of data and return error for keys
        new_data = {"email": self.email}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'keys: Missing data for required field.')

        # Check if email is out of data and return error for email
        new_data = {"keys": keys_obj.keys}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'email: Missing data for required field.')

        # Check if key no validate
        new_data = {"keys": 00000, "email": self.email}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned, "Keys invalid")

        # Check if key validate
        new_data['keys'] = keys_obj.keys
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

    def check_service_errors(self, key, key_true_value, key_false_value, data, error_message):

        self.service_test[key] = key_false_value
        data["services"] = json.dumps(self.service_test)
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json_returned, error_message)
        self.service_test[key] = key_true_value

    def createTestAccount(self):
        data_form_type = MultipartEncoder(fields={"name": self.name, "email": self.email, "password": self.password})
        response = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(response.status_code, 200)

        # Check my key in data
        with self._app.app_context():
            user = User.get_user_by_email(email=self.email)
            self.assertTrue(user)
            keys_obj = KeyResetPassword.get_by_user_id(user.id)
            self.assertTrue(keys_obj)

        new_data = {"keys": keys_obj.keys, "email": self.email}
        response = self.app.post(
            'api/users/get_if_keys_validate', data=json.dumps(new_data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_change_user_type_auditor_to_artist(self):

        data = {"name": self.name, "email": self.email, "password": self.password}
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(resp.status_code, 200)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertTrue(json_returned['token'])
        self.assertEqual(json_returned['name'], self.name)
        self.assertEqual(json_returned['email'], self.email)
        self.assertEqual(json_returned['photo'], None)
        self.check_keys_validate()

        # check user_type not allowed
        resp = self.app.put('api/users/update_user_to/' + "qwerty", content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, "Authentication token is not available, please login to get one")

        del data["name"]
        resp = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        json_returned = json.loads(resp.get_data(as_text=True))
        token = json_returned['token']
        headers = {'content_type': 'application/json', 'Isl-Token': token}
        resp = self.app.put('api/users/update_user_to/' + "qwerty", headers=headers)
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, "artist type not Allowed")

        resp = self.app.put('api/users/update_user_to/' + USER_ARTIST_BEATMAKER, headers=headers)
        self.assertEqual(resp.status_code, 200)

        # check if user type is updated
        user = self.get_user_data_by_token(token)
        self.assertEqual(user.user_type, USER_ARTIST_BEATMAKER)

        with self._app.app_context():
            # check default contract
            self.assertIsNotNone(ContractBeatMaking.get_contract_name_by_user_id(user_id=user.id))
            # check condition globals
            self.assertIsNotNone(ConditionGlobals.get_condition_globals_by_user_id(user_id=user.id))

    def test_artist_register(self):
        """ Test my function register.
            Register function include too the function validation_keys(), token_return
            in Controller User.py
        """

        # Check if user_type is out of data and return error name
        data = {"name": self.name, "email": self.email, "password": self.password}
        data["services"] = json.dumps(self.service_test)
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, 'I need user_type')

        # artist type not allowed
        data["user_type"] = "user_type_not_allowed"
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(resp.status_code, 400)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned, 'user_type: artist type not allowed')
        data["user_type"] = self.user_type

        # Check if country is out of data and return error name
        self.check_service_errors(
            key="country",
            key_false_value="Manakara",
            key_true_value=self.service_country,
            data=data,
            error_message='country not allowed'
        )

        # check thematics error
        self.check_service_errors(
            key="thematics",
            key_false_value=["boboThematics"],
            key_true_value=self.service_thematics,
            data=data,
            error_message="dj type don't match with thematics"
        )

        # check events errors
        self.check_service_errors(
            key="events",
            key_false_value=["boboEvents"],
            key_true_value=self.service_events,
            data=data,
            error_message="events event boboEvents not allowed"
        )

        # check unit_of_the_preparation_time errors
        self.check_service_errors(
            key="unit_of_the_preparation_time",
            key_false_value="qwerty",
            key_true_value=self.service_unit_of_the_preparation_time,
            data=data,
            error_message="unit_of_the_preparation_time not allowed"
        )

        # check unit_duration_of_the_service errors
        self.check_service_errors(
            key="unit_duration_of_the_service",
            key_false_value="qwerty",
            key_true_value=self.service_unit_duration_of_the_service,
            data=data,
            error_message="unit_duration_of_the_service not allowed"
        )

        field_required = [
            ["events", self.service_events],
            ["title", self.service_title],
            ["thematics", self.service_thematics],
            ["price", self.service_price],
            ["country", self.service_country],
            ["reference_city", self.service_reference_city],
            ["refund_policy", self.service_refund_policy],
            ["number_of_artists", self.service_number_of_artists],
            ["unit_duration_of_the_service", self.service_unit_duration_of_the_service],
            ["unit_of_the_preparation_time", self.service_unit_of_the_preparation_time],
        ]

        for field in field_required:
            del self.service_test[field[0]]
            data["services"] = json.dumps(self.service_test)
            data_form_type = MultipartEncoder(fields=data)
            resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
            self.assertEqual(resp.status_code, 400)
            json_returned = json.loads(resp.get_data(as_text=True))
            self.assertEqual(json_returned, field[0] + ' Missing data for required services.')
            self.service_test[field[0]] = field[1]

        # Now we test register with success and return 200 in status
        data["services"] = json.dumps(self.service_test)
        data_form_type = MultipartEncoder(fields=data)
        resp = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(resp.status_code, 200)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertTrue(json_returned['token'])
        self.assertEqual(json_returned['name'], self.name)
        self.assertEqual(json_returned['email'], self.email)
        self.assertEqual(json_returned['photo'], None)
        self.check_keys_validate()

    def test_auditor_pro_register(self):
        """ Test my function register.
            Register function include too the function validation_keys(), token_return
            in Controller User.py
        """

        # Check if name is out of data and return error name
        data = {"email": self.email, "password": self.password}
        data_form_type = MultipartEncoder(fields=data)
        response = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'name: Missing data for required field.')

        # Check if email is out of data and return error for email
        del data['email']
        data['name'] = self.name
        data_form_type = MultipartEncoder(fields=data)
        response = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'email: Missing data for required field.')

        # Check if password is out of data and return error for password
        del data['password']
        data['email'] = self.email
        data_form_type = MultipartEncoder(fields=data)
        response = self.app.post(
            'api/users/register', data=data_form_type, content_type=data_form_type.content_type
        )
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'password: Missing data for required field.')

        # Now we test register with success and return 200 in status
        data['password'] = self.password
        data_form_type = MultipartEncoder(fields=data)
        response = self.app.post('api/users/register', data=data_form_type, content_type=data_form_type.content_type)
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_returned['token'])
        self.assertEqual(json_returned['name'], self.name)
        self.assertEqual(json_returned['email'], self.email)
        self.assertEqual(json_returned['photo'], None)
        self.check_keys_validate()

    def test_login(self):
        """ Test my function login."""

        self.createTestAccount()

        # Check if password is out of data and return error for password
        data = {"email": self.email}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'password: Missing data for required field.')

        # Check if email is out of data and return error for password
        data = {"password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'email: Missing data for required field.')

        # Check if email not found
        data = {"email": "emailnotfound@gmail.com", "password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'invalid email')

        # Check if password not match
        data = {"email": self.email, "password": "wrong_password"}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'invalid password')

        # Check login success
        data = {"email": self.email, "password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned['name'], self.name)
        self.assertEqual(json_returned['email'], self.email)
        self.assertTrue(json_returned['token'])

    def test_logout(self):
        """ Check logout if ok """

        self.createTestAccount()

        # log user
        data = {"email": self.email, "password": self.password}
        response = self.app.post(
            'api/users/login', data=json.dumps(data), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        _token = json.loads(response.get_data(as_text=True))['token']
        response = self.app.delete(
            'api/users/logout', content_type='application/json'
        )
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_returned, 'Authentication token is not available, please login to get one')

        # logout
        response = self.app.delete(
            'api/users/logout', headers={'content_type': 'application/json', 'Isl-Token': _token}
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.delete(
            'api/users/logout', headers={'content_type': 'application/json', 'Isl-Token': _token}
        )
        self.assertEqual(response.status_code, 400)

    def test_reset_password(self):
        """ Check user change password """

        self.createTestAccount()

        # check if email exist
        data = {"email": "emailnotexist@gmail.com"}
        response = self.app.post('api/users/get_mail', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'Email not Found')
        data = {"email": self.email}
        response = self.app.post('api/users/get_mail', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check my key in data
        self.check_keys_validate()

        # Check if password is out of data and return error for password
        data = {"email": self.email}
        response = self.app.put('api/users/reset_password', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'password: Missing data for required field.')

        # Check if email is out of data and return error for email
        data = {"password": self.password}
        response = self.app.put('api/users/reset_password', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'email: Missing data for required field.')

        # change user password
        data = {"password": self.password, "email": self.email}
        response = self.app.put('api/users/reset_password', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, 'password changed')
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
