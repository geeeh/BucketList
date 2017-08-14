import os

from flask import Flask


from bucketlist.config import app_config
from bucketlist.extensions import bcrypt, db, migrate
from .v1.views import v1

config_name = os.getenv('APP_SETTINGS')


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(app_config[config_object])
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate.init_app(app, db)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(v1)
    return None

app = create_app(config_name)

