import glob

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

# This is a janky and bad way to store data for our app.
# In reality, we would use a nice database like Redis, Postgres, MySQL, MongoDB, whatever...
memory = {'fave': 'placeholder'}


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-next-image/', methods=['GET'])
def get_next_image():
    path = "data/*.tif"
    next_file_to_process = find_next_file_to_process(path)
    json = {"filename": next_file_to_process}
    return jsonify(json)

@app.route('/crop-image/', methods=['POST'])
def crop_image():
    crop_info = dict(request.form)
    filename = crop_info['filename']
    x1 = crop_info['x1']
    y1 = crop_info['y1']
    x2 = crop_info['x2']
    y2 = crop_info['y2']
    length, width = analysis.process_image(filename, x1, y1, x2, y2)
    # TODO: write length, width, ratio to spreadsheet
    json = {
        "length": length,
        "width": width
    }
    return jsonify(json)

def find_next_file_to_process(path):
    for file in glob.iglob(path):
        filename = file.split("/")[1]
        processed = database.check_file_processed(filename)
        if processed is None or processed.decode("utf-8") != "processed":
            return filename


if __name__ == '__main__':
    # This starts the server. Just run `python server.py` to start the app.
    app.run()
