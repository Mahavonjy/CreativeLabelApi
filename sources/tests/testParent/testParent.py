#!/usr/bin/env python3
""" shebang """

import unittest

from preferences import ANIMATOR, USER_ARTIST_DJ
from sources.app import welcome
from sources.models import db


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
