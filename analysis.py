import cv2
import numpy as np


def find_contour(image):
    edges = cv2.Canny(image, 50, 75)
    dilated = cv2.dilate(edges, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    eroded = cv2.erode(dilated, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    _, contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    if len(contours) > 0:
        return max(contours, key=lambda contour: cv2.contourArea(contour))
    return None


def find_bounding_box(contour):
    bounding_box = cv2.minAreaRect(contour)
    corners = cv2.boxPoints(bounding_box)
    return corners


def find_width_and_length(box):
    a, b, c, d = box
    side1 = np.linalg.norm(a - b)
    side2 = np.linalg.norm(b - c)
    width = min(side1, side2)
    height = max(side1, side2)
    return width, height


if __name__ == '__main__':
    image = cv2.imread("data/cropped.jpg", cv2.IMREAD_GRAYSCALE)
    contour = find_contour(image)
    box = find_bounding_box(contour)
    width, height = find_width_and_length(box)
    print width, height
    # Render box
    color_image = cv2.imread("data/cropped.jpg", cv2.IMREAD_COLOR)
    result = cv2.drawContours(color_image, [np.int0(box)], 0, (0, 0, 255), 2)
    cv2.imshow('1', result)
    cv2.waitKey()
