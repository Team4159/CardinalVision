from CardinalVision.vision import Vision
import cv2
import zmq
import time
import struct


class VisionServer:
    tick_time = 1 / 60  # same as camera loop but can be tuned differently

    def __init__(self):
        # cameras
        self.front_cam = cv2.VideoCapture(2)  # arbitrary
        self.back_cam = cv2.VideoCapture(3)  # arbitrary

        # self.front_cam.set(3, 320) theoretically you can set the camera properties
        # self.back_cam.set(4, 240)

        # zmq comms
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://*:5802')  # arbitrary

    def run(self):
        last_tick = time.time()

        while True:
            self.tick()

            tmp = time.time()
            if VisionServer.tick_time - (time.time() - last_tick) > 0:
                time.sleep(VisionServer.tick_time - (time.time() - last_tick))
            last_tick = tmp

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
