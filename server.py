import glob

from flask import Flask, request, render_template, jsonify
from flask import logging

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
    path = "data/"
    file_iterator = glob.iglob(path)
    processed = True
    filename = None

    while processed:
        try:
            filename = file_iterator.next()
        except StopIteration:
            logger.info("No more images to process.")
            return None
        processed = database.check_file_processed(filename)
    return "/data/{}".format(filename)

@app.route('/crop-image/', methods=['POST'])
def crop_image():
    crop_info = dict(request.form)
    logger.info("filename: {}".format(crop_info['filename']))
    logger.info("x1: {}".format(crop_info['x1']))
    logger.info("y1: {}".format(crop_info['y1']))
    logger.info("x2: {}".format(crop_info['x2']))
    logger.info("y2: {}".format(crop_info['y2']))
    return jsonify(process_image(crop_info))

def process_image(crop_info):
    database.mark_file_as_processed(crop_info["filename"])
    return {
        "length": 2,
        "width": 1,
        "ratio": 2
    }

if __name__ == '__main__':
    # This starts the server. Just run `python server.py` to start the app.
    app.run()
