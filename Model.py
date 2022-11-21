import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # kill warning about tensorflow
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import load_model


# Building the neural network

class Model:

    def __init__(self, num_layers, width, batch_size, learning_rate, input_dim, output_dim):
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.model = self.build_model(num_layers, width)
        self.model.summary()

    # Generating the neural network: Refering to: https://keras.io/api/models/model/
    def build_model(self, num_layers, width):
        inputs = keras.Input(shape=(self.input_dim,))
        x = layers.Dense(width, activation='relu')(inputs)
        for _ in range(num_layers):
            x = layers.Dense(width, activation='relu')(x)
        outputs = layers.Dense(self.output_dim, activation='linear')(x)

        model = keras.Model(inputs=inputs, outputs=outputs, name='my_model')
        model.compile(loss=losses.mean_squared_error, optimizer=Adam(learning_rate=self.learning_rate))
        return model

    # Function which predicts the action from a single state
    def predict_one(self, state):
        state = np.reshape(state, [1, self.input_dim])
        return self.model.predict(state)

    # Function which predicts the action from a batch of states
    def predict_batch(self, states):
        return self.model.predict(states)

        #  https: // www.educba.com / keras - fit /
    def train_batch(self, states, q_sa):
        self.model.fit(states, q_sa, epochs=1, verbose=0)

    # SAVING MODEL

    def save_model(self, path):
        self.model.save(os.path.join(path, 'trained_model.h5'))
        plot_model(self.model, to_file=os.path.join(path, 'model_structure.png'),
                   show_shapes=True, show_layer_names=True)



class Model_test:

    def __init__(self, input_dim, model_path):
        self.input_dim = input_dim
        self.model = self.load_my_model(model_path)


    def load_my_model(self, model_folder_path):

        model_file_path = os.path.join(model_folder_path, 'trained_model.h5')

        if os.path.isfile(model_file_path):
            loaded_model = load_model(model_file_path)
            return loaded_model
        else:
            sys.exit("Model number not found")


    def predict_one(self, state):

        state = np.reshape(state, [1, self.input_dim])
        return self.model.predict(state)
