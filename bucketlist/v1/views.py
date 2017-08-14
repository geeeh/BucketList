import re

from flask import request, make_response, jsonify, Blueprint
from flask_restplus import Resource, Api, fields, reqparse
from validate_email import validate_email

from bucketlist.Exceptions.invalid_query import InvalidQuery
from bucketlist.models.models import User, Bucketlist, Bucketlistitem

v1 = Blueprint('v1', __name__)

authorizations = {
    'Bearer': {
        'type': 'apikey',
        'in': 'header',
        'name': 'Token'
    }
}

api = Api(v1, version='1.0', title='Bucket list Application', authorization=authorizations, security='Bearer',
          description='A bucketlist api')

register_expect_fields = api.model('Registration', {
    'username': fields.String(required=True, description='user username'),
    'email': fields.String(required=True, description='user email address'),
    'password': fields.String(required=True, description='user password'),
})

ns = api.namespace('/', description='Operations related to a bucket list')


@ns.route('/auth/register')
class Register(Resource):

    @api.expect(register_expect_fields)
    def post(self):
        """register a user"""
        try:
            username = str(request.json.get("username"))
            email = request.json.get("email")
            password = request.json.get("password")

            if not (str.isalpha(username) or str.isalnum(username)):
                return "username should be a string!", 200
        except AttributeError:
            return "Attributes not found!"

        is_valid = validate_email(email) and self.validate_password(password)
        if is_valid:
            user = User.create_user(username, email, password )
            if isinstance(user, User):
                result = {
                    'message': "user registered successfully",
                    'user': {
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }
                return make_response(jsonify(result), 201)
            else:
                return user
        else:
            return "use strong passwords and correct email format", 200

    @staticmethod
    def validate_password(password):
            while True:
                if len(password) < 8:
                    return False
                elif re.search('[0-9]', password) is None:
                    return False
                elif re.search('[A-Z]', password) is None:
                    return False
                else:
                    return True



login_expect_fields = api.model('Login', {
    'username': fields.String(required=True, description='user username'),
    'password': fields.String(required=True, description='user password'),
})


@ns.route('/auth/login')
class Login(Resource):
    """
    allow registered users to login
    """
    @api.expect(login_expect_fields)
    def post(self):
        """
        login a user

        """
        try:
            user = User.query.filter_by(username=request.json.get('username')).first()

            # Try to authenticate the found user using their password
            if user and user.check_password(request.json.get('password')):
                # Generate the access token. This will be used as the authorization header
                access_token = user.encode_auth_token(user.id)
                if access_token:
                    result = {
                        "username": user.username,
                        "email": user.email,
                        "auth_token": access_token.decode()
                    }
                    return make_response(jsonify(result), 200)
            else:
                result = {
                    'message': "Invalid email or password, Please try again",
                }
                return make_response(jsonify(result), 401)

        except InvalidQuery:
            result = {
                'message': "Query error!",
            }
            return make_response(jsonify(result), 500)


pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', location="args", type=int, required=False, default=1)
pagination_arguments.add_argument('limit', location="args", type=int, required=False, default=20)
pagination_arguments.add_argument('q', location="args", required=False)

bucketlist_expect = api.model('Bucketlist_expect', {
        'name': fields.String(description='Bucketlist name', required=True),

    })


@ns.route('/bucketlists/')
@api.doc(params={})
class Bucketlists(Resource):
    """
    Shows a list of all bucketlists, and lets you POST to add new bucketlists
    """

    @api.header('Token', required=True)
    @api.expect(pagination_arguments)
    def get(self):

        """
        List all bucket list
        """

        args = pagination_arguments.parse_args()
        page = args['page']
        limit = args['limit']
        search_words = args['q']

        if limit > 100:
            limit = 100

        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        else:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):
                if search_words:
                    bucketlists_page = Bucketlist.query.filter(
                        Bucketlist.created_by == user_id,
                        Bucketlist.name.contains(search_words + "%")).paginate(page, limit, False)
                    if bucketlists_page:
                        total = bucketlists_page.pages
                        has_next = bucketlists_page.has_next
                        has_previous = bucketlists_page.has_prev

                        if has_next:
                            next_page = str(request.url_root) + 'bucketlists?' + \
                                        'q=' + str(search_words) + '&page=' + str(page + 1)
                        else:
                            next_page = 'None'
                        if has_previous:
                            previous_page = request.url_root + 'bucketlists?' + \
                                            'q=' + str(search_words) + '&page=' + str(page - 1)
                        else:
                            previous_page = 'None'
                        bucketlists = bucketlists_page.items
                        if bucketlists:
                            items = []
                            for item in bucketlists:
                                buc_items = []
                                bucketlist_items = Bucketlistitem.query.filter_by(bucketlist_id=item.id).all()
                                for any_item in bucketlist_items:
                                    an_item = {
                                        'id': any_item.id,
                                        'name': any_item.name,
                                        'done': any_item.done,
                                        'date_created': any_item.date_created,
                                        'date_modified': any_item.date_modified
                                    }
                                    buc_items.append(an_item)
                                a_bucket = {
                                    'id': item.id,
                                    'name': item.name,
                                    'items': buc_items,
                                    'created_by': item.created_by,
                                    'date_created': item.date_created,
                                    'date_modified': item.date_modified
                                }
                                items.append(a_bucket)

                            result = {'bucketlists': items,
                                      'has_next': has_next,
                                      'pages': total,
                                      'previous_page': previous_page,
                                      'next_page': next_page
                                      }
                            return make_response(jsonify(result), 200)
                        else:
                            result = {
                                "message": "No bucketlist item  found"
                            }
                            return make_response(jsonify(result), 200)

                bucketlists_page = Bucketlist.query.filter_by(created_by=user_id).paginate(page=page,
                                                                                           per_page=limit,
                                                                                           error_out=False)
                if not bucketlists_page:
                    result = {
                        "message": "No bucketlist item  found"
                    }
                    return make_response(jsonify(result), 204)

                total = bucketlists_page.pages
                has_next = bucketlists_page.has_next
                has_previous = bucketlists_page.has_prev

                if has_next:
                    next_page = str(request.url_root) + 'bucketlists?' + \
                                'limit=' + str(limit) + '&page=' + str(page + 1)
                else:
                    next_page = 'None'
                if has_previous:
                    previous_page = request.url_root + 'bucketlists?' + \
                                    'limit=' + str(limit) + '&page=' + str(page - 1)
                else:
                    previous_page = 'None'

                bucketlists = bucketlists_page.items
                items = []
                if bucketlists:
                    for item in bucketlists:
                        buc_items = []
                        bucketlist_items = Bucketlistitem.query.filter_by(bucketlist_id=item.id).all()
                        for any_item in bucketlist_items:
                            an_item = {
                                'id': any_item.id,
                                'name': any_item.name,
                                'done': any_item.done,
                                'date_created': any_item.date_created,
                                'date_modified': any_item.date_modified
                            }
                            buc_items.append(an_item)
                        a_bucket = {
                            'id': item.id,
                            'name': item.name,
                            'items': buc_items,
                            'created_by': item.created_by,
                            'date_created': item.date_created,
                            'date_modified': item.date_modified
                        }
                        items.append(a_bucket)

                    result = {'bucketlists': items,
                              'has_next': has_next,
                              'pages': total,
                              'previous_page': previous_page,
                              'next_page': next_page
                              }
                    return make_response(jsonify(result), 200)
                else:
                    result = {
                        "message": "No bucketlist item  found"
                    }
                    return make_response(jsonify(result), 200)

            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.header('Token', required=True)
    @api.expect(bucketlist_expect)
    def post(self):
        """
               insert a bucket list
               """
        access_token = request.headers.get('Token')
        try:
            name = request.json.get('name')
            if not name:
                return "attribute name not found", 400

        except AttributeError:
            return "attribute name not found", 400

        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)
        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)

            if isinstance(user_id, int):
                output = Bucketlist.create_bucketlist(user_id, name)
                if isinstance(output, Bucketlist):
                    result = {
                        "message": "Bucketlist successfully created",
                        "item": {
                            "id": output.id,
                            "name": output.name,
                            "created_by": output.created_by,
                            "date_created": output.date_created
                        }
                    }
                    return make_response(jsonify(result), 200)
                else:
                    return output
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)


