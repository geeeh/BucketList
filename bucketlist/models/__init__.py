

import datetime
import os

import jwt

from bucketlist.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

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

    def __repr__(self):
        return '<User %r>' % self.username


class Bucketlistitem(db.Model):
    __tablename__ = 'bucketlistitems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))
    bucketlist = db.relationship('Bucketlist',
                                 backref=db.backref('bucketlistitem', lazy='dynamic'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, done, bucketlist_id):
        self.name = name
        self.bucketlist_id = bucketlist_id
        self.done = done

    def __repr__(self):
        return '<Bucketlist item %r>' % self.name


class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    user = db.relationship('User',
                           backref=db.backref('bucketlist', lazy='dynamic'))

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by


    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def __repr__(self):
        return '<Bucketlist %r>' % self.name