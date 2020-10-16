#!/usr/bin/env python3
""" shebang """

import json
from sources.tests.testParent.testParent import Test


class AdmirationTest(Test):

    def admiration_test_error(self, link, _id=1, error_message=""):
        """ """

        response = self.app.post(link + str(_id),  headers=self.headers, content_type='application/json')
        if response.status_code == 200:
            return

        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, error_message)

    def admiration_delete_test_error(self, link, _id=1, error_message=""):
        """ """

        response = self.app.delete(link + str(_id),  headers=self.headers, content_type='application/json')
        if response.status_code == 200:
            return

        self.assertEqual(response.status_code, 400)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_returned, error_message)

    def test_admire_artist_and_beat(self):
        """  """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        # user admire test
        link = '/api/admiration/admire_user/'
        self.admiration_test_error(link=link, _id=2, error_message="Unauthorized")
        self.admiration_test_error(link=link, _id=3, error_message="User not found")
        self.admiration_test_error(link=link, _id=1, error_message="")
        self.admiration_test_error(link=link, _id=1, error_message="exist")

        # beat admire test
        link = 'api/beats/admire_beat/'
        self.admiration_test_error(link=link, _id=2, error_message="Beat not found")
        self.admiration_test_error(link=link, _id=1, error_message="")
        self.admiration_test_error(link=link, _id=1, error_message="exist")

    def test_delete_admire_artist_and_beat(self):
        """ """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        # user admire test
        link = '/api/admiration/admire_user/'
        self.admiration_test_error(link=link, _id=1, error_message="")
        link = 'api/admiration/delete_admire_user/'
        self.admiration_delete_test_error(link=link, _id=1, error_message="")
        self.admiration_delete_test_error(link=link, _id=1, error_message="Not found")

        # beat admire test
        link = 'api/beats/admire_beat/'
        self.admiration_test_error(link=link, _id=1, error_message="")
        link = 'api/beats/delete_admire_beat/'
        self.admiration_delete_test_error(link=link, _id=1, error_message="")
        self.admiration_delete_test_error(link=link, _id=1, error_message="Not found")

    def test_user_beat_admirers(self):
        """  """

        self.headers = {"Isl-Token": self.create_artist_beat_and_auditor_pro()}

        # user admire test
        link = '/api/admiration/admire_user/'
        self.admiration_test_error(link=link, _id=1, error_message="")
        response = self.app.get("api/admiration/my_admire", headers=self.headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(json_returned['all_admire']), 1)
        self.assertEqual(len(json_returned['my_admirers']), 0)

        # beat admire test
        link = 'api/beats/admire_beat/'
        self.admiration_test_error(link=link, _id=1, error_message="")
        response = self.app.get("api/beats/my_admire", headers=self.headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_returned = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(json_returned), 1)
