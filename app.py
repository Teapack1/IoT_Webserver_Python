from flask import Flask, render_template, request, jsonify, Response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import plotly 
import requests
from device_core import Camera, Sensor
from models import init_db, Device
from device_routes import SENSORS, CAMERAS, LIGHTING_DATA
from config import Config
from flask import Flask, render_template, jsonify
from device_blueprints import sensor_blueprint, camera_blueprint

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)
init_db(app)

# from main import app, db, Device
# app.app_context().push()
# db.create_all()

app.register_blueprint(sensor_blueprint, url_prefix='/sensors')
app.register_blueprint(camera_blueprint, url_prefix='/cameras')

# ---------------------------------------------------------------------------------------------
        
@app.route('/')
def home():
    def generate_sensor_plot(sensor_id, title):
        sensor = Sensor.find(SENSORS, sensor_id)
        if sensor:
            fig = sensor.plot(Device)
            fig.update_layout(title=title)
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return None

    # Generate plots for specific sensors
    graphJSON_1 = generate_sensor_plot("e1", 'Spotřeba elektřiny spodní byt')
    graphJSON_2 = generate_sensor_plot("e2", 'Spotřeba elektřiny horní byt')
    graphJSON_3 = generate_sensor_plot("e3", 'Spotřeba elektřiny čerpadlo')

    # Filter sensors based on their types
    thermo = [sensor for sensor in SENSORS if sensor.id.startswith('t')]
    ele = [sensor for sensor in SENSORS if sensor.id.startswith('e')]

    # Render the index template with the plot data and sensor lists
    return render_template('index.html', t=thermo, e=ele, graphJSON_1=graphJSON_1, graphJSON_2=graphJSON_2, graphJSON_3=graphJSON_3, cameras=CAMERAS)


@app.route('/lighting-data/', methods=['POST', 'GET'])
def receive_data():
    global LIGHTING_DATA
    print(LIGHTING_DATA)

    try:
        if request.method == 'POST':
            address_value = request.json.get('address')
            intensity_value = request.json.get('value')

            if intensity_value is None:
                return jsonify({"error": "Value not provided"}), 400
            if address_value is None:
                return jsonify({"error": "Address not provided"}), 400
            address_value = int(address_value)

            LIGHTING_DATA[address_value] = intensity_value

            response = requests.post(f"http://127.0.0.1:1880/", json={"daliData_flask":[address_value, intensity_value]}, timeout=1)
            response.raise_for_status()

            return jsonify({"address": address_value, "value": intensity_value}), 200
        
        elif request.method == 'GET':
            address_value = request.args.get('address')
            if not address_value:
                return jsonify({"error": "Address not provided"}), 400
            address_value = int(address_value)
            intensity_value = LIGHTING_DATA.get(address_value, 0)

            return jsonify({"address": address_value, "value": intensity_value}), 200
    
    except requests.RequestException as e:
        print("debug")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
