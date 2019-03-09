import cv2
import numpy as np


class Vision:
    # Define range of threshold in HSV. Tip: Get these values from generated GRIP code.
    lower_range = np.array([0.0, 0.0, 255.0])
    upper_range = np.array([0.0, 0.0, 255.0])

    min_area = 500

    @staticmethod
    def process_image(image, debug=False):
        """Identifies all reflective tapes and determines our error from the largest one.
        :param image: Image to identify tapes on.
        :param debug: Whether or not to draw bounding boxes and return bounded image
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

        grouped = []

        processed_contours = Vision.sort_left_to_right(Vision.filter_area(contours))

        # Loop through each contour(tape) with an index, sorted and filtered
        for idx, tape in enumerate(processed_contours[:-1]):
            if idx in grouped:
                continue

            # Get the current indexed contour and next index contour in the list
            left_tape = processed_contours[idx]
            right_tape = processed_contours[idx + 1]

            left_slope = Vision.slope(left_tape)
            right_slope = Vision.slope(right_tape)

            # Compare slopes and run
            if left_slope > 0 > right_slope:
                # Bound a rectangle on the two contours and get the (x,y) of the top left coordinate and the rectangle's width and height
                xL, yL, wL, hL = cv2.boundingRect(left_tape)
                xR, yR, wR, hR = cv2.boundingRect(right_tape)

                # Assign x, y, width, and height to a tuple that represents a rectangle
                left_rect = (xL, yL, wL, hL)
                right_rect = (xR, yR, wR, hR)

                # Combine the two rectangles by computing its union (creating a bounding box around the two pieces of tape)
                combined_rect = Vision.union(left_rect, right_rect)

                if debug:
                    x, y, w, h = combined_rect
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Add combined_rect to the list of bounding_boxes
                bounding_boxes.append(combined_rect)

                grouped.append(idx)
                grouped.append(idx + 1)

        if debug:
            for contour in processed_contours:
                cv2.drawContours(image, [np.int0(cv2.boxPoints(cv2.minAreaRect(contour)))], 0, (0, 0, 255), 2)

        # Loop through each bounding box and compute which has the largest area
        if bounding_boxes:
            largest_bounding_box = max(bounding_boxes, key=lambda rect: rect[2] * rect[3])
            x_value_to_align_to = largest_bounding_box[0] + largest_bounding_box[2] / 2
            error = (x_value_to_align_to - (cols / 2)) / (cols / 2)  # error scaled down to -1 to 1

            return error if not debug else image

        return None if not debug else image

    @staticmethod
    def slope(cnt):
        """Finds two points on a line fitted to a contour
        :param cnt: Contour to fit line to.
        :return: Slope of the line
        """
        vx, vy, x0, y0 = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
        return vy / vx

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
