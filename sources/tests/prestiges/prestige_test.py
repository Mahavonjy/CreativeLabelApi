#!/usr/bin/env python3
""" shebang """

import json
import os

from sources.tests.testParent.testParent import Test


class PrestigeTest(Test):

    def prestige_test_error(self, link, _id, error_message):
        """

        Args:
            link:
            _id:
            error_message:
        """

        response = self.app.post(link + str(_id), headers=self.headers, content_type='application/json')
        if response.status_code == 200:
            return

        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, error_message)

    def test_send_prestige_and_get(self):
        """ """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        # prestige for artist service
        link = 'api/prestige/basy/service/'
        self.prestige_test_error(link=link, _id=2, error_message="prestige type not found")
        link = 'api/prestige/basy_mena/service/'
        self.prestige_test_error(link=link, _id=2, error_message="service not found")
        link = 'api/prestige/basy_mena/service/'
        self.prestige_test_error(link=link, _id=1, error_message="service not found")

        # prestige for artist beat
        link = 'api/prestige/basy/beat/'
        self.prestige_test_error(link=link, _id=2, error_message="prestige type not found")
        link = 'api/prestige/basy_mena/beat/'
        self.prestige_test_error(link=link, _id=2, error_message="beat not found")
        link = 'api/prestige/basy_mena/beat/'
        self.prestige_test_error(link=link, _id=1, error_message="beat not found")

        # check user prestige send
        response = self.app.get('api/prestige/me', headers=self.headers, content_type='application/json')
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(json_returned['sends']), 2)

        # check artist prestige receipt
        data = {"email": self.email, "password": self.password}
        response = self.app.post('api/users/login', data=json.dumps(data), content_type='application/json')
        json_returned = json.loads(response.get_data(as_text=True))
        self.headers = {"Isl-Token": json_returned['token']}
        response = self.app.get('api/prestige/me', headers=self.headers, content_type='application/json')
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(json_returned['receipted']), 2)

