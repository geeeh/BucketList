import unittest

from flask import json

from bucketlist.tests.base import Initializer


class RegisterTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        self.initializer = Initializer()

        self.wrong_login_details = {
            "username": "tester",
            "password": "passwords"
        }

    def test_login(self):
        """
        Test user successful login.
        """
        login = self.initializer.login()
        self.assertEqual(login.status_code, 200)

    def test_login_with_wrong_details(self):
        """
        Test user unsuccessful login.
        """
        register = self.initializer.register()
        self.assertEqual(register.status_code, 201)
        login = self.initializer.get_app().test_client().post('/bucketlist/v1/auth/login',
                                                              data=json.dumps(self.wrong_login_details),
                                                              content_type='application/json')
        self.assertEqual(login.status_code, 401)
