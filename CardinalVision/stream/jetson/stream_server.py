# https://github.com/log0/video_streaming_with_flask_example/blob/master/main.py

from CardinalVision.stream.jetson import VideoCamera
import zmq.asyncio
import asyncio


class StreamServer:
    def __init__(self):
        self.camera = VideoCamera()
        self.camera_port = 0

        self.context = zmq.asyncio.Context()

        self.control_socket = self.context.socket(zmq.SUB)
        self.control_socket.connect('tcp://127.0.0.1:5803')
        self.control_socket.setsockopt(zmq.SUBSCRIBE, b'')

        self.footage_socket = self.context.socket(zmq.PUB)
        self.footage_socket.bind('tcp://127.0.0.1:5801')

    async def read_control_socket(self):
        last_value = 0
        while True:
            value = int(await self.control_socket.recv())
            if value and not last_value:
                self.camera ^= 1  # my brain expands every day
            last_value = value

    async def send_footage(self):
        while True:
            frame = self.camera.get_frame(self.camera_port)
            await self.footage_socket.send(frame)
            await asyncio.sleep(0)  # yield control to self.read_control_socket

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.read_control_socket())
        loop.run_until_complete(self.send_footage())


# Use UDP/TCP ports 5800 - 5810 only.
# TODO: Set host ip to the Jetson's static IP address
if __name__ == '__main__':
    stream_server = StreamServer()
    stream_server.run()
