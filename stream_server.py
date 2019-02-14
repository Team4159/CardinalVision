# https://github.com/log0/video_streaming_with_flask_example/blob/master/main.py

from flask import Flask, render_template, Response
from camera import VideoCamera

import time


class StreamServer(Flask):
    def __init__(self, *args, **kwargs):
        # looping
        self.last_tick = time.time()
        self.tick_time = 1 / 60  # 60 fps

        Flask.__init__(self, *args, **kwargs)

        @self.route('/')
        def index():
            return render_template('index.html')

        @self.route('/video_feed')
        def video_feed():
            return Response(self.make_stream(VideoCamera()),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

    def make_stream(self, camera):
        while True:
            tmp = time.time()
            if self.tick_time - (time.time() - self.last_tick) > 0:
                time.sleep(self.tick_time - (time.time() - self.last_tick))
            self.last_tick = tmp

            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# Use UDP/TCP ports 5800 - 5810 only. Set debug to False in competition.
# TODO: Set host ip to the Jetson's static IP address
# Go to 0.0.0.0:5801/video_feed for stream only
if __name__ == '__main__':
    app = StreamServer(__name__)
    app.run(host='0.0.0.0', port='5801', debug=True)
