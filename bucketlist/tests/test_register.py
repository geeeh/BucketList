import unittest

from flask import json

from bucketlist.tests.base import Initializer


class RegisterTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.initializer = Initializer()

        self.same_email = {
            "username": "sameemail",
            "email": "test@example.com",
            "password": "Password12"
        }

        self.bad_mail = {
            "username": "same email",
            "email": "testexample",
            "password": "Password12"
        }

        self.weak_pass = {
            "username": "same email",
            "email": "test@example.com",
            "password": "pass"
        }

        self.invalid_username = {
            "username": 31411,
            "email": "test@example.com",
            "password": "Password12"
        }

    def test_registration(self):
        """
        Test user successful registration.
        """
        result = self.initializer.register()
        self.assertEqual(result.status_code, 201)

    def test_for_valid_username(self):
        result = self.initializer.get_app().test_client().post(
            '/auth/register',
            data=json.dumps(
                self.invalid_username),
            content_type='application/json')
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
        result = self.initializer.get_app().test_client().post('/auth/register',
                                                               data=json.dumps(self.same_email),
                                                               content_type='application/json')
        self.assertEqual(result.status_code, 202)

    def test_reg_pass_validation(self):
        """
        Test that a user cannot be registered with a weak password.
        """
        result = self.initializer.get_app().test_client().post('/auth/register',
                                                               data=json.dumps(self.weak_pass),
                                                               content_type='application/json')
        self.assertEqual(result.status_code, 200)

    def test_reg_email_validation(self):
        result = self.initializer.get_app().test_client().post('/auth/register',
                                                               data=json.dumps(self.bad_mail),
                                                               content_type='application/json')
        self.assertEqual(result.status_code, 200)
