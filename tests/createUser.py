from netbeez import app
from netbeez.models import User_Account
import getpass

print("current db in .env config: " + app.config["SQLALCHEMY_DATABASE_URI"])
app.config["SQLALCHEMY_DATABASE_URI"] = (
    input("enter new database uri or leave blank for env value: ")
    or app.config["SQLALCHEMY_DATABASE_URI"]
)

with app.app_context():
    user_id = User_Account.create().id

print("New user id: ", user_id)
