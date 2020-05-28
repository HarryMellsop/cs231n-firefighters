import tensorflow as tf
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import TimeDistributed, Conv2D, MaxPooling2D, Flatten, LSTM, Dense

class ConvolutionalLSTM():

    def __init__(self):
        # create the model 
        self.model = Sequential()

        # inputs to the model are initially downscaled to 400x400
        # initially, use a CNN on each image input tensor in order to extract key features
                                                                                                            # meaning 9 months fed, 400x400x3 image
        self.model.add(TimeDistributed(Conv2D(filters=5, kernel_size=7, activation='relu'), batch_input_shape=(9, 9, 400, 400, 3)))
        self.model.add(TimeDistributed(MaxPooling2D(pool_size=4)))
        self.model.add(TimeDistributed(Conv2D(filters=5, kernel_size=5, activation='relu')))
        self.model.add(TimeDistributed(MaxPooling2D(pool_size=4)))
        self.model.add(TimeDistributed(Flatten()))

        # now, pass these pre-feature extracted tensors on to an LSTM
        self.model.add(LSTM(50, stateful=True))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae', 'mape', 'acc'])
        self.model.summary()

    def fit(self):
        pass