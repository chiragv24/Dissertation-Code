
from imutils import paths
import numpy as np
import imutils
import cv2
import time
import cozmo


# def findMarker():
# #def findMarker(robot:cozmo.robot.Robot):
#     #robot.camera.image_stream_enabled = True
#     #image = robot.world.latest_image
#     # greyScale = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#     # greyScale = cv2.GaussianBlur(greyScale,(5,5),0)
#     # edges = cv2.Canny(greyScale,35,125)
#     # contours = cv2.findContours(edges.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
#     # contours = imutils.grab_contours(contours)
#     # c = max(contours,key = cv2.contourArea)
#     # return cv2.minAreaRect(c)
#     image = cv2.imread("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Individual Code Tests/chirag.jpg")
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
#     edged = cv2.Canny(gray, 35, 125)
#
# # find the contours in the edged image and keep the largest one;
# # we'll assume that this is our piece of paper in the image
# #     cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# #     cnts = imutils.grab_contours(cnts)
# #     c = max(cnts, key=cv2.contourArea)
#
# # compute the bounding box of the of the paper region and return it
#     #return cv2.minAreaRect(c)
#
# findMarker()
#cozmo.run_program(findMarker,use_viewer=True)

def findMarker():
    image = cv2.imread("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Individual Code Tests/General-Electric-GE-logo-880x660.png")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    cv2.imshow("image", image)
    cv2.waitKey(0)
    return cv2.minAreaRect(c)

findMarker()


    # def distance_to_camera(knownWidth, focalLength, perWidth):
#     # compute and return the distance from the maker to the camera
# 	return (knownWidth * focalLength) / perWidth
#
# KNOWN_DISTANCE = 24.0
# KNOWN_WIDTH = 11.0
# image = cv2.imread("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Individual Code Tests/chirag.jpg")
# marker = findMarker(image)
# focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH
#
# # for imagePath in sorted(paths.list_images("images")):
# #     # load the image, find the marker in the image, then compute the
# #     # distance to the marker from the camera
# # image = cv2.imread(imagePath)
# marker = findMarker(image)
# inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
#
#     # draw a bounding box around the image and display it
# box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
# box = np.int0(box)
# cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
# cv2.putText(image, "%.2fft" % (inches / 12),
# (image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,2.0, (0, 255, 0), 3)
# cv2.imshow("image", image)
# cv2.waitKey(0)