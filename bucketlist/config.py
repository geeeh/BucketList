import os


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://godwingitonga@localhost/bucketlist'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://godwingitonga@localhost/bucketlist'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    DEBUG = True


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
