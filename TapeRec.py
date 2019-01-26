#!/usr/bin/env python3

import numpy as np
import cv2
import math
from enum import Enum
from gripir import GripPipeline

# Self written code
cap = cv2.VideoCapture(1)
eyes = GripPipeline()

class Tape:
    def __init__(self, cnt):
        self.center = None
        self.angle = None
        self.area = None
        self.vertices =  np.int0(cv2.boxPoints(cv2.minAreaRect(cnt)))
        self.sortedVerticesX = []
        self.sortedVerticesY = []
        self.contour = cnt

    # Gets the center of current tape, if current tape's area is 0, return 0,0
    def getCenter(self):
        M = cv2.moments(self.contour)
        if M['m00'] != 0:
            self.center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
            return self.center
        return (0,0)

    # Gets the area bounded by the current tape in pixels
    def getArea(self):
        M = cv2.moments(self.contour)
        self.area = M['m00']
        return self.area

    # Gets the list of vertices of the tape sorted from the left to right in the manner [[x1,y1],[x2,y2]...]
    def getSortedVerticesX(self):
        def x(list):
            return list[1]
        self.sortedVerticesX = list(sorted(self.vertices, key = x))
        return self.sortedVerticesX

    # Gets the list of vertices of the tape sorted from the top to down in the manner [[x1,y1],[x2,y2]...]
    def getSortedVerticesY(self):
        def Y(list):
            return list[1]
        self.sortedVerticesY = sorted(self.vertices, key = Y)
        return self.sortedVerticesY

    # Gets the list of vertices of the tape in the manner [[x1,y1],[x2,y2]...]
    def getVertices(self):
        return self.vertices

    # Getting the parameter needed for the center line through the tape
    def getCenterLine(self, img):
        rows,cols = img.shape[:2]
        [vx,vy,x,y] = cv2.fitLine(self.contour, cv2.DIST_L2,0,0.01,0.01)
        lefty = int((-x*vy/vx) + y)
        righty = int(((cols-x)*vy/vx)+y)
        return [rows, cols, lefty, righty]

    # Getting the coefficient of the linear function represented by the center line of the tape
    def getEquation(self, img):
        rightPt = [self.getCenterLine(img)[1]-1, self.getCenterLine(img)[3]]
        leftPt = [0,self.getCenterLine(img)[2]]
        a = -(self.getCenterLine(img)[3]-self.getCenterLine(img)[2])
        b = self.getCenterLine(img)[1]-1
        c = self.getCenterLine(img)[3]*(self.getCenterLine(img)[1]-1)
        return [a,b,c]
# end of class Tape

# Finds the intercept of the 2 center lines through the two tapes
def findIntercept(tape1, tape2, img):
    y = 0
    if ((tape1.getEquation(img)[0]*tape2.getEquation(img)[1])-(tape1.getEquation(img)[1]*tape2.getEquation(img)[0]))!=0:
        y = ((tape1.getEquation(img)[0]*tape2.getEquation(img)[2])-(tape1.getEquation(img)[2]*tape2.getEquation(img)[0]))/((tape1.getEquation(img)[0]*tape2.getEquation(img)[1])-(tape1.getEquation(img)[1]*tape2.getEquation(img)[0]))
    return y

# Find the center between two tapes
def findCenter(tape1, tape2):
    M1 = cv2.moments(tape1.contour)
    M2 = cv2.moments(tape2.contour)
    if M1['m00'] != 0 and M2['m00'] != 0:
        c1x, c1y = int(M1['m10']/M1['m00']), int(M1['m01']/M1['m00'])
        c2x, c2y = int(M2['m10']/M2['m00']), int(M2['m01']/M2['m00'])
        centerX = int((c1x + c2x)/2)
        centerY = int((c1y + c2y)/2)
        return [centerX, centerY]
    return [0,0]

# Converting the area of the tape into real distance
def findDist(x):
    return (9/2053408)*x**2-(17463/1283380)*x+(5866131/513352)

# Everything in the loop runs framewise
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    uselessThing, shape = cap.read()
    unneeded, boundedImg = cap.read()

    # access the generated code
    eyes.process(frame)

    # initializes variables
    tapeNum = 0
    numOftape = len(eyes.filter_contours_output)
    font = cv2.FONT_HERSHEY_SIMPLEX
    boundedImg = cv2.putText(boundedImg,'# of tapes: '+str(numOftape),(10,12), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    tapes = []
    sortedTapes = []
    groups = []

    # Loops through every tape detected
    for borders in eyes.filter_contours_output:
        num = 0
        tape = Tape(borders)
        tapes.append(tape)
        tapeNum += 1
        boundedImg = cv2.drawContours(boundedImg,[tape.vertices],0,(0,0,255),2)

        # Gets statistics on the tape and display it
        boundedImg = cv2.putText(boundedImg,'Tape#: '+str(tapeNum)+', Center at: '+str(tape.getCenter()[0])+','+str(tape.getCenter()[1]),(tape.vertices[0][0],tape.vertices[0][1]), font, 0.4,(255,255,255),1,cv2.LINE_AA)
        textY = 40
        for rects in tapes:
            num += 1
            boundedImg = cv2.putText(boundedImg,'Tape#: '+str(num)+', Area: '+str(rects.getArea())+', Dist: '+str(findDist(rects.getArea())),(10, textY), font, 0.4,(255,255,255),1,cv2.LINE_AA)
            textY += 10

        # Sorts the tapes seen from the left to right
        def getLeftCorner(list):
            return list.getSortedVerticesX()[0][0]
        sortedTapes = list(sorted(tapes, key = getLeftCorner))

        # Grouping the tapes by checking the intersection of the centerlines and check whether above or below the center of tape
        for tape_1 in sortedTapes:
            for tape_2 in sortedTapes:
                if tape_1 != tape_2:
                    if (tape_1.getCenter()!=tape_2.getCenter()) and findIntercept(tape_1, tape_2, boundedImg) < findCenter(tape_1, tape_2)[1] :
                        groups.append([tape_1, tape_2])
                        sortedTapes.remove(tape_1)
                        sortedTapes.remove(tape_2)
                        break
        # Draws a bounding rectangle over the grouped tapes
        for target in groups:
            boundedImg =  cv2.rectangle(boundedImg,(target[0].getSortedVerticesX()[2][0],target[0].getSortedVerticesX()[0][1]),(target[1].getSortedVerticesY()[2][0],target[1].getSortedVerticesY()[3][1]),(0,255,0),3)

    # multiple image to compare effect
    cv2.imshow('frame',frame)
    cv2.imshow('frame2',shape)
    cv2.imshow('frame3',boundedImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
