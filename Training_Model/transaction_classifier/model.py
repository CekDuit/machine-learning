# transaction_classifier/model.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, BatchNormalization, LeakyReLU, Dropout
from utils import save_pickle

def create_model(input_dim, output_dim):
    model = Sequential([
        Dense(1024, kernel_regularizer=tf.keras.regularizers.l1_l2(1e-8, 1e-7)),
        BatchNormalization(),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(512, kernel_regularizer=tf.keras.regularizers.l1_l2(1e-8, 1e-7)),
        BatchNormalization(),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(128, kernel_regularizer=tf.keras.regularizers.l1_l2(1e-8, 1e-7)),
        BatchNormalization(),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(output_dim, activation='softmax')
    ])
    return model

def train_and_evaluate(train_df, test_df, X_train, X_test, y_train, y_test):
    model = create_model(X_train.shape[1], len(set(y_train)))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    history = model.fit(X_train, tf.keras.utils.to_categorical(y_train), epochs=15, validation_split=0.2)

    if len(y_test) > 0:
        test_loss, test_accuracy = model.evaluate(X_test, tf.keras.utils.to_categorical(y_test))
        print(f"Test Accuracy: {test_accuracy:.4f}, Test Loss: {test_loss:.4f}")

    return model