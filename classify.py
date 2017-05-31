
import logging
import scipy.io.wavfile as wav
import numpy
import os

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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    data = []
    targets = []
    database = load_mfccs()

    filenames = []

    genres = ['Metal', 'Electronic', 'Jazz', 'Classical']

    for genre in genres:
        for filename in os.listdir('./audio_sample/{}/'.format(genre)):
            filenames.append((
                './audio_sample/{}/{}'.format(genre, filename),
                filename,
                int(genre == 'Metal')
            ))

    for filedata in filenames:
        filepath, filename, target = filedata

        if filename in database:
            data.append(database[filename])
            targets.append(1)
            continue

        logging.info('processing {}'.format(filepath))

        mf = get_features(filepath)[100:1600].flatten().tolist()

        mf = mf[:1500]
        data.append(mf)
        targets.append(target)

    logging.info('fitting')
    classifier = KNeighborsClassifier(
        n_neighbors=5)
    classifier.fit(data, targets)

    #mf = get_features('/home/scott/pull/music/Metal/ffe1a65b732877fb68a3300097be8665')
    mf = get_features('./audio_sample/Metal/01dd4690fffa6f4cbd86af3faa7adc37')
    mf = mf[100:1600].flatten().tolist()
    mf = mf[:1500]

    prediction_probabilities = classifier.predict_proba([mf])

    logging.info(
        'classified as {}'
        .format(prediction_probabilities))



