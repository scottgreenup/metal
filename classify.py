
import logging
import scipy.io.wavfile as wav
import numpy
import os

import random

import matplotlib.pyplot as plt

from pydub import AudioSegment
from python_speech_features import mfcc
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier

# http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/
logging.basicConfig(level=logging.INFO)

def load_audio(filename):
    song = AudioSegment.from_file(filename)
    data = numpy.fromstring(song._data, numpy.int16)

    # Gather separate channels together [[CH1 CH2 ... CHN] ...]
    signal = [data[channel::song.channels] for channel in range(song.channels)]
    signal = numpy.array(signal).T

    # Convert to MONO if STEREO
    if signal.ndim == 2:
        if signal.shape[1] == 1:
            signal = signal.flatten()
        elif signal.shape[1] == 2:
            signal = ((signal[:,1] / 2) + (signal[:,0] / 2))

    return signal, song.frame_rate


def get_features(filename):
    signal, rate = load_audio(filename)

    mfcc_features = mfcc(signal, rate)

    # Target is the classification
    # data is the atrributes
    # feature_names are the titles of each column in each dataset
    # target_names are the titles of each target
    # So... we give the attribute data and the classification of each data
    # point.

    return mfcc_features

def save_mfcc(filename, mf, dbfile='./main.db'):
    with open(dbfile, 'a') as f:
        f.write('{}:{}\n'.format(filename, ','.join(str(x) for x in mf)))

def load_mfccs(dbfile='./main.db'):
    database = {}

    with open(dbfile, 'r') as f:
        for line in f:
            line = line.split(':')
            database[line[0]] = [float(x) for x in line[1].split(',')]

    return database

def classify(filename, classifier):
    logging.info("classifying {}".format(filename))

    mf = get_features(filename)
    mf = mf[100:1600].flatten().tolist()
    mf = mf[:1500]
    pred = classifier.predict_proba([mf])
    return pred[0][1] > pred[0][0]

def build_model():

    logging.info("building model...")

    data = []
    targets = []
    database = load_mfccs()

    filenames = []

    genres = ['Metal', 'Electronic', 'Jazz', 'Classical']

    for genre in genres:
        for filename in os.listdir('./audio_dataset/{}/'.format(genre)):
            filenames.append((
                './audio_dataset/{}/{}'.format(genre, filename),
                filename,
                int(genre == 'Metal')
            ))

    for filedata in filenames:
        filepath, filename, target = filedata

        logging.debug('processing {} ({})'.format(filepath, target))

        if filename in database:
            if len(database[filename]) != 1500:
                logging.debug(' -> skipping');
                continue

            logging.debug(' -> found in cache');
            data.append(database[filename])
            targets.append(target)
            continue

        mf = get_features(filepath)[100:1600].flatten().tolist()
        mf = mf[:1500]

        save_mfcc(filename, mf)

        data.append(mf)
        targets.append(target)

    classifier = KNeighborsClassifier(
        n_neighbors=10)
    classifier.fit(data, targets)

    logging.info("built model, done")
    return classifier

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    classifier = build_model()
    pred = classify(
        './audio_dataset/Classical/a7bc0f4161bfba9e16d0c4186e437020',
        classifier)

    logging.info(pred)
