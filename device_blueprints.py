from flask import Blueprint, render_template, jsonify, request, Response
from models import Device, db  # Assuming Device is your database model from models.py
from device_core import Sensor, Camera  # Import your Sensor class
from device_routes import SENSORS, CAMERAS  # Import your SENSORS list
import json
import plotly

sensor_blueprint = Blueprint('sensor_blueprint', __name__, template_folder='templates')
camera_blueprint = Blueprint('camera_blueprint', __name__, template_folder='templates')

@sensor_blueprint.route('/plot/<sensor_id>')
def generate_plot(sensor_id):
    sensor = Sensor.find(SENSORS, sensor_id)  # Assuming SENSORS is accessible here
    if not sensor:
        return jsonify({"error": "Sensor not found"}), 404

    fig = sensor.plot(Device, title=sensor.name)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@sensor_blueprint.route('/postplain/', methods=['POST'])
def post_plain():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    device_id = data.get('id')
    device_values = data.get('values')
    device_units = data.get('units')

    if device_values and device_id:
        sensor = Sensor.find(SENSORS, device_id)
        if sensor:
            sensor.update_values(device_values, device_units)

            device = Device(
                sensor_id=device_id,
                name=sensor.name,
                time=sensor.time,
            )

            for i, value in enumerate(sensor.values):
                setattr(device, f"value{i + 1}", value)
            for i, unit in enumerate(sensor.units):
                setattr(device, f"unit{i + 1}", unit)

            db.session.add(device)
            db.session.commit()

            return jsonify({'message': 'Success!'}), 200
        else:
            return jsonify({'message': 'Sensor not found'}), 404
    else:
        return jsonify({'message': 'Missing data'}), 400
    

# -------------- CAMERA ROUTES --------------


@camera_blueprint.route('/video_feed/<camera_id>')
def stream_camera(camera_id):
    """
    Stream the video feed from a specific camera.
    """
    camera = next((cam for cam in CAMERAS if cam.id == camera_id), None)
    if not camera:
        return Response("Camera not found or could not be opened", status=404)
    
    return Response(camera.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_blueprint.route('/refresh_camera')
def refresh_camera():
    success = True
    message = "All cameras refreshed successfully."
    
    for cam in CAMERAS:
        cam.close_camera()
        try:
            cam.__init__(cam.id, cam.name, cam.index)
        except:
            success = False
            message = "Error occurred while refreshing cameras."
            
    return jsonify({"success": success, "message": message})
