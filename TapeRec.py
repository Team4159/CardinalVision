#!/usr/bin/env python3

import numpy as np
import cv2
import math
from enum import Enum
from gripir import GripPipeline
from tape import Tape
from group import Group
import zmq
import time

# Setting up ZMQ
# context = zmq.Context(1)
# socket = context.socket(zmq.PAIR)
# socket.bind("tcp://localhost:5555" )

# Self written code
cap = cv2.VideoCapture(0)
eyes = GripPipeline()

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
    return -0.042495 * x + 6.97107
    # return (9/2053408)*x**2-(17463/1283380)*x+(5866131/513352)




# Everything in the loop runs framewise
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # uselessThing, shape = cap.read()
    unneeded, boundedImg = cap.read()
    height, width = boundedImg.shape[:2]
    center = [height/2, width/2]

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
    groups_for_calc = []
    sortedTarget = []
    groupTargeted = None

    # Loops through every tape detected
    for borders in eyes.filter_contours_output:
        num = 0
        tape = Tape(borders)
        tapes.append(tape)
        tapeNum += 1
        boundedImg = cv2.drawContours(boundedImg,[tape.vertices],0,(0,0,255),2)



        # Sorts the tapes seen from the left to right
        def getLeftCorner(list):
            return list.getSortedVerticesX()[0][0]
        sortedTapes = list(sorted(tapes, key = getLeftCorner))

        # Grouping the tapes by checking the intersection of the centerlines and check whether above or below the center of tape
        for tape_1 in sortedTapes:
            for tape_2 in sortedTapes:
                if tape_1 != tape_2:
                    if (tape_1.getCenter()!=tape_2.getCenter()) and findIntercept(tape_1, tape_2, boundedImg) < findCenter(tape_1, tape_2)[1] :
                        group = Group(tape_1, tape_2)
                        groups_for_calc.append(group)
                        groups.append([tape_1, tape_2])
                        sortedTapes.remove(tape_1)
                        sortedTapes.remove(tape_2)
                        break
        if len(groups_for_calc) > 0:
            groupTargeted = max(groups_for_calc, key = lambda group: group.getGroupArea())
            groupTargeted.targeted = True

            offsetAngle = ((groupTargeted.getCenter()[0]-center[0])*75)/width
            dist = (findDist(groupTargeted.tapeL.getHeight())+findDist(groupTargeted.tapeR.getHeight()))/2

# ##################### Visuals #####################

        # Gets statistics on the tape and display it
        boundedImg = cv2.putText(boundedImg,'Tape#: '+str(tapeNum)+', Center at: '+str(tape.getCenter()[0])+','+str(tape.getCenter()[1]),(tape.vertices[0][0],tape.vertices[0][1]), font, 0.4,(255,255,255),1,cv2.LINE_AA)
        textY = 40
        for rects in tapes:
            num += 1
            boundedImg = cv2.putText(boundedImg,'Tape#: '+str(num)+', Area: '+str(rects.getArea())+', Dist: '+str(findDist(rects.getHeight())),(10, textY), font, 0.4,(255,255,255),1,cv2.LINE_AA)
            textY += 10




        # Draws a bounding rectangle over the grouped tapes, the color of the targeted group has a different color
        for target in groups_for_calc:
            if target.targeted:
                boundedImg =  cv2.rectangle(boundedImg,(target.tapeL.getSortedVerticesX()[2][0],target.tapeL.getSortedVerticesX()[0][1]),(target.tapeR.getSortedVerticesY()[2][0],target.tapeR.getSortedVerticesY()[3][1]),(255,255,0),3)
                boundedImg = cv2.putText(boundedImg,'offset: '+str(offsetAngle)+', Dist: '+str(dist),(10,20), font, 0.4,(255,255,255),1,cv2.LINE_AA)

            else:
                boundedImg =  cv2.rectangle(boundedImg,(target.tapeL.getSortedVerticesX()[2][0],target.tapeL.getSortedVerticesX()[0][1]),(target.tapeR.getSortedVerticesY()[2][0],target.tapeR.getSortedVerticesY()[3][1]),(0,255,0),3)


    # multiple image to compare effect
    # cv2.imshow('frame',frame)
    # cv2.imshow('frame2',shape)
    cv2.imshow('frame3',boundedImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
