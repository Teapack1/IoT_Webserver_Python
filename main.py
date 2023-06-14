from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
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
    unit1 = db.Column(db.String(10))
    unit2 = db.Column(db.String(10))
    unit3 = db.Column(db.String(10))


# from main import app, db, Device
# app.app_context().push()
# db.create_all()

class Sensor:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.time = None
        self.date = None
        self.values = [None, None, None]  # store sensor values in a dictionary
        self.units = [None, None, None]  # store sensor units in a dictionary

    def update_values(self, data, units):
        self.values = [round(int(d),2) for d in data]
        self.units= units


# Define devices---------------------------------------------------------------------------------
SENSORS = [
    Sensor("Teploměr", "Teplota, vlhkost kůlna"),
    Sensor("Stmívač", "Lustr kůlna"),
    Sensor("Elektroměr", "Byt dole"),
    Sensor("Teploměr", "Teplota, vlhkost byt"),
    Sensor("Stmívač", "LED pásek, kůlna"),
    Sensor("Elektroměr", "Byt nahoře"),
    Sensor("t1", "Teploměr Kůlna")      # for testing purposes - aktivní senzor
]
# ---------------------------------------------------------------------------------------------


@app.route('/')
def home():

    temperature_1 = Device.query.filter_by(sensor_id="t1").all()

    x = [record.time for record in temperature_1]
    y = [record.value1 for record in temperature_1]

    # Create a trace
    trace = go.Scatter(
        x = x,
        y = y
    )
    data = [trace]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    thermo = [sensor for sensor in SENSORS if sensor.id.startswith('t')]

    return render_template('index.html', t=thermo, graphJSON=graphJSON)


# dictionary to be sent:
# {
#   "id": "sensor1",
#   "values": {
#     "temperature": 23.5,
#     "humidity": 50.2
#   }
# }

@app.route('/postplain/', methods=['POST'])
def post_plain():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    device_id = data.get('id')
    device_values = data.get('values')
    device_units = data.get('units')

    if device_values and device_id:
        for sensor in SENSORS:
            if sensor.id == device_id:
                sensor.update_values(device_values, device_units)
                print(f'ID: {device_id}, Value: {device_values}')

# Add to database
                device = Device(
                    sensor_id=device_id,
                    name=sensor.name,
                    time=datetime.now(),

                    value1=sensor.values[0],
                    value2=sensor.values[1],
                    #value3=sensor.values[2],

                    unit1=sensor.units[0],
                    unit2=sensor.units[1],
                    #unit3=sensor.units[2]
                )

                db.session.add(device)
                db.session.commit()

                break
        return jsonify({'message': 'Success!'}), 200
    else:
        return jsonify({'message': 'Missing data'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

