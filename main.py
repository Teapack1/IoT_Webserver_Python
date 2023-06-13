from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import plotly
import plotly.graph_objs as go
import numpy as np
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.db'
db = SQLAlchemy(app)
Bootstrap(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sensor_id = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    value1 = db.Column(db.Float, nullable=False)
    value2 = db.Column(db.Float)
    value3 = db.Column(db.Float)


class Sensor:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.time = None
        self.date = None
        self.values = {}  # store sensor values in a dictionary

    def update_values(self, data):
        for key, value in data.items():
            self.values[key] = value


# Define devices---------------------------------------------------------------------------------
SENSORS = [
    Sensor("Teploměr", "Teplota, vlhkost kůlna"),
    Sensor("Stmívač", "Lustr kůlna"),
    Sensor("Elektroměr", "Byt dole"),
    Sensor("Teploměr", "Teplota, vlhkost byt"),
    Sensor("Stmívač", "LED pásek, kůlna"),
    Sensor("Elektroměr", "Byt nahoře")
]
# ---------------------------------------------------------------------------------------------


@app.route('/')
def home():

    x = np.linspace(0, 10, 1000)
    y = np.sin(x)

    # Create a trace
    trace = go.Scatter(
        x = x,
        y = y
    )
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('index.html', devices=SENSORS, graphJSON=graphJSON)


# dictionary to be sent:
# {
#   "id": "sensor1",
#   "values": {
#     "temperature": 23.5,
#     "humidity": 50.2
#   }
# }

@app.route('/postplain', methods=['POST'])
def post_plain():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    sensor_id = data.get('id')
    sensor_value = data.get('values')

    if sensor_value and sensor_id:
        for sensor in SENSORS:
            if sensor.id == sensor_id:
                sensor.update_values(sensor_value)
                print(f'ID: {sensor_id}, Value: {sensor_value}')

# Add to database
                device = Device(
                    sensor_id=sensor_id,
                    name=sensor.name,
                    time=datetime.now(),
                )
                for key, value in sensor_value.items():
                    setattr(device, key, value)
                db.session.add(device)
                db.session.commit()

                break
        return jsonify({'message': 'Success!'}), 200
    else:
        return jsonify({'message': 'Missing data'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

