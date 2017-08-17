import datetime

import os

import jwt
from sqlalchemy.orm import relationship

from bucketlist.Exceptions.invalid_query import InvalidQuery
from bucketlist.extensions import db, bcrypt


class User(db.Model):
    # Model of a user for table mapping
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)

    bucketlists = relationship(
        "Bucketlist",
        backref="users",
        cascade="all, delete-orphan",
        lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        return self.password

    def check_password(self, passw):
        return bcrypt.check_password_hash(self.password.encode('utf-8'), passw)

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def create_user(username, email, password):
        # Add a new user to the users table
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                return "user already exists", 202
            user = User.query.filter_by(email=email).first()
            if user:
                return "email already exists", 202
        except InvalidQuery:
            return "Query error!"

        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, username=None, email=None, password=None):
        # Allow Modification of user data
        try:
            user = User.query.filter_by(id=user_id).first()
        except InvalidQuery:
            return "Query error!"

        if user:
            if username:
                user.username = username
            if email:
                user.email = email
            if password:
                user.password = User.hash_password(password)
        else:
            return "user not found", 404
        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def delete_user(user_id):
        # Allow deletion of user data
        try:
            user = User.query.filter_by(id=user_id).first()
        except InvalidQuery:
            return "Query error", 500
        if user:
            db.session.delete(user)
            db.session.commit()
        return "user deleted", 200

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token

        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1200),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                os.getenv('SECRET'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token

        """
        try:
            payload = jwt.decode(auth_token, os.getenv('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    bucketlists = relationship(
        "Bucketlistitem",
        backref="bucketlists",
        cascade="all, delete-orphan",
        lazy='dynamic')

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def __repr__(self):
        return '<Bucketlist %r>' % self.name

    @staticmethod
    def create_bucketlist(user_id, name):
        try:
            buckets = Bucketlist.query.filter_by(name=name).first()
            if buckets:
                return "Bucketlist name already taken!"
        except InvalidQuery:
            return "Query Error!"
        bucketlist = Bucketlist(name, user_id)
        db.session.add(bucketlist)
        db.session.commit()
        return bucketlist

    @staticmethod
    def update_bucketlist(bucketlist_id, user_id, name=None):
        try:
            bucketlist = Bucketlist.query.filter_by(id=bucketlist_id).first()
            if not bucketlist:
                return "Bucketlist not found", 404
        except InvalidQuery:
            return "Query Error", 500
        if name:
            bucketlist.name = name
        bucketlist.user_id = user_id

        db.session.add(bucketlist)
        db.session.commit()
        return bucketlist

    @staticmethod
    def delete_bucketlist(bucketlist_id):
        try:
            bucketlist = Bucketlist.query.filter_by(id=bucketlist_id).first()
            if not bucketlist:
                return "Bucketlist not found", 404
        except InvalidQuery:
            return "Query Error", 500
        db.session.delete(bucketlist)
        db.session.commit()
        return "Bucketlist successfully deleted", 200


class Bucketlistitem(db.Model):
    __tablename__ = 'bucketlistitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))
    date_created = db.Column(db.DateTime,
                             default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, done, bucketlist_id):
        self.name = name
        self.bucketlist_id = bucketlist_id
        self.done = done

    @staticmethod
    def create_bucketlistitem(bucketlist_id, name, done):
        try:
            bucketlistitem = Bucketlistitem.query.filter_by(
                name=name, bucketlist_id=bucketlist_id).first()
            if bucketlistitem:
                return "Item name already taken!", 200
        except InvalidQuery:
            return "query error", 500
        bucketlistitem = Bucketlistitem(name, done, bucketlist_id)
        db.session.add(bucketlistitem)
        db.session.commit()
        return bucketlistitem

    @staticmethod
    def update_bucketlistitem(
            bucketlistitem_id,
            bucketlist_id,
            name=None,
            done=None):
        try:
            bucketlistitem = Bucketlistitem.query.filter_by(
                id=bucketlistitem_id, bucketlist_id=bucketlist_id).first()
            if not bucketlistitem:
                return "Item not found!"
        except InvalidQuery:
            return "Query Error!", 500
        if name:
            bucketlistitem.name = name
        if done:
            bucketlistitem.done = done
        bucketlistitem.bucketlist_id = bucketlist_id
        db.session.add(bucketlistitem)
        db.session.commit()
        return bucketlistitem

    @staticmethod
    def delete_bucketlistitem(bucketlistitem_id, bucketlist_id):
        try:
            bucketlistitem = Bucketlistitem.query.filter_by(
                id=bucketlistitem_id, bucketlist_id=bucketlist_id).first()
            if not bucketlistitem:
                return "Item not found!", 404
        except BaseException:
            return "Query Error!", 500
        db.session.delete(bucketlistitem)
        db.session.commit()
        return "Bucketlistitem successfully deleted", 200

    def __repr__(self):
        return '<Bucketlist item %r>' % self.name
