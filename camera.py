# https://github.com/log0/video_streaming_with_flask_example/blob/master/camera.py

import cv2
import zmq


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 2 and 3.
        self.video0 = cv2.VideoCapture(0)
        self.video1 = cv2.VideoCapture(1)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://127.0.0.1:5803')  # arbitrary
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

        self.switch = False
        self.last_value = 0

    def __del__(self):
        self.video0.release()
        self.video1.release()

    def get_frame(self):
        value = int(self.socket.recv())

        if value and not self.last_value:
            self.switch = not self.switch

        self.last_value = value

        if self.switch:
            success, image = self.video1.read()
            image = cv2.applyColorMap(image, cv2.COLORMAP_PINK)

        else:
            success, image = self.video0.read()
            image = cv2.applyColorMap(image, cv2.COLORMAP_BONE)

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
