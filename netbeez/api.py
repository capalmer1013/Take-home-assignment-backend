from flask import Flask, render_template
from flask_restplus import Resource, Api, fields, reqparse
from flask_socketio import SocketIO, send, emit

from . import models, exceptions, utils

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
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


# socketio stuff


@socketio.on("connect")
def test_connect():
    print("connected")
    emit("my response", {"data": "Connected"})


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected")


@socketio.on_error_default
def error_handler(e):
    # print("An error has occurred: " + str(e))
    send({"error": e.error})


@socketio.on("json")
def handle_data(message):
    # print("stream data", message)
    # sensor types are [electricity, temperature_f, motion, smoke, CO2]
    # expects json with {id: userId, sensor_type: temperature_f, sensor_name: "temp_1", value: 68}
    expectedFields = ["id", "sensor_type", "sensor_name", "value"]
    # print(message)
    valid_request = True
    for key in expectedFields:
        if key not in message:
            valid_request = False

    if not valid_request:
        raise exceptions.BadRequestError(
            error="Must have id, sensor_type, sensor_name, value fields."
        )
    # send(message)


if __name__ == "__main__":
    socketio.run(app)
