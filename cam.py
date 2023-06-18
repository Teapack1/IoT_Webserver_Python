import cv2

class Camera:
    def __init__(self, id, name, index):
        self.index = index
        self.name = name
        self.id = id
        self.cap = cv2.VideoCapture(self.index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

    def gen_frames(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def close_camera(self):
        self.cap.release()

