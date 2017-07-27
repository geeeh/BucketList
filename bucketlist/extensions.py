from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth


bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
auth = HTTPBasicAuth()

