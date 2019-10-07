# stdlib imports
import os

# flask imports
from flask_migrate import Migrate

# project imports
from .models import db
from .api import app

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = bool(int(os.environ.get("SQLALCHEMY_ECHO", False)))
migrate = Migrate(app, db)
db.init_app(app)
