from flask import Flask, render_template
from flask_restplus import Resource, Api, fields, reqparse
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from . import models, exceptions, utils

app = Flask(__name__)
socketio = SocketIO(app)
api = Api(app, title="NetBeez Application API")


@app.before_request
def func_before_request():
    pass


@app.after_request
def func_after_request(response):
    return response


# Catch all Bad Request exceptions and exceptions that inherit from it
@api.errorhandler(exceptions.BadRequestError)
def handle_auth_error(ex):
    return ex.error, ex.status_code


@api.route("/")
class BaseEndpoint(Resource):
    @api.doc(description="Base Endpoint")
    def get(self):
        return {}


@api.route("/users")
class UsersEndpoints(Resource):
    def get(self):
        return [x.id for x in models.User_Account.query.all()]


@api.route("/users/<userid>")
class UserDetailsEndpoints(Resource):
    def get(self, userid):
        return [
            {"key": x.key, "value": x.value}
            for x in models.Data_Stream.query.filter_by(user_id=userid).all()
        ]


# socketio stuff


@socketio.on("connect")
def test_connect():
    emit("my response", {"data": "Connected"})


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected")


@socketio.on("join")
def on_join(data):
    join_room(data["id"])


@socketio.on("leave")
def on_leave(data):
    leave_room(data["id"])


@socketio.on_error_default
def error_handler(e):
    # print("An error has occurred: " + str(e))
    send({"error": e.error})


@socketio.on("json")
def handle_data(message):
    expectedFields = ["id", "sensor_type", "sensor_name", "value"]
    sensor_types = [
        "electricity_w",
        "temperature_f",
        "motion_bool",
        "smoke_bool",
        "CO2_ppm",
    ]
    sensor_value_types = {
        "electricity_w": float,
        "motion_bool": bool,
        "smoke_bool": bool,
        "CO2_ppm": float,
    }
    valid_request = True
    for key in expectedFields:
        if key not in message:
            valid_request = False

    if valid_request and message["sensor_type"] not in sensor_types:
        valid_request = False

    if valid_request and not isinstance(
        message["value"], sensor_value_types[message["sensor_type"]]
    ):
        valid_request = False
    if (
        valid_request
        and not models.User_Account.query.filter_by(id=message["id"]).first()
    ):
        valid_request = False

    if not valid_request:
        raise exceptions.BadRequestError(
            error="Must have id, sensor_type, sensor_name, value fields."
        )

    models.Data_Stream.create(
        user_id=message["id"], key=message["sensor_type"], value=message["value"]
    )
    send({"key": message["sensor_type"], "value": message["value"]}, room=message["id"])


if __name__ == "__main__":
    socketio.run(app)
