import tensorflow as tf
import keras
import pandas as pd
import numpy as np
import pickle


class EmailTitleClassifier:
    def __init__(self, model_path: str, tokenizer_path: str):
        self.model = keras.models.load_model(model_path, compile=True)
        with open(tokenizer_path, "rb") as handle:
            from_disk = pickle.load(handle)
            self.vectorizer = keras.layers.TextVectorization.from_config(from_disk['config'])
            # You have to call `adapt` with some dummy data (BUG in Keras)
            self.vectorizer.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
            self.vectorizer.set_vocabulary(from_disk["vocabulary"])

    def predict(self, titles: list[str], threshold: float = 0.5):
        titles = [self.vectorizer(title) for title in titles]
        input_arr = np.array(titles)
        predictions = self.model.predict(input_arr, verbose=0)  # type: ignore

        return [True if pred > threshold else False for pred in predictions]
