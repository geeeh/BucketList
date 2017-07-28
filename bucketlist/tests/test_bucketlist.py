import unittest

from flask import json, jsonify

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
            "Token": data['auth_token']
        }
        bucketlists = self.initializer.get_app().test_client().get('/bucketlist/v1/bucketlists',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 204)

    def test_get_bucketlist_with_search(self):
        """
        Test user successful login.
        """
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
            "q": "bucketlist1"
        }
        bucketlists = self.initializer.get_app().test_client().get('/bucketlist/v1/bucketlists',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 204)

    def test_unauthorized_get_bucketlist(self):
        output = None
        bucketlists = self.initializer.get_app().test_client().get('/bucketlist/v1/bucketlists',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 401)

    def test_post_bucketlist(self):
        """
        Test user successful login.
        """
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        input_data = {
            "name": "bucket 1",
        }
        output = {
            "Token": data['auth_token'],
            "q": "bucketlist1"
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 201)

    def test_post_bucketlist_without_data(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        data_input = None
        output = {
            "Token": data['auth_token']
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists',
                                                                    headers=output, data=json.dumps(data_input),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 400)

    def test_unauthorized_post_bucketlist(self):
        data_input = None
        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists',
                                                                    data=json.dumps(data_input),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 401)

