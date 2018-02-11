import csv
import glob
import os

import cv2
from flask import Flask, request, render_template, jsonify
from flask import logging

import analysis
import database

app = Flask(__name__)
# When this is True, when you edit this file, the server automatically picks up the changes and refreshes! Wow!
# It will also give you nice error messages if you fuck up
# Turn this to False when your app is done, so hackers can't mess up your cool app!
app.debug = True
logger = logging.getLogger(__name__)

SPREADSHEET = 'results/nematocyst_dimensions.csv'


@app.route('/')
def home():
    return render_template('crop.html')


@app.route('/get-next-image/', methods=['GET'])
def get_next_image():
    path = "static/todo/*.jpg"
    next_file_to_process = find_next_file_to_process(path)
    filename = "static/todo/{}".format(next_file_to_process)
    database.mark_file_as_processed(os.path.basename(filename))
    image = cv2.imread(filename)
    h, w = image.shape[:2]
    json = {"filename": next_file_to_process, 'height': h, 'width': w}
    return jsonify(json)


@app.route('/crop-image', methods=['POST'])
def crop_image():
    crop_info = dict(request.form)
    filename = crop_info['filename'][0]
    x1 = int(float(crop_info['x1'][0]))
    y1 = int(float(crop_info['y1'][0]))
    x2 = int(float(crop_info['x2'][0]))
    y2 = int(float(crop_info['y2'][0]))
    result = analysis.process_image(filename, x1, y1, x2, y2)
    if result is not None:
        width, length = result
        write_to_spreadsheet(filename, length, width)
        json = {
            'status': 'ok',
            "length": str(length),
            "width": str(width),
            "ellipse": '/static/ellipses/{}'.format(os.path.basename(filename).replace('.jpg', '.png')),
            'render': '/static/output/{}'.format(os.path.basename(filename)),
            'normalized': '/static/normalized/{}'.format(os.path.basename(filename)),
            'normalized2': '/static/normalized_ian/{}'.format(os.path.basename(filename)),
            'segmentation': '/static/segmentation/{}'.format(os.path.basename(filename))
        }
        return jsonify(json)
    return jsonify({'status': 'failed'})


def find_next_file_to_process(path):
    for filename in glob.iglob(path):
        basename = os.path.basename(filename)
        processed = database.check_file_processed(basename)
        if processed is None or processed.decode("utf-8") != "processed":
            return basename


def write_to_spreadsheet(filename, length, width):
    length_to_width = (1.0*length)/width
    f = open(SPREADSHEET, "a+")
    row = [[filename, length, width, length_to_width]]

    with f:
        writer = csv.writer(f)
        writer.writerows(row)

    f.close()


if __name__ == '__main__':
    # This starts the server. Just run `python server.py` to start the app.
    app.run()
