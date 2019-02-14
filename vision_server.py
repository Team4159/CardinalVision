import cv2
import zmq
import time
import struct

from vision import Vision


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

        # zmq comms
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://*:5555')  # arbitrary

    def run(self):
        while True:
            self.tick()

            tmp = time.time()
            if self.tick_time - (time.time() - self.last_tick) > 0:
                time.sleep(self.tick_time - (time.time() - self.last_tick))
            self.last_tick = tmp

    def tick(self):
        _, front_frame = self.front_cam.read()
        _, back_frame = self.back_cam.read()

        front_error, _ = Vision.process_image(front_frame)
        back_error, _ = Vision.process_image(back_frame)

        if front_error is None:
           front_error = 0  # don't move if no tapes

        if back_error is None:
            back_error = 0  # don't move if no tapes

        self.socket.send(struct.pack('<2d', front_error, back_error))


if __name__ == '__main__':
    vision_server = VisionServer()
    vision_server.run()
