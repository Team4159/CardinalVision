import numpy as np
import cv2
import math
from enum import Enum
from gripir import GripPipeline
from networktables import NetworkTables
from tape import Tape

class Group:
    def __init__(self, tapeA, tapeB):
        self.tapeL = tapeA
        self.tapeR = tapeB
        self.center = None
        self.area = None
        self.leftTilt = False
        self.rightTilt = False
        self.noTilt = False
        self.targeted = False

    def getCenter(self):
        M1 = cv2.moments(self.tapeL.contour)
        M2 = cv2.moments(self.tapeR.contour)
        if M1['m00'] != 0 and M2['m00'] != 0:
            c1x, c1y = int(M1['m10']/M1['m00']), int(M1['m01']/M1['m00'])
            c2x, c2y = int(M2['m10']/M2['m00']), int(M2['m01']/M2['m00'])
            centerX = int((c1x + c2x)/2)
            centerY = int((c1y + c2y)/2)
            self.center = [centerX, centerY]
            return self.center
        return [0,0]

    def getGroupArea(self):
        self.area = self.tapeL.getArea()+self.tapeR.getArea()
        return self.area

    def checkTilt(self):
        if(int(round(self.tapeL.getArea(), -2)) > int(round(self.tapeR.getArea(), -2))):
            self.leftTilt = False
            self.rightTilt = True
            self.noTilt = False
        elif(int(round(self.tapeL.getArea(), -2)) < int(round(self.tapeR.getArea(), -2))):
            self.leftTilt = True
            self.rightTilt = False
            self.noTilt = False
        else:
            self.leftTilt = True
            self.rightTilt = False
            self.noTilt = False
