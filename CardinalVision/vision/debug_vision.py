from CardinalVision.test import get_video
from CardinalVision.vision import Vision
import cv2
import os


class DebugVision:
    def __init__(self, fps, category, name, camera, file):
        self.fps = fps

        if file is not None:
            self.image = cv2.imread(file)

        elif camera is not None:
            self.video = cv2.VideoCapture(camera)

        else:
            self.video = cv2.VideoCapture(get_video(category, name))

    def run(self):
        if getattr(self, 'image', None) is not None:
            frame = Vision.debug_image(self.image)
            cv2.imshow('debug', frame)
            cv2.waitKey(0)

        else:
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
    parser.add_argument('--file', required=False, type=str)
    parser.add_argument('--category', default='deepspace_2019')
    parser.add_argument('--name', default='deepspace_debug_video.mov')
    args = parser.parse_args(sys.argv[1:])

    debug_vision = DebugVision(args.fps, args.category, args.name, args.camera, args.file)
    debug_vision.run()
