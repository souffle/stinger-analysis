import cv2
import glob
import os

if __name__ == '__main__':
    for filename in glob.glob("/home/tommychen/Keys/cleaned/*.tif"):
        print filename
        image = cv2.imread(filename)
        basename = os.path.basename(filename).replace('.tif', '.jpg')
        cv2.imwrite("static/todo/{}".format(basename), image)
