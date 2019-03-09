from CardinalVision.test import get_video
from CardinalVision.vision import Vision
import cv2


class DebugVision:
    def __init__(self, fps, category, name, camera):
        self.fps = fps

        if camera is not None:
            self.video = cv2.VideoCapture(camera)

        else:
            self.video = cv2.VideoCapture(get_video(category, name))

    def run(self):
        while self.video.isOpened():
            ret, frame = self.video.read()

            if frame is None:
                break

            frame = Vision.debug_image(frame)

            cv2.imshow('debug', frame)

            if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--fps', default=10, type=int)
    parser.add_argument('--camera', required=False, type=int)
    parser.add_argument('--category', default='deepspace_2019')
    parser.add_argument('--name', default='deepspace_debug_video.mov')
    args = parser.parse_args(sys.argv[1:])

    debug_vision = DebugVision(args.fps, args.category, args.name, args.camera)
    debug_vision.run()