@ns.route('/bucketlists/<int:id>')
class BucketlistModification(Resource):
    @api.header('Token', required=True)
    def get(self, id):

        """
        List all tasks'
        """

        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        if access_token:

            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):

                bucket = Bucketlist.query.filter_by(id=id, created_by=user_id).first()

                if bucket:
                    bucket_list = []
                    items = Bucketlistitem.query.filter_by(bucketlist_id=id).all()
                    for item in items:
                        an_item = {
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "done": item.done,
                            "date_modified": item.date_modified
                        }
                        bucket_list.append(an_item)
                    result = {
                        "id": bucket.id,
                        "name": bucket.name,
                        "items": bucket_list,
                        "date_created": bucket.date_created,
                        "date_modified": bucket.date_modified,
                        "created_by": bucket.created_by
                    }

                    return make_response(jsonify(result), 200)
                else:
                    result = {
                        "message": "Bucketlist not found"
                    }
                    return make_response(jsonify(result), 404)
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.expect(bucketlist_expect)
    @api.header('Token', required=True)
    def put(self, id):

        """
        updates a bucket list given id and the data
        """
        try:
            name = request.json.get('name')
        except AttributeError:
            return "attribute name not found", 400
        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):
                output = Bucketlist.update_bucketlist(id, user_id, name)
                if isinstance(output, Bucketlist):
                    result = {
                        "message": "Bucketlist successfully updated",
                        "item": {
                            "id": output.id,
                            "name": output.name,
                            "created_by": output.created_by,
                            "date_created": output.date_created
                        }
                    }
                    return make_response(jsonify(result), 200)

                else:
                    return output

            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.header('Token', required=True)
    def delete(self, id):

        """"
        deletes a bucket list given its id
        """
        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):
                output = Bucketlist.delete_bucketlist(id)
                return output
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)


