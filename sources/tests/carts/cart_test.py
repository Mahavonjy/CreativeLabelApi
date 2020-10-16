#!/usr/bin/env python3
""" shebang """

import json
from sources.tests.testParent.testParent import Test


class CartTest(Test):

    def cart_test_error(self, link, data, error_message=""):
        """

        Args:
            data:
            link:
            error_message:
        """

        response = self.app.post(link, data=json.dumps(data), headers=self.headers, content_type='application/json')
        if response.status_code == 200:
            return

        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, error_message)

    def test_adding_cart(self):
        """ """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}
        data = {"beat_id": 15, "license": "basic_lease"}

        link = '/api/carts/addToCart'
        self.cart_test_error(link=link, data=data, error_message="beat not exist")
        data.update({"beat_id": 1, "license": "basic"})
        self.cart_test_error(link=link, data=data, error_message="invalid license")
        data.update({"license": "basic_lease"})
        self.cart_test_error(link=link, data=data)

        data = {"email": self.email, "password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        json_returned = json.loads(response.get_data(as_text=True))
        self.headers = {"Isl-Token": json_returned['token']}
        data = {"beat_id": 1, "license": "basic_lease"}
        self.cart_test_error(link=link, data=data, error_message="Unauthorized")

    def test_delete_cart(self):
        """ """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        link = '/api/carts/addToCart'
        data = {"beat_id": 1, "license": "basic_lease"}
        self.cart_test_error(link=link, data=data)
        link = '/api/carts/delete/'
        response = self.app.delete(link + str(2), headers=self.headers, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, "cart not existing")
        response = self.app.delete(link + str(1), headers=self.headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_my_cart(self):
        """ """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        link = '/api/carts/addToCart'
        data = {"beat_id": 1, "license": "basic_lease"}
        self.cart_test_error(link=link, data=data)
        link = '/api/carts/MyCart'
        response = self.app.get(link, headers=self.headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(json_returned), 1)
