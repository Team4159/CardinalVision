import cv2
import numpy as np
import zmq


class StreamDisplay:
    def __init__(self):
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.SUB)
        self.footage_socket.connect('tcp://10.41.59.5:5801')
        self.footage_socket.setsockopt(zmq.CONFLATE, 1)
        self.footage_socket.setsockopt(zmq.SUBSCRIBE, b'')

    def run(self):
        while True:
            frame = self.footage_socket.recv()
            source = cv2.imdecode(np.fromstring(frame, dtype=np.uint8), 1)
            cv2.imshow('robot', source)
            cv2.waitKey(1)


if __name__ == '__main__':
    stream_display = StreamDisplay()
    stream_display.run()
