#!/usr/bin/env python3
""" shebang """

from sources.app import welcome
from sources.models import db
import unittest


class ParentTest(unittest.TestCase):

    _app = None

    def setUp(self):
        """ this method is run before each test """

        app = welcome("development_test")
        self.app = app.test_client()

        with app.app_context():
            db.init_app(app)
            db.drop_all()
            db.create_all()
        self._app = app

    def tearDown(self):
        """ delete all info in DB """

        pass


if __name__ == '__main__':
    unittest.main()
