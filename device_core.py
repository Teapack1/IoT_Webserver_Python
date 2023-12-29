import cv2
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import threading
import os
import time

class Camera:
    def __init__(self, id, name, index=0, fps=1, save_duration=0.1, rtsp=None):
        self.name = name
        self.id = id
        self.fps = fps
        self.save_duration = save_duration
        self.index = rtsp if rtsp else index

        # Initialize camera in a separate thread to avoid blocking
        self.cap = None
        self.frame_width = 1980
        self.frame_height = 720
        self.frame_count = 0
        self.start_time = time.time()
        self.initialization_thread = threading.Thread(target=self.initialize_camera)
        self.initialization_thread.start()

    def initialize_camera(self):
        self.cap = cv2.VideoCapture(self.index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        # Wait for camera to open or timeout after 10 seconds
        start_time = time.time()
        while not self.cap.isOpened():
            time.sleep(0.1)
            if time.time() - start_time > 10:  # 10 seconds timeout
                print(f"Timeout: Unable to open camera {self.id} - {self.name}")
                break


    def save_frame(self, frame):
        filename = "video/frames/frame_{}.jpg".format(self.frame_count)
        cv2.imwrite(filename, frame)
        self.frame_count += 1

    def create_video_from_frames(self):
        filename = "video/outpy_{}.mp4".format(time.strftime("%Y%m%d-%H%M%S"))
        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.frame_width, self.frame_height))
        for i in range(self.frame_count):
            frame = cv2.imread("video/frames/frame_{}.jpg".format(i))
            out.write(frame)
            os.remove("video/frames/frame_{}.jpg".format(i))
        out.release()
        self.frame_count = 0

    def gen_frames(self):
        i = 0
        if not self.cap or not self.cap.isOpened():
            yield b''  # Return empty bytes if camera is not available
            return
        while True:
            success, frame = self.cap.read()
            if not success:
                break
            else:
                if i % 20 == 0:
                    self.save_frame(frame)
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                i += 1
                if time.time() - self.start_time > self.save_duration * 3600:
                    self.create_video_from_frames()
                    self.start_time = time.time()

    def close_camera(self):
        self.cap.release()
        self.out.release()


class Sensor:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.time = datetime.now()
        self.values = [None,None,None,None,None,None]  # store sensor values in a dictionary
        self.units = [None,None,None,None,None,None]  # store sensor units in a dictionary

    def update_values(self, data, units):
        self.values = [round(float(d), 4) for d in data]
        self.units = units
        self.time = datetime.now()
        print(self.values, self.units)

    def find(devices, id):
        for device in devices:
            if device.id == id:
                return device
        return None  # device not found

    def plot(self, Db_class):
        # Get the current date and time
        now = datetime.now()

        # Calculate the date and time 10 days ago
        ten_days_ago = now - timedelta(days=300)

        # Query the database for records from the last 10 days

        ele_1 = Db_class.query.filter(Db_class.sensor_id == self.id, Db_class.time >= ten_days_ago).all()

        x = [record.time for record in ele_1]
        y1 = [record.value4 for record in ele_1]
        y2 = [record.value3 for record in ele_1]  # Assuming value2 exists

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=x, y=y1, name="Spotřeba['kWh'])"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=x, y=y2, name="Aktuální výkon['W']"),
            secondary_y=True,
        )

        fig.update_layout(
            autosize=True,
            title='Spotřeba elektřiny spodní byt',
            margin=dict(
                l=80,
                r=20,
                b=20,
                t=60,
                pad=4
            ),
            paper_bgcolor='#F5F5F5',
            plot_bgcolor='#FFFFFF'
        )

        fig.update_xaxes(title_text='Datum a čas')
        fig.update_yaxes(title_text="Spotřeba [kWh]", secondary_y=False)
        fig.update_yaxes(title_text="Aktuální výkon [W]", secondary_y=True)

        return fig