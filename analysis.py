import cv2
import glob
import numpy as np
import os
import ellipseEdgeDetect as elps

CANVAS_DIAMETER = 1000
STANDARD_SIZE = 10000
STANDARD_WIDTH = 350
STANDARD_HEIGHT = 75
STANDARD_VALUE = 150


def process_image(filename, x1, y1, x2, y2):
    filename = filename.strip('/')
    basename = os.path.basename(filename)
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    if image is not None:
        # image = normalize_brightness(image)
        cropped = image[y1:y2, x1:x2]
        print cropped.shape
        grayscale = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        try:
            center_x, center_y, scale, orientation = elps.file2ellipse(grayscale, basename, plot=True)
            normalized_ian = normalize_ian_orientation(cropped, center_x, center_y, -orientation, scale)
        except:
            normalized_ian = cropped
        fallback = find_contour(grayscale)
        preferred = find_contour_v2(cropped)
        contour = preferred if preferred is not None else fallback
        box = find_bounding_box(contour)
        width, length = find_width_and_length(box)
        center_x, center_y, orientation, scale = find_center_and_orientation(contour)
        normalized = normalize_orientation(cropped, center_x, center_y, orientation, scale)
        cv2.imwrite("static/normalized/{}".format(basename), normalized)
        cv2.imwrite("static/normalized_ian/{}".format(basename), normalized_ian)
        demo = render_boundaries(cropped, contour, box)
        cv2.imwrite("static/output/{}".format(basename), demo)
        segmentation = find_mask(cropped)
        cv2.imwrite("static/segmentation/{}".format(basename), segmentation)
        return width, length


def normalize_brightness(image):
    avg_brightness = np.mean(image)
    factor = STANDARD_VALUE / avg_brightness
    return (image * factor).astype(np.uint8)


def find_contour(image):
    edges = cv2.Canny(image, 50, 75)
    dilated = cv2.dilate(edges, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    eroded = cv2.erode(dilated, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    _, contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    if len(contours) > 0:
        return max(contours, key=lambda contour: cv2.contourArea(contour))
    return None


def find_mask(image):
    h, w = image.shape[:2]
    mask = np.zeros(image.shape[:2], np.uint8)
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    rect = (10, 10, w - 20, h - 20)
    result, _, _ = cv2.grabCut(image, mask, rect, background, foreground, 5, cv2.GC_INIT_WITH_RECT)
    response_map = np.zeros(image.shape[:2], dtype=np.uint8)
    response_map[result == 3] = 255
    response_map[result == 1] = 255
    return response_map


def find_contour_v2(image):
    mask = find_mask(image)
    eroded = cv2.erode(mask, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    dilated = cv2.dilate(eroded, kernel=np.ones((3, 3), dtype=np.uint8), iterations=2)
    _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
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


def normalize_ian_orientation(image, center_x, center_y, orientation, scale):
    canvas_radius = CANVAS_DIAMETER / 2
    translation = np.float32([[1, 0, canvas_radius-center_x], [0, 1, canvas_radius-center_y]])
    translated = cv2.warpAffine(image, translation, (CANVAS_DIAMETER, CANVAS_DIAMETER))
    rotation_matrix = cv2.getRotationMatrix2D((canvas_radius, canvas_radius), orientation-90, scale=scale)
    canvas_result = cv2.warpAffine(translated, rotation_matrix, (CANVAS_DIAMETER, CANVAS_DIAMETER))
    height_offset = int(STANDARD_HEIGHT/2)
    width_offset = int(STANDARD_WIDTH/2)
    cropped = canvas_result[canvas_radius-height_offset:canvas_radius+height_offset,
                            canvas_radius-width_offset:canvas_radius+width_offset]
    return cropped


def find_center_and_orientation(contour):
    moments = cv2.moments(contour)
    center_x = float(moments["m10"]) / moments["m00"]
    center_y = float(moments["m01"]) / moments["m00"]
    _, _, orientation = cv2.fitEllipse(contour)
    box = find_bounding_box(contour)
    width, height = find_width_and_length(box)
    scale = np.sqrt(float(STANDARD_SIZE) / float(width * height))
    return center_x, center_y, orientation, scale


def normalize_orientation(image, center_x, center_y, orientation, scale):
    canvas_radius = CANVAS_DIAMETER / 2
    translation = np.float32([[1, 0, canvas_radius-center_x], [0, 1, canvas_radius-center_y]])
    translated = cv2.warpAffine(image, translation, (CANVAS_DIAMETER, CANVAS_DIAMETER))
    rotation_matrix = cv2.getRotationMatrix2D((canvas_radius, canvas_radius), orientation-90, scale=scale)
    canvas_result = cv2.warpAffine(translated, rotation_matrix, (CANVAS_DIAMETER, CANVAS_DIAMETER))
    height_offset = int(STANDARD_HEIGHT/2)
    width_offset = int(STANDARD_WIDTH/2)
    cropped = canvas_result[canvas_radius-height_offset:canvas_radius+height_offset,
                            canvas_radius-width_offset:canvas_radius+width_offset]
    return cropped


def render_boundaries(image, contour, box):
    result = cv2.drawContours(np.copy(image), [np.int0(box)], 0, (0, 0, 255), 2)
    # result = cv2.drawContours(result, [np.int0(contour)], 0, (0, 255, 0), 1)
    return result


def main():
    for filename in glob.glob("data/*"):
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # image = normalize_brightness(image)
        contour = find_contour(image)
        box = find_bounding_box(contour)
        width, height = find_width_and_length(box)
        print float(height) / width
        center_x, center_y, orientation, scale = find_center_and_orientation(contour)
        normalized = normalize_orientation(image, center_x, center_y, orientation, scale)
        # Render box
        color_image = cv2.imread(filename, cv2.IMREAD_COLOR)
        result = cv2.drawContours(color_image, [np.int0(box)], 0, (0, 0, 255), 2)
        result = cv2.drawContours(result, [np.int0(contour)], 0, (0, 255, 0), 1)
        cv2.imshow('1', image)
        cv2.imshow('5', normalized)
        cv2.imshow('6', result)
        cv2.waitKey()


def test_full_process():
    print process_image("uncropped.jpg", 500, 300, 800, 450)


if __name__ == '__main__':
    main()
