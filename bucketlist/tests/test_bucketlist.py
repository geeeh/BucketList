import unittest

from flask import json

from bucketlist.tests.base import Initializer


class BucketlistTestCase(unittest.TestCase):

    def setUp(self):
        self.initializer = Initializer()

    def test_post_bucketlist_successfully(self):
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
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)

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
        bucketlists = self.initializer.get_app().test_client().get('/bucketlists/',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 200)

    def test_get_bucketlist_with_search(self):
        """
        Test user successful login.
        """
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token']
        }
        search_out = {
            "Token": data['auth_token'],
            "q": "buc"
        }
        get_data = {
            "name": "bucketlist 1"
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(get_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 200)
        bucketlists = self.initializer.get_app().test_client().get('/bucketlists/',
                                                                   headers=search_out)
        self.assertEqual(bucketlists.status_code, 200)

    def test_unauthorized_get_bucketlist(self):
        output = None
        bucketlists = self.initializer.get_app().test_client().get('/bucketlists/',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 401)

    def test_post_bucketlist_without_data(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        data_input = None
        output = {
            "Token": data['auth_token']
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    headers=output, data=json.dumps(data_input),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 400)

    def test_unauthorized_post_bucketlist(self):
        data_input = {
            "name": "bucketlist 1"
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlists/',
                                                                    data=json.dumps(data_input),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 401)

