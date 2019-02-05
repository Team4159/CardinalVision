import cv2
import numpy as np

import zmq
import time
import struct

# Takes a contour and fits a line to it. Returns 2 points on that line.
def fitLine(cnt):
    _, cols = frame.shape[:2]
    [vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((cols - x) * vy / vx) + y)
    x0 = cols - 1
    y0 = righty
    x1 = 0
    y1 = lefty
    return x0, y0, x1, y1


# Takes a list of contours and returns it sorted from left to right
def sortLeftToRight(cnts):
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b:b[1][0], reverse=False))
    return cnts


# Takes two rectangles as tuples (x, y, w, h) and returns a larger rectangle tuple that encompasses both of them
def union(a, b):
    x = min(a[0], b[0])
    y = min(a[1], b[1])
    w = max(a[0] + a[2], b[0] + b[2]) - x
    h = max(a[1] + a[3], b[1] + b[3]) - y
    return x, y, w, h


# Define range of threshold in HSV. Tip: Get these values from generated GRIP code.
lower_range = np.array([0.0, 0.0, 255.0])
upper_range = np.array([0.0, 0.0, 255.0])

last_tick = time.time()
tick_time = 0.1  # arbitrary, tune for with live camera and zmq
camera = 0  # change default camera

# cap = cv2.VideoCapture(camera)
# cap.set(3, 320) theoretically you can set the camera properties
# cap.set(4, 240)

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind('tcp://127.0.0.1:5555')  # arbitrary

while True:
    # data = socket.recv()
    # switchCamera = struct.unpack('b', data)
    # if switchCamera:
    #     camera = 0 if camera == 1 else 1
    #     cap = cv2.VideoCapture(camera)

    # _, frame = cap.read()

    # For testing purposes we will process on a still image
    frame = cv2.imread('test2.png')

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold HSV to only get white target
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Sort contours from left to right
    contours = sortLeftToRight(contours)

    # Initialize a variable to store all bounding boxes in a list
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

            # Calculate the centeroid y coordinates of the two contours
            leftY = int(leftM['m01'] / leftM['m00'])
            rightY = int(rightM['m01'] / rightM['m00'])

            # Fit each contour to a line and get two points from each line
            x1, y1, x2, y2 = fitLine(leftTape)
            x3, y3, x4, y4 = fitLine(rightTape)

            # Compute the y coordinate of the intersection point of the two lines
            intersectY = y1 + ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)) * (y2-y1)

            # Run if the intersection of the two lines are higher than the contours (the two pieces of tape are angled towards each other)
            # TODO: Might be a better idea to compare the slopes of the two lines (positive or negative)
            # because there are actually some extreme cases where the intersect point is lower than one of the tape's y coordinate even though they are meant to be grouped together
            if(intersectY < rightY or intersectY < leftY):

                # Bound a rectangle on the two contours and get the (x,y) of the top left coordinate and the rectangle's width and height
                xL, yL, wL, hL = cv2.boundingRect(leftTape)
                xR, yR, wR, hR = cv2.boundingRect(rightTape)

                # Assign x, y, width, and height to a tuple that represents a rectangle
                leftRect = (xL, yL, wL, hL)
                rightRect = (xR, yR, wR, hR)

                # Combine the two rectangles by computing its union (creating a bounding box around the two pieces of tape)
                combinedRect = union(leftRect, rightRect)

                # Add combinedRect to the list of boundingBoxes
                boundingBoxes.append(combinedRect)

                # Draw the bounding box to the frame
                frame = cv2.rectangle(frame, (combinedRect[0], combinedRect[1]), (combinedRect[0] + combinedRect[2], combinedRect[1] + combinedRect[3]), (0, 255 ,0), 3)

    # Loop through each bounding box and compute which has the largest area
    if boundingBoxes:

        largestBoundingBox = boundingBoxes[0]
        largestArea = 0

        for rect in boundingBoxes:

            area = rect[2] * rect[3]

            if (area > largestArea):
                largestArea = area
                largestBoundingBox = rect

        xValueToAlignTo = largestBoundingBox[0] + largestBoundingBox[2] / 2
        # print(xValueToAlignTo)

        # socket.send(struct.pack('d', xValueToAlignTo))

    # Display the frame
    cv2.imshow("Frame", frame)

    # Exit program if any key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    tmp = time.time()
    if tick_time - (time.time() - last_tick) > 0:
        time.sleep(tick_time - (time.time() - last_tick))
    last_tick = tmp


# When everything done, release the capture
# cap.release()
cv2.destroyAllWindows()