bucketlistitem_expect = api.model('Bucketlistitem_expect', {
    'name': fields.String(description='Bucketlist name', required=True),
    'done': fields.Boolean(description='bucket list name', required=True),
})


@ns.route('/bucketlists/<int:id>/items/')
@api.doc(params={})
class Bucketlistitems(Resource):
    """
    Shows a list of all bucketlists, and lets you POST to add new bucketlists
    """

    @api.header('Token', required=True)
    def get(self, id):
        """
            List all items of a given bucketlist
        """
        bucket = Bucketlist.query.filter_by(id=id).first()
        if not bucket:
            return "Bucketlist not found!", 404
        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        if access_token:

            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):

                items = Bucketlistitem.query.filter_by(bucketlist_id=id).all()

                if items:
                    bucket_item_list = []
                    for item in items:
                        result = {
                            "id": item.id,
                            "name": item.name,
                            "done": item.done,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified

                        }
                        bucket_item_list.append(result)

                    return make_response(jsonify(bucket_item_list), 200)
                else:
                    result = {
                        "message": "No items found"
                    }
                    return make_response(jsonify(result), 200)
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.header('Token', required=True)
    @api.expect(bucketlistitem_expect)
    def post(self, id):
        """
        creates a bucketlist item
        """
        access_token = request.headers.get('Token')

        bucket = Bucketlist.query.filter_by(id=id).first()
        if not bucket:
            return "Bucketlist not found!", 404

        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)
        try:
            name = request.json.get('name')
            if not name:
                return "name attribute not found!", 400
            done = request.json.get('done')
            if done == None:
                return "done attribute not found!", 400
        except AttributeError:
            return "attributes not found!", 400

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            if isinstance(user_id, int):
                output = Bucketlistitem.create_bucketlistitem(id, name, done)
                if isinstance(output, Bucketlistitem):
                    result = {
                        "message": "Bucketlistitem successfully created",
                        "item": {
                            "id": output.id,
                            "name": output.name,
                            "done": output.done,
                            "date_created": output.date_created
                        }
                    }
                    return make_response(jsonify(result), 200)
                else:
                    return output
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)


@ns.route('/bucketlists/<int:id>/items/<int:item_id>')
@api.doc(params={})
class BucketlistitemModification(Resource):
    @api.header('Token', required=True)
    @api.expect(bucketlistitem_expect)
    def put(self, id, item_id):

        """
        updates a bucket list given id and the data
        """
        access_token = request.headers.get('Token')
        try:
            name = request.json.get('name')
            done = request.json.get('done')
        except AttributeError:
            return "attributes not found!"

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            buckets = Bucketlist.query.filter_by(id=id).first()
            if isinstance(user_id, int):
                if buckets:
                    output = Bucketlistitem.update_bucketlistitem(item_id, id,  name, done)
                    if isinstance(output, Bucketlistitem):
                        result = {
                            "message": "Bucketlistitem successfully updated",
                            "item": {
                                "id": output.id,
                                "name": output.name,
                                "done": output.done,
                                "date_created": output.date_created
                            }
                        }
                        return make_response(jsonify(result), 200)
                    else:
                        return output
                else:
                    result = {
                        "message": "bucketlist not available"
                    }
                    return make_response(jsonify(result), 404)
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.header('Token', required=True)
    def delete(self, id, item_id):

        """"
        deletes a bucket list item given its id
        """
        access_token = request.headers.get('Token')
        if not access_token:
            result = {
                "message": "unauthorized action"
            }
            return make_response(jsonify(result), 401)

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            buckets = Bucketlist.query.filter_by(id=id).first()
            if isinstance(user_id, int):
                if buckets:
                    output = Bucketlistitem.delete_bucketlistitem(item_id, id)
                    return output
                else:
                    result = {
                        "message": "bucketlist not available"
                    }
                    return make_response(jsonify(result), 404)
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

