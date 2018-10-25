import numpy as np
import pandas as pd

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.utils import np_utils
import keras.backend as K
np.random.seed(123)

class Model():

    def __init__(self):
        model = Sequential()
        model.add(Dense(8, input_dim=420*6, activation='relu'))
        model.add(Dense(8, activation='relu'))
        # model.add(Dense(1, activation='linear'))
        model.add(Dense(1, activation='relu'))

if __name__ == '__main__':
    md = Model()