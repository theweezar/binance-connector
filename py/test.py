import numpy as np
import pandas as pd
from keras.src.models.sequential import Sequential
from keras.src.layers.rnn.lstm import LSTM
from keras.src.layers.core.dense import Dense
from keras.src.layers.regularization.dropout import Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split