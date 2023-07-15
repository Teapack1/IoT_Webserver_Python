from flask import Flask, render_template, request, jsonify, Response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import plotly
from cam import Camera, Sensor

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
    value4 = db.Column(db.Float)
    value5 = db.Column(db.Float)
    value6 = db.Column(db.Float)
    unit1 = db.Column(db.String(10))
    unit2 = db.Column(db.String(10))
    unit3 = db.Column(db.String(10))
    unit4 = db.Column(db.String(10))
    unit5 = db.Column(db.String(10))
    unit6 = db.Column(db.String(10))


# from main import app, db, Device
# app.app_context().push()
# db.create_all()


# Define devices---------------------------------------------------------------------------------
SENSORS = [
    Sensor("e1", "elektro spodní byt"),
    Sensor("e2", "elektro horní byt"),
    Sensor("e3", "elektro čerpadlo"),
]

CAMERAS = [
#    Camera(id="c1", name="Garáže", rtsp='rtsp://169.254.0.99:554/live.sdp')
]


# ---------------------------------------------------------------------------------------------
for index, camera in enumerate(CAMERAS):
    app.add_url_rule('/video_feed/' + camera.id,
                     'video_feed_' + camera.id,
                     (lambda camera: lambda: Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame'))(camera))


@app.route('/')
def home():

    fig1 = Sensor.find(SENSORS, "e1").plot(Device)
    fig1.update_layout(
        title='Spotřeba elektřiny spodní byt')
    graphJSON_1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    fig2 = Sensor.find(SENSORS, "e2").plot(Device)
    fig2.update_layout(
        title='Spotřeba elektřiny horní byt')
    graphJSON_2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    fig3 = Sensor.find(SENSORS, "e3").plot(Device)
    fig3.update_layout(
        title='Spotřeba elektřiny čerpadlo')
    graphJSON_3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)


    thermo = [sensor for sensor in SENSORS if sensor.id.startswith('t')]
    ele = [sensor for sensor in SENSORS if sensor.id.startswith('e')]

    return render_template('index.html', t=thermo, e=ele, graphJSON_1=graphJSON_1, graphJSON_2=graphJSON_2, graphJSON_3=graphJSON_3, cameras=CAMERAS)


@app.route('/postplain/', methods=['POST'])
def post_plain():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    device_id = data.get('id')
    device_values = data.get('values')
    device_units = data.get('units')


    if device_values[0] and device_id:
        sensor = Sensor.find(SENSORS, device_id)
        sensor.update_values(device_values, device_units)

# Add to database
        device = Device(
            sensor_id=device_id,
            name=sensor.name,
            time=sensor.time,
            )

        for i in range(len(sensor.values)):
            setattr(device, f"value{i + 1}", sensor.values[i])
        for i in range(len(sensor.units)):
            setattr(device, f"unit{i + 1}", sensor.units[i])

        db.session.add(device)
        db.session.commit()

        return jsonify({'message': 'Success!'}), 200
    else:
        return jsonify({'message': 'Missing data'}), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

