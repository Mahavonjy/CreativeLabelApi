#!/usr/bin/env python3
""" shebang """

import json

from preferences.defaultData import beats_pricing
from sources.tests.testParent.testParent import Test


class ContractBeats(Test):

    def test_get_my_contract_beat(self):
        """ check contract beat """

        self.headers = {"Isl-Token": self.check_beatMaker_token()}
        resp = self.app.get(
            'api/beats/contract/user_artist_contract',
            headers=self.headers,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned['silver_lease']['price'], beats_pricing['silver'])
        self.assertEqual(json_returned['gold_lease']['price'], beats_pricing['gold'])
        self.assertEqual(json_returned['platinum_lease']['price'], beats_pricing['platinum'])
        self.assertEqual(json_returned['basic_lease']['price'], beats_pricing['basic'])

    def test_update_my_contract_beat(self):
        """ """

        self.headers = {"Isl-Token": self.check_beatMaker_token()}
        resp = self.app.get(
            'api/beats/contract/user_artist_contract',
            headers=self.headers,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        data = {
            "mp3": True,
            'wave': False,
            'stems': False,
            'unlimited': False,
            'enabled': True,
            "contract_name": "basic_lease",
            "price": 12.0,
            "number_audio_stream": 10000,
            "number_of_distribution_copies": 10000,
            "number_music_video": 10000,
            "number_radio_station": 10000,
            "user_id": 1
        }
        resp = self.app.put(
            'api/beats/contract/update_basic',
            headers=self.headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        data.update({
            "wave": True,
            "contract_name": "silver_lease",
            "price": 30.0,
            "number_of_distribution_copies": 10000,
            "number_audio_stream": 100000,
            "number_music_video": 30000,
            "number_radio_station": 40000,
        })
        resp = self.app.put(
            'api/beats/contract/update_silver',
            headers=self.headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        data.update({
            "stems": True,
            "contract_name": "gold_lease",
            "price": 40.0,
            "number_of_distribution_copies": 20000,
            "number_audio_stream": 200000,
            "number_music_video": 20000,
            "number_radio_station": 999999
        })
        resp = self.app.put(
            'api/beats/contract/update_gold',
            headers=self.headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        data.update({
            "contract_name": "platinum_lease",
            "price": 100.00,
            'enabled': False,
            "number_of_distribution_copies": 999999,
            "number_audio_stream": 999999,
            "number_music_video": 999999,
            "number_radio_station": 999999,
            "unlimited": True
        })
        resp = self.app.put(
            'api/beats/contract/update_platinum',
            headers=self.headers,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(
            'api/beats/contract/user_artist_contract',
            headers=self.headers,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        json_returned = json.loads(resp.get_data(as_text=True))
        self.assertEqual(json_returned['platinum_lease']['price'], 100.00)
        self.assertEqual(json_returned['gold_lease']['price'], 40.0)
        self.assertEqual(json_returned['silver_lease']['price'], 30.0)
        self.assertEqual(json_returned['basic_lease']['price'], 12.0)
