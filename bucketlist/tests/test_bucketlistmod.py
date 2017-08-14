import unittest

from flask import json

from bucketlist.tests.base import Initializer


class BucketlistTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.initializer = Initializer()

    def test_get_bucketlist(self):
        """
        Test user successful login.
        """
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().get('/bucketlists/1',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 200)

    def test_unauthorized_get_bucketlist(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().get('/bucketlists/1',
                                                                   headers=None)
        self.assertEqual(bucketlists.status_code, 401)

    def test_update_bucketlist(self):
        login = self.initializer.login()
        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }
        update_data = {
            "name": "bucket 2"
        }

        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().put('/bucketlists/1',
                                                                   headers=output, data=json.dumps(update_data),
                                                                   content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)

    def test_unauthorized_update(self):
        login = self.initializer.login()
        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }
        update_data = {
            "name": "bucket 2"
        }

        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().put('/bucketlists/1',
                                                                   data=json.dumps(update_data),
                                                                   content_type='application/json')
        self.assertEqual(bucketlists.status_code, 401)

    def test_delete_bucketlist(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }

        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().delete('/bucketlists/1',
                                                                      headers=output)
        self.assertEqual(bucketlists.status_code, 200)

    def test_unauthorized_delete(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1"
        }

        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().delete('/bucketlists/1')
        self.assertEqual(bucketlists.status_code, 401)
