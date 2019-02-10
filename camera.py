# https://github.com/log0/video_streaming_with_flask_example/blob/master/camera.py

import cv2


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0 and 1.
        self.video0 = cv2.VideoCapture(0)
        self.video1 = cv2.VideoCapture(1)

    def __del__(self):
        self.video0.release()
        self.video1.release()

    switch = False

    def get_frame(self):

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
