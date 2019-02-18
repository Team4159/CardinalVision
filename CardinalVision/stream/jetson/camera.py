import cv2


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0 and 1.
        self.video0 = cv2.VideoCapture(0)
        self.video1 = cv2.VideoCapture(1)

    def get_frame(self, camera):
        """Reads a frame from the corresponding camera and color maps it to distinguish it.
        :param camera: (int) 0 or 1, depending on which camera to read the frame from.
        :return: jpeg encoded image in a bytestring
        """

        if camera == 0:
            success, image = self.video0.read()
            image = cv2.applyColorMap(image, cv2.COLORMAP_PINK)

        elif camera == 1:
            success, image = self.video1.read()
            image = cv2.applyColorMap(image, cv2.COLORMAP_BONE)

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 25])
        return jpeg.tobytes()
