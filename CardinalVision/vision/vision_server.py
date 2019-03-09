from CardinalVision.vision import Vision
import cv2
import zmq
import struct


class VisionServer:
    tick_time = 1 / 60  # same as camera loop but can be tuned differently

    def __init__(self):
        print('Starting Vision Server...')

        # cameras
        self.front_cam = cv2.VideoCapture(2)  # arbitrary
        self.back_cam = cv2.VideoCapture(3)  # arbitrary
        # self.front_cam.set(3, 320) theoretically you can set the camera properties
        # self.back_cam.set(4, 240)

        # zmq comms
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://*:5801')
        self.socket.setsockopt(zmq.CONFLATE, 1)

    def run(self):
        while True:
            _, front_frame = self.front_cam.read()
            _, back_frame = self.back_cam.read()

            front_error = Vision.process_image(front_frame)
            back_error = Vision.process_image(back_frame)

            self.socket.send(struct.pack('<2d', front_error, back_error))


if __name__ == '__main__':
    vision_server = VisionServer()
    vision_server.run()
