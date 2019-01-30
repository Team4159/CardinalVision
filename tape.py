import numpy as np
import cv2
import math
from enum import Enum
from gripir import GripPipeline

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
