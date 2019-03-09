import cv2
import numpy as np


class Vision:
    # Define range of threshold in HSV. Tip: Get these values from generated GRIP code.
    lower_range = np.array([0.0, 0.0, 255.0])
    upper_range = np.array([0.0, 0.0, 255.0])

    min_area = 500

    @staticmethod
    def process_image(image):
        """Identifies all reflective tapes and determines our error from the largest one.
        :param image: Image to identify tapes on.
        :return: Error in pixels that the camera has from the tape.
        """
        rows, cols = image.shape[:2]

        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Threshold HSV to only get white target
        mask = cv2.inRange(hsv, Vision.lower_range, Vision.upper_range)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        bounding_boxes = []

        # Loop through each contour(tape) with an index, sorted and filtered
        for idx, tape in enumerate(Vision.sort_left_to_right(Vision.filter_area(contours[:-1]))):
            # Get the current indexed contour and next index contour in the list
            left_tape = contours[idx]
            right_tape = contours[idx + 1]

            # Fit each contour to a line and get two points from each line
            x1, y1, x2, y2 = Vision.fit_line(left_tape)
            x3, y3, x4, y4 = Vision.fit_line(right_tape)

            left_slope = (y2 - y1) / (x2 - x1)
            right_slope = (y4 - y3) / (x4 - x3)

            # Compare slopes and run
            if left_slope < 0 < right_slope:
                # Bound a rectangle on the two contours and get the (x,y) of the top left coordinate and the rectangle's width and height
                xL, yL, wL, hL = cv2.boundingRect(left_tape)
                xR, yR, wR, hR = cv2.boundingRect(right_tape)

                # Assign x, y, width, and height to a tuple that represents a rectangle
                left_rect = (xL, yL, wL, hL)
                right_rect = (xR, yR, wR, hR)

                # Combine the two rectangles by computing its union (creating a bounding box around the two pieces of tape)
                combined_rect = Vision.union(left_rect, right_rect)

                # Add combined_rect to the list of bounding_boxes
                bounding_boxes.append(combined_rect)

                contours.pop(idx + 1)

        # Loop through each bounding box and compute which has the largest area
        if bounding_boxes:
            largest_bounding_box = max(bounding_boxes, key=lambda rect: rect[2] * rect[3])
            x_value_to_align_to = largest_bounding_box[0] + largest_bounding_box[2] / 2
            error = (x_value_to_align_to - (cols / 2)) / (cols / 2)  # error scaled down to -1 to 1

            return error

        return None

    @staticmethod
    def fit_line(cnt):
        """Finds two points on a line fitted to a contour
        :param cnt: Contour to fit line to.
        :return: Two points on the line as a tuple: (x0, y0, x1, y1)
        """
        vx, vy, x0, y0 = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
        x1, y1 = np.array([x0, y0]) + (100 * np.array([vx, vy]))
        return x0, y0, x1.item(), y1.item()

    @staticmethod
    def filter_area(contours):
        return filter(lambda contour: cv2.contourArea(contour) > Vision.min_area, contours)

    @staticmethod
    def sort_left_to_right(contours):
        """
        :param contours: Contours to sort.
        :return: Contours sorted from left to right.
        """
        return sorted(contours, key=lambda contour: cv2.boundingRect(contour)[0], reverse=True)

    @staticmethod
    def union(a, b):
        """Creates a larger rectangle containing two smaller ones
        :param a: First rectangle as a tuple: (x, y, w, h)
        :param b: Second rectangle as a tuple: (x, y, w, h)
        :return: Larger rectangle containing both smaller rectangles as a tuple: (x, y, w, h)
        """
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0] + a[2], b[0] + b[2]) - x
        h = max(a[1] + a[3], b[1] + b[3]) - y
        return x, y, w, h
