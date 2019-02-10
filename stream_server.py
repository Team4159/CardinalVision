# https://github.com/log0/video_streaming_with_flask_example/blob/master/main.py

from flask import Flask, render_template, Response
from camera import VideoCamera

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Use UDP/TCP ports 5800 - 5810 only. Set debug to False in competition.
# TODO: Set host ip to the Jetson's static IP address
# Go to 0.0.0.0:5801/video_feed for stream only
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5801', debug=True)
