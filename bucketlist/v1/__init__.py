from flask import Blueprint, request, jsonify, make_response
from flask_restplus import Api, fields, reqparse, Resource, marshal

from bucketlist.model_functions import create_bucketlist, update_bucketlist, delete_bucketlist, update_bucketlistitem, \
    delete_bucketlistitem, create_bucketlistitem, create_user
from bucketlist.models import User, Bucketlist, Bucketlistitem

authorizations = {
    'Bearer': {
        'type': 'apikey',
        'in': 'header',
        'name': 'Token'
    }
}
v1 = Blueprint('v1', __name__)

api = Api(v1, version='1.0', title='Bucket list Application', authorization=authorizations, security='Bearer',
          description='A bucketlist api')

register_expect_fields = api.model('Registration', {
    'username': fields.String(required=True, description='user username'),
    'email': fields.String(required=True, description='user email address'),
    'password': fields.String(required=True, description='user password'),
})

login_expect_fields = api.model('Login', {
    'username': fields.String(required=True, description='user username'),
    'password': fields.String(required=True, description='user password'),
})

user_output_fields = api.model('User', {
    'id': fields.Integer(readOnly=True, description='user unique identifier'),
    'username': fields.String(readOnly=True, description='user username'),
    'email': fields.String(required=True, description='user email address')
})
login_model = api.model('login_model', {
    "username": fields.String(readOnly=True, description='user username'),
    "email": fields.String(readOnly=True, description='user email'),
    "auth_token": fields.String(readOnly=True, description='user auth token'),
})


bucketlist_expect = api.model('Bucketlist_expect', {
    'name': fields.String(description='Bucketlist name', required=True),

})

bucketlistitem_expect = api.model('Bucketlistitem_expect', {
    'name': fields.String(description='Bucketlist name', required=True),
    'done': fields.Boolean(description='bucket list name', required=True),
})

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', location="args", type=int, required=False, default=1)
pagination_arguments.add_argument('limit', location="args", type=int, required=False, default=20)
pagination_arguments.add_argument('q', location="args", required=False)

ns = api.namespace('bucketlist/v1/', description='Operations related to a bucket list')


@ns.route('/auth/register')
class Register(Resource):
    @api.response(201, 'user registered successfully')
    @api.response(400, 'bad request')
    @api.expect(register_expect_fields)
    def post(self):
        """register a user"""
        try:
            user = User.query.filter_by(username=request.json.get("username")).first()
            if user:
                return "user already exists", 202
            user = User.query.filter_by(email=request.json.get("email")).first()
            if user:
                result = {
                    'message': "email already exists",
                }

                return make_response(jsonify(result), 202)
            create_user(request.json)
            result = {
                'message': "user registered successfully",
            }
            return make_response(jsonify(result), 201)
        except:
            result = {
                'message': "database error"
            }
            return make_response(jsonify(result), 500)


@ns.route('/auth/login')
class Login(Resource):
    @api.expect(login_expect_fields)
    def post(self):
        """login as a user"""
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
        except:
            result = {
                'message': "database error",
            }
            return make_response(jsonify(result), 500)


@ns.route('/bucketlists')
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
                        Bucketlist.name.like(search_words + "%")).paginate(page, limit, False)
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

                bucketlists_page = Bucketlist.query.filter_by(created_by=user_id).paginate(page=page,
                                                                                           per_page=limit,
                                                                                           error_out=False)

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
                    return make_response(jsonify(result), 204)

            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)

    @api.expect(bucketlist_expect)
    @api.header('Token', required=True)
    def post(self):

        """
        insert a bucket list
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
                creation_output = create_bucketlist(user_id, request.json)
                if creation_output:
                    result = {
                        "message": "post data not provided"
                    }
                    return make_response(jsonify(result), 400)
                else:
                    result = {
                        "message": "Bucketlist successfully created"
                    }
                    return make_response(jsonify(result), 201)
            else:
                result = {
                    "message": "unauthorized action"
                }
                return make_response(jsonify(result), 401)


@ns.route('/bucketlists/<int:id>')
class BucketlistModification(Resource):
    @api.response(404, 'bucket list <bucketlist_id> not found')
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
    @api.response(204, 'Bucketlist successfully updated.')
    @api.header('Token', required=True)
    def put(self, id):

        """
        updates a bucket list given id and the data
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
                output = update_bucketlist(id, user_id, request.json)
                if not output:
                    result = {
                        "message": "Bucketlist successfully updated"
                    }
                    return make_response(jsonify(result), 204)

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

    @api.response(204, 'Bucketlist successfully deleted')
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
                output = delete_bucketlist(id)
                if not output:
                    result = {
                        "message": "Bucketlist successfully deleted"
                    }
                    return make_response(jsonify(result), 204)

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


ns = api.namespace('bucketlist/v1/', description='Operations related to a bucket list items')


@ns.route('/bucketlists/<int:id>/items')
@api.doc(params={})
class Bucketlistitems(Resource):
    """
    Shows a list of all bucketlists, and lets you POST to add new bucketlists
    """

    @api.response(400, 'bad request')
    @api.header('Token', required=True)
    @api.expect(bucketlistitem_expect)
    def post(self, id):
        """insert a bucket list"""
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
            if buckets:
                if isinstance(user_id, int):
                    create_bucketlistitem(id, request.json)
                    result = {
                        "message": "Bucketlistitem successfully created"
                    }
                    return make_response(jsonify(result), 201)
                else:
                    result = {
                        "message": "unauthorized action"
                    }
                    return make_response(jsonify(result), 201)
            else:
                result = {
                    "message": "bad request"
                }
                return make_response(jsonify(result), 400)


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

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_auth_token(access_token)
            buckets = Bucketlist.query.filter_by(id=id).first()
            if buckets:
                if isinstance(user_id, int):
                    output = update_bucketlistitem(id, item_id, request.json)
                    if not output:
                        result = {
                            "message": "Bucketlistitem successfully updated"
                        }
                        return make_response(jsonify(result), 204)
                    else:
                        result = {
                            "message": "Item not found"
                        }
                        return make_response(jsonify(result), 404)

                else:
                    result = {
                        "message": "unauthorized action"
                    }
                    return make_response(jsonify(result), 401)
            else:
                result = {
                    "message": "bad request"
                }
                return make_response(jsonify(result), 400)

    @api.header('Token', required=True)
    def delete(self, id, item_id):

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
            buckets = Bucketlist.query.filter_by(id=id).first()
            if buckets:
                if isinstance(user_id, int):
                    output = delete_bucketlistitem(item_id, id)
                    if not output:

                        result = {
                            "message": "Bucketlistitem successfully deleted"
                        }
                        return make_response(jsonify(result), 204)
                    else:
                        result = {
                            "message": "Item not found"
                        }
                        return make_response(jsonify(result), 404)

                else:
                    result = {
                        "message": "unauthorized action"
                    }
                    return make_response(jsonify(result), 401)
            else:
                result = {
                    "message": "bad request"
                }
                return make_response(jsonify(result), 400)
