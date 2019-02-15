# https://github.com/log0/video_streaming_with_flask_example/blob/master/main.py

from CardinalVision.stream import VideoCamera
from sanic import Sanic
from sanic.response import stream, html
import zmq.asyncio
import asyncio
import time


class StreamServer(Sanic):
    tick_time = 1 / 60  # 60 fps

    def __init__(self, *args, **kwargs):
        Sanic.__init__(self, *args, **kwargs)

        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://127.0.0.1:5803')  # arbitrary
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

        self.camera = 0

        @self.route('/')
        def index(request):
            return html('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Driver Cam</title>
</head>
<body>
    <img id="bg" src="/video_feed" alt="Driver Cam">
</body>
</html>            
            ''')

        @self.route('/video_feed', stream=True)
        def video_feed(request):
            return stream(self.make_stream,
                          content_type='multipart/x-mixed-replace; boundary=frame')

    async def make_stream(self, response):
        camera = VideoCamera()
        last_tick = time.time()
        loop = asyncio.get_event_loop()

        while True:
            frame = await loop.run_in_executor(None, camera.get_frame, self.camera)
            response.write(b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            tmp = time.time()
            if StreamServer.tick_time - (time.time() - last_tick) > 0:
                await asyncio.sleep(StreamServer.tick_time - (time.time() - last_tick))
            last_tick = tmp

    async def read_zmq(self):
        last_tick = time.time()
        last_value = 0
        while True:
            value = int(await self.socket.recv())
            if value and not last_value:
                self.camera = 1 if self.camera == 0 else 0
            last_value = value

            tmp = time.time()
            if StreamServer.tick_time - (time.time() - last_tick) > 0:
                await asyncio.sleep(StreamServer.tick_time - (time.time() - last_tick))
            last_tick = tmp


# Use UDP/TCP ports 5800 - 5810 only. Set debug to False in competition.
# TODO: Set host ip to the Jetson's static IP address
# Go to 0.0.0.0:5801/video_feed for stream only
if __name__ == '__main__':
    app = StreamServer(__name__)
    app.add_task(app.read_zmq())
    app.run(host='0.0.0.0', port='5801', debug=True)
