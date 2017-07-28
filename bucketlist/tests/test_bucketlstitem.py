import unittest

from flask import json

from bucketlist.tests.base import Initializer


class BucketlistTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.initializer = Initializer()

    def test_post_item(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        buc_data={
            "name": "bucket 1"
        }
        input_data = {
            "name": "bucket 1 item",
            "done": True
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists',
                                                                    headers=output, data=json.dumps(buc_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 201)

        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists/1/items',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 201)
        bucketlists = self.initializer.get_app().test_client().get('/bucketlist/v1/bucketlists/1',
                                                                   headers=output)
        self.assertEqual(bucketlists.status_code, 200)

    def test_update_item(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1",
            "done": False
        }

        update_data = {
            "name": "bucket 1",
            "done": True
        }

        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists/1/items',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 201)
        bucketlists = self.initializer.get_app().test_client().put('/bucketlist/v1/bucketlists/1/items/1',
                                                                   headers=output, data=json.dumps(update_data),
                                                                   content_type='application/json')
        self.assertEqual(bucketlists.status_code, 204)

    def test_delete_item(self):
        login = self.initializer.login()

        self.assertEqual(login.status_code, 200)
        data = json.loads(login.data.decode())
        output = {
            "Token": data['auth_token'],
        }
        input_data = {
            "name": "bucket 1",
            "done": True
        }
        bucketlists = self.initializer.get_app().test_client().post('/bucketlist/v1/bucketlists/1/items',
                                                                    headers=output, data=json.dumps(input_data),
                                                                    content_type='application/json')
        self.assertEqual(bucketlists.status_code, 201)
        bucketlists = self.initializer.get_app().test_client().delete('/bucketlist/v1/bucketlists/1/items/1',
                                                                      headers=output)
        self.assertEqual(bucketlists.status_code, 204)