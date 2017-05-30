#!/usr/bin/env python3

# Documents
# http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
# http://freemusicarchive.org/genre/Metal/
# https://github.com/tyiannak/pyAudioAnalysis

import hashlib
import logging
import os

from flask import (
    Flask, render_template, redirect, request, send_from_directory)
from pydub import AudioSegment
from werkzeug import secure_filename

from classify import classify

logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER_WAV = './audio_data'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/'
app.config['UPLOAD_FOLDER_WAV'] = './audio_data'

MEGABYTE = 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = 20 * MEGABYTE


@app.route('/', methods=['GET', 'POST'])
def route_index():
    if request.method == 'POST':
        upload = request.files['file']
        if upload.filename == '':
            return redirect(request.url)

        if upload:
            logging.info(
                "incoming upload: {}"
                .format(upload.filename))
            filename = secure_filename(upload.filename)
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            upload.save(file_location)

            with open(file_location, 'rb') as f:

                # get the hash of the file, h
                hasher = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
                h = hasher.hexdigest()

                # _, ext = os.path.splitext(file_location)
                new_file_loc = os.path.join(
                    app.config['UPLOAD_FOLDER_WAV'], h + '.wav'
                )

                logging.info(new_file_loc)

                song = AudioSegment.from_file(file_location)
                song.export(new_file_loc)

                classify(new_file_loc)

            return h

    return render_template('index.html', title="Is It Metal?")

@app.route('/static/css/<path:path>')
def route_static_css(path):
    return send_from_directory('./static/css', path);
