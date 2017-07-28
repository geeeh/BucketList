import unittest

from flask import json

from bucketlist import app, create_app
from bucketlist.extensions import db
from bucketlist.tests.base import Initializer


class RegisterTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.initializer = Initializer()

        self.same_email = {
            "username": "different email",
            "email": "test@example.com",
            "password": "password"
        }

    def test_registration(self):
        """
        Test user successful registration.
        """
        result = self.initializer.register()
        self.assertEqual(result.status_code, 201)

    def test_already_registered_username(self):
        """
        Test that a user cannot be registered twice with the same email.
        """
        initial = self.initializer.register()
        self.assertEqual(initial.status_code, 201)
        result = self.initializer.register()
        self.assertEqual(result.status_code, 202)

    def test_already_registered_email(self):
        """
        Test that a user cannot be registered twice with the same username.
        """
        initial = self.initializer.register()
        self.assertEqual(initial.status_code, 201)
        result = self.initializer.get_app().test_client().post('/bucketlist/v1/auth/register',
                                                               data=json.dumps(self.same_email),
                                                               content_type='application/json')
        self.assertEqual(result.status_code, 202)
