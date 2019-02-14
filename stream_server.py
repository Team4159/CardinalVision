# https://github.com/log0/video_streaming_with_flask_example/blob/master/main.py

from sanic import Sanic
from sanic.response import stream, html
from camera import VideoCamera
import zmq.asyncio
import asyncio

import time


class StreamServer(Sanic):
    def __init__(self, *args, **kwargs):
        Sanic.__init__(self, *args, **kwargs)

        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://127.0.0.1:5803')  # arbitrary
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

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
        tick_time = 1 / 60  # 60 fps
        last_tick = time.time()
        loop = asyncio.get_event_loop()

        while True:
            tmp = time.time()
            if tick_time - (time.time() - last_tick) > 0:
                await asyncio.sleep(tick_time - (time.time() - last_tick))
            last_tick = tmp

            frame = await loop.run_in_executor(None, camera.get_frame, 0)
            response.write(b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Use UDP/TCP ports 5800 - 5810 only. Set debug to False in competition.
# TODO: Set host ip to the Jetson's static IP address
# Go to 0.0.0.0:5801/video_feed for stream only
if __name__ == '__main__':
    app = StreamServer(__name__)
    app.run(host='0.0.0.0', port='5801', debug=True)
