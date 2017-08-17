from flask import json

from bucketlist.app import create_app
from bucketlist.extensions import db


class Initializer(object):

    def __init__(self):
        """Set up test variables."""
        self.app = create_app("testing")

        self.registration_details = {
            "username": "tester",
            "email": "test@example.com",
            "password": "Password12"
        }
        self.login_details = {
            "username": "tester",
            "password": "Password12"
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def get_app(self):
        return self.app

    def register(self):
        """
        register user
        """
        register = self.app.test_client().post(
            '/auth/register',
            data=json.dumps(
                self.registration_details),
            content_type='application/json')
        return register

    def login(self):
        """
        login user
        """
        self.register()
        login = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(
                self.login_details),
            content_type='application/json')
        return login
