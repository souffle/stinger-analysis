import cv2
import numpy as np
import glob

for filename in glob.glob("static/data/*.jpg"):
    img = cv2.imread(filename)
    cv2.imshow('2', img)
    h, w = img.shape[:2]
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (10, 10, w-20, h-20)
    result, _, _ = cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    print result.dtype

    response = np.zeros(img.shape, dtype=np.uint8)
    response[result==3] = 255
    cv2.imshow('1', response)
    cv2.waitKey()