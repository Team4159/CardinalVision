import cv2
import numpy as np


class Vision:
    # Define range of threshold in HSV. Tip: Get these values from generated GRIP code.
    lower_range = np.array([0.0, 0.0, 255.0])
    upper_range = np.array([0.0, 0.0, 255.0])

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

        # Sort contours from left to right
        contours = Vision.sort_left_to_right(contours)

        boundingBoxes = []

        # Loop through each contour(tape) with an index
        for idx, tape in enumerate(contours):
            # Only loop until second to last contour
            if idx < len(contours) - 1:
                # Get the current indexed contour and next index contour in the list
                leftTape = contours[idx]
                rightTape = contours[idx + 1]

                # Get the Moment objects of the two contours
                leftM = cv2.moments(leftTape)
                rightM = cv2.moments(rightTape)

                # skip if either contour has an area of 0
                if leftM['m00'] == 0 or rightM['m00'] == 0:
                    continue

                # Calculate the centeroid y coordinates of the two contours
                leftY = int(leftM['m01'] / leftM['m00'])
                rightY = int(rightM['m01'] / rightM['m00'])

                # Fit each contour to a line and get two points from each line
                x1, y1, x2, y2 = Vision.fit_line(leftTape)
                x3, y3, x4, y4 = Vision.fit_line(rightTape)

                # Compute the y coordinate of the intersection point of the two lines
                intersectY = y1 + ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / (
                            (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)) * (y2 - y1)

                # Run if the intersection of the two lines are higher than the contours (the two pieces of tape are angled towards each other)
                # TODO: Might be a better idea to compare the slopes of the two lines (positive or negative)
                # because there are actually some extreme cases where the intersect point is lower than one of the tape's y coordinate even though they are meant to be grouped together
                if intersectY < rightY or intersectY < leftY:
                    # Bound a rectangle on the two contours and get the (x,y) of the top left coordinate and the rectangle's width and height
                    xL, yL, wL, hL = cv2.boundingRect(leftTape)
                    xR, yR, wR, hR = cv2.boundingRect(rightTape)

                    # Assign x, y, width, and height to a tuple that represents a rectangle
                    leftRect = (xL, yL, wL, hL)
                    rightRect = (xR, yR, wR, hR)

                    # Combine the two rectangles by computing its union (creating a bounding box around the two pieces of tape)
                    combinedRect = Vision.union(leftRect, rightRect)

                    # Add combinedRect to the list of boundingBoxes
                    boundingBoxes.append(combinedRect)

        # Loop through each bounding box and compute which has the largest area
        if boundingBoxes:
            largestBoundingBox = max(boundingBoxes, key=lambda rect: rect[2] * rect[3])
            xValueToAlignTo = largestBoundingBox[0] + largestBoundingBox[2] / 2
            error = (xValueToAlignTo - (cols / 2)) / (cols / 2)  # error scaled down to -1 to 1

            return error

        else:
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
    def sort_left_to_right(contours):
        """
        :param contours: Contours to sort.
        :return: Contours sorted from left to right.
        """
        if len(contours) >= 2:
            contours, _ = zip(*sorted(zip(contours, (cv2.boundingRect(c) for c in contours)), key=lambda b: b[1][0], reverse=False))
        return contours

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
