from device_core import Camera, Sensor

# Define devices
SENSORS = [
    Sensor("e1", "elektro spodní byt"),
    Sensor("e2", "elektro horní byt"),
    Sensor("e3", "elektro dílna"),
    Sensor("e4", "elektro čerpadlo"),
    Sensor("t1", "teplota spodní kuchyň"),
    Sensor("t2", "teplota horní kuchyň"),
    Sensor("t3", "teplota půda"),
    Sensor("t4", "teplota venkovní"),
]

CAMERAS = [
    #Camera(id="c1", name="Garáže", rtsp='rtsp://169.254.0.99:554/live.sdp'),
    Camera(id="c2", name="Kůlna", index=0)
]

LIGHTING_DATA = {}