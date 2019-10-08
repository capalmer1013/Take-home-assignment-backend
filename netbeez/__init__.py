# stdlib imports
import os

# flask imports
from flask_migrate import Migrate
from flask_cors import CORS


# project imports
from .models import db
from .api import app

CORS(app, expose_headers=["X-Authentication-JWT"])
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = bool(int(os.environ.get("SQLALCHEMY_ECHO", False)))
migrate = Migrate(app, db)
db.init_app(app)
