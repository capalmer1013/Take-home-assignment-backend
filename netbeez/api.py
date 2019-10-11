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
        q = models.Data_Stream.query.filter_by(user_id=userid).all()
        if len(q) > 1000:
            for i in range(1000 - len(q)):
                models.db.session.delete(q[i])
            models.db.session.commit()

        dataStream = []
        for each in q:
            dataStream.append(
                {
                    "sensor_type": each.key,
                    "value": each.value,
                    "timestamp": each.timestamp,
                }
            )

        dataStream.sort(key=lambda x: x["timestamp"])
        current_time = time.time()
        electricityList = list(
            filter(lambda x: x["sensor_type"] == "electricity_w", dataStream)
        )
        electricityList_15m = list(
            filter(lambda x: current_time - x["timestamp"] < 900.0, electricityList)
        )
        electricityList_60m = list(
            filter(lambda x: current_time - x["timestamp"] < 3600.0, electricityList)
        )

        temperatureList = list(
            filter(lambda x: x["sensor_type"] == "temperature_f", dataStream)
        )
        temperatureList_15m = list(
            filter(lambda x: current_time - x["timestamp"] < 900.0, temperatureList)
        )
        temperatureList_60m = list(
            filter(lambda x: current_time - x["timestamp"] < 3600.0, temperatureList)
        )

        motionList = list(
            filter(lambda x: x["sensor_type"] == "motion_bool", dataStream)
        )
        smokeList = list(filter(lambda x: x["sensor_type"] == "smoke_bool", dataStream))

        CO2List = list(filter(lambda x: x["sensor_type"] == "CO2_ppm", dataStream))
        CO2List_15m = list(
            filter(lambda x: current_time - x["timestamp"] < 900.0, CO2List)
        )
        CO2List_60m = list(
            filter(lambda x: current_time - x["timestamp"] < 3600.0, CO2List)
        )
        print(CO2List_15m)
        print(len(CO2List_15m) > 0)
        return {
            "electricity_w": {
                "current": max(
                    electricityList, key=lambda x: x["timestamp"], default={"value": 0}
                )["value"],
                "15m": sum([float(x["value"]) for x in electricityList_15m])
                / len(electricityList_15m)
                if len(electricityList_15m) > 0
                else None,
                "60m": sum([float(x["value"]) for x in electricityList_60m])
                / len(electricityList_60m)
                if len(electricityList_60m) > 0
                else None,
            },
            "temperature_f": {
                "current": max(
                    temperatureList, key=lambda x: x["timestamp"], default={"value": 0}
                )["value"],
                "15m": sum([float(x["value"]) for x in temperatureList_15m])
                / len(temperatureList_15m)
                if len(temperatureList_15m) > 0
                else None,
                "60m": sum([float(x["value"]) for x in temperatureList_60m])
                / len(temperatureList_60m)
                if len(temperatureList_60m) > 0
                else None,
            },
            "motion_bool": {
                "current": max(
                    motionList, key=lambda x: x["timestamp"], default={"value": False}
                )["value"]
            },
            "smoke_bool": {
                "current": max(
                    smokeList, key=lambda x: x["timestamp"], default={"value": False}
                )["value"]
            },
            "CO2_ppm": {
                "current": max(
                    CO2List, key=lambda x: x["timestamp"], default={"value": 0}
                )["value"],
                "15m": sum([float(x["value"]) for x in CO2List_15m]) / len(CO2List_15m)
                if len(CO2List_15m) > 0
                else None,
                "60m": sum([float(x["value"]) for x in CO2List_60m]) / len(CO2List_60m)
                if len(CO2List_60m) > 0
                else None,
            },
        }


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
    pass
    # join_room(data["id"])


@socketio.on("leave")
def on_leave(data):
    leave_room(data["id"])


@socketio.on_error_default
def error_handler(e):
    print("An error has occurred: " + str(e))
    # send({"error": e.error})


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

    if (
        message["sensor_type"] == "motion_bool"
        or message["sensor_type"] == "smoke_bool"
    ):
        message["value"] = bool(message["value"])

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
    emit(
        "live",
        {
            "key": message["sensor_type"],
            "value": message["value"],
            "timestamp": timestamp,
        },
        broadcast=True,
        include_self=False,
    )
    # emit(
    #     "live",
    #     {
    #         "key": message["sensor_type"],
    #         "value": message["value"],
    #         "timestamp": timestamp,
    #     },
    #     room=message["id"],
    # )
    print("success")


if __name__ == "__main__":
    socketio.run(app)
