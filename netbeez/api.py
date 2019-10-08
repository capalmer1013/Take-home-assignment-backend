import time

from flask import Flask, render_template
from flask_restplus import Resource, Api, fields, reqparse
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS

from . import models, exceptions, utils

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["X-Authentication-JWT"])
socketio = SocketIO(app, cors_allowed_origins="*")
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
        result = {}
        q = models.Data_Stream.query.filter_by(user_id=userid).all()
        for each in q:
            if each.key not in result:
                result[each.key] = {"x": [], "y": []}

            result[each.key]["x"].append(each.timestamp)
            result[each.key]["y"].append(each.value)
        return [
            {"label": each, "x": result[each]["x"], "y": result[each]["y"]}
            for each in result
        ]


@api.route("/users/<userid>/<sensor_type>")
class UserDetailsEndpoints(Resource):
    def get(self, userid, sensor_type):
        result = {}
        q = models.Data_Stream.query.filter_by(user_id=userid, key=sensor_type).all()
        for each in q:
            if each.key not in result:
                result[each.key] = {"x": [], "y": []}

            result[each.key]["x"].append(each.timestamp)
            result[each.key]["y"].append(each.value)
        return [
            {"label": each, "x": result[each]["x"], "y": result[each]["y"]}
            for each in result
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
    print("An error has occurred: " + str(e))
    send({"error": e.error})


@socketio.on("json")
def handle_data(message):
    print(message)
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
        "CO2_ppm": int,
    }
    valid_request = True
    for key in expectedFields:
        if key not in message:
            print("missing key", key)
            valid_request = False

    if valid_request and message["sensor_type"] not in sensor_types:
        print("invalid sensor type", message["sensor_type"])
        valid_request = False

    if (
        valid_request
        and not models.User_Account.query.filter_by(id=message["id"]).first()
    ):
        print("invalid id", message["id"])
        valid_request = False

    if not valid_request:
        raise exceptions.BadRequestError(
            error="Must have id, sensor_type, sensor_name, value fields."
        )
    timestamp = time.time()
    models.Data_Stream.create(
        user_id=message["id"],
        key=message["sensor_type"],
        value=message["value"],
        timestamp=timestamp,
    )
    send(
        {
            "key": message["sensor_type"],
            "value": message["value"],
            "timestamp": timestamp,
        },
        room=message["id"],
    )
    print("success")


if __name__ == "__main__":
    socketio.run(app)
