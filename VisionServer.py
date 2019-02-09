import cv2
import wpilib
import zmq
import time
import struct

from Vision import Vision


class VisionServer:
    def __init__(self):
        # looping
        self.last_tick = time.time()
        self.tick_time = 0.1  # arbitrary, tune for with live camera and zmq

        # cameras
        self.front_cam = cv2.VideoCapture(0)  # arbitrary
        self.back_cam = cv2.VideoCapture(1)  # arbitrary

        # self.front_cam.set(3, 320) theoretically you can set the camera properties
        # self.back_cam.set(4, 240)

        self.camera = self.front_cam

        # controls
        self.xbox_port = 2  # change xbox usb port
        self.xbox = wpilib.xboxcontroller.XboxController(self.xbox_port)
        self.button_number = 1

        # zmq comms
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://127.0.0.1:5555')  # arbitrary

    def mainloop(self):
        while True:
            self.run()

            tmp = time.time()
            if self.tick_time - (time.time() - self.last_tick) > 0:
                time.sleep(self.tick_time - (time.time() - self.last_tick))
            self.last_tick = tmp

    def run(self):
        if self.xbox.getRawButtonPressed(self.button_number):
            self.camera = self.back_cam if self.camera is self.front_cam else self.front_cam

        _, frame = self.camera.read()

        translationValue, _ = Vision.process_image(frame)

        if translationValue is None:
            translationValue = 0  # don't move if no tapes

        self.socket.send(struct.pack('d', translationValue))
