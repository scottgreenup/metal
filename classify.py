
import logging
import numpy
import scipy.io.wavfile as wav

from pydub import AudioSegment

from python_speech_features import mfcc, delta, logfbank

# http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/



def classify2(filename):
    logging.info("Classifying: {}".format(filename))

    rate, signal = wav.read(filename)
    mfcc_features = mfcc(signal, rate)
    print(mfcc_features)

    return signal


def classify(filename):
    logging.info("Classifying: {}".format(filename))

    song = AudioSegment.from_file(filename)
    data = numpy.fromstring(song._data, numpy.int16)

    # Gather separate channels together [[CH1 CH2] ...]
    x = []
    for channel in range(song.channels):
        logging.info(channel)
        logging.info(song.channels)
        x.append(data[channel::song.channels])
        logging.info("appended: {}".format(x[-1]))
    x = numpy.array(x).T

    # Convert to MONO if STEREO
    if x.ndim == 2:
        if x.shape[1] == 1:
            x = x.flatten()
        elif x.shape[1] == 2:
            x = ((x[:,1] / 2) + (x[:,0] / 2))

    mfcc_features = mfcc(x, song.frame_rate)

    return mfcc_features


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    classify('./audio_data/b37abc5589aee2f2ba86cc001b008678.wav')
