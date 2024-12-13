import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import nltk
from nltk.corpus import wordnet
import tensorflow as tf
from tensorflow.keras.layers import Dense, BatchNormalization, LeakyReLU, Dropout, CategoryEncoding, TextVectorization
from tensorflow.keras.models import Sequential
from tensorflow.keras import regularizers
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from datetime import datetime
from decimal import Decimal
from ..Email_Data_Extraction.extractors.base_extractor import TransactionData

# Ensure nltk WordNet is downloaded
nltk.download('wordnet')

# Save and load pickled objects
def save_pickle(obj, filename):
    """ Save the object to a pickle file. """
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def load_pickle(filename):
    """ Load the object from a pickle file. """
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Function for synonym replacement in the "Notes" column
def augment_text_with_synonyms(text, num_replacements=2):
    words = text.split()
    for _ in range(num_replacements):
        word_idx = random.randint(0, len(words) - 1)
        synonyms = wordnet.synsets(words[word_idx])
        if synonyms:
            if synonyms[0]:
                synonym = synonyms[0].lemmas()[0].name()
                if synonym != words[word_idx]:
                    words[word_idx] = synonym
    return ' '.join(words)

# Process datetime-related features
def process_datetime_features(df):
    """ Process datetime-related features like Year, Month, DayOfWeek, etc. """
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Year'] = df['Datetime'].dt.year
    df['Month'] = df['Datetime'].dt.month
    df['DayOfWeek'] = df['Datetime'].dt.dayofweek
    df['DayOfMonth'] = df['Datetime'].dt.day
    df['WeekOfYear'] = df['Datetime'].dt.isocalendar().week
    df['IsWeekend'] = df['Datetime'].dt.dayofweek.isin([5, 6]).astype(int)
    return df

# Preprocess the training and test datasets
def preprocess_transaction_data(train_df, test_df):
    """ Preprocess the training and testing data, applying text augmentation, TF-IDF, category encoding, and scaling. """
    
    # Process datetime features
    train_df = process_datetime_features(train_df)
    test_df = process_datetime_features(test_df)

    # Apply text augmentation on "Notes" and "Merchant Name" columns
    train_df['Notes'] = train_df['Notes'].apply(lambda x: augment_text_with_synonyms(str(x), num_replacements=2))
    train_df['Merchant Name'] = train_df['Merchant Name'].apply(lambda x: augment_text_with_synonyms(str(x), num_replacements=1))

    # TF-IDF for 'Notes' column
    tfidf_vectorizer_notes = TextVectorization(max_features=150, ngram_range=(1, 2))
    tfidf_train_notes = tfidf_vectorizer_notes(train_df['Notes'].values)
    tfidf_test_notes = tfidf_vectorizer_notes(test_df['Notes'].values)

    # TF-IDF for 'Merchant Name' column
    tfidf_vectorizer_merchant = TextVectorization(max_features=150)
    tfidf_train_merchant = tfidf_vectorizer_merchant(train_df['Merchant Name'].values)
    tfidf_test_merchant = tfidf_vectorizer_merchant(test_df['Merchant Name'].values)

    # Save the vectorizers for future use
    save_pickle(tfidf_vectorizer_notes, 'trained/notes_vectorizer.pkl')
    save_pickle(tfidf_vectorizer_merchant, 'trained/merchant_vectorizer.pkl')

    # Category Encoding for 'Payment Method' and 'Transaction Type'
    category_encoding_layer = CategoryEncoding(output_mode='one_hot')
    categorical_train = category_encoding_layer(tf.convert_to_tensor(train_df[['Payment Method', 'Transaction Type']].values))
    categorical_test = category_encoding_layer(tf.convert_to_tensor(test_df[['Payment Method', 'Transaction Type']].values))

    # Save the category encoding layer for future use
    save_pickle(category_encoding_layer, 'trained/category_encoding_layer.pkl')

    # Scaling the numerical features (e.g., Amount, Year, Month, DayOfWeek, etc.)
    scaler = StandardScaler()
    numerical_features = ['Amount', 'Year', 'Month', 'DayOfWeek', 'DayOfMonth', 'WeekOfYear', 'IsWeekend']
    numerical_train = train_df[numerical_features]
    numerical_test = test_df[numerical_features]

    numerical_train_scaled = scaler.fit_transform(numerical_train)
    numerical_test_scaled = scaler.transform(numerical_test)

    # Save the scaler for future use
    save_pickle(scaler, 'trained/scaler.pkl')

    # Combine all processed features into a single feature set
    X_train_combined = np.hstack((numerical_train_scaled, categorical_train, tfidf_train_notes, tfidf_train_merchant))
    X_test_combined = np.hstack((numerical_test_scaled, categorical_test, tfidf_test_notes, tfidf_test_merchant))

    return X_train_combined, X_test_combined, scaler, tfidf_vectorizer_notes, tfidf_vectorizer_merchant, category_encoding_layer

# Create a complex model for the task
def create_model(input_dim, output_dim, category_encoding_layer, tfidf_vectorizer_notes, tfidf_vectorizer_merchant):
    model = Sequential([
        Dense(1024, kernel_regularizer=regularizers.l1_l2(l1=1e-8, l2=1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(512, kernel_regularizer=regularizers.l1_l2(l1=1e-8, l2=1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(256, kernel_regularizer=regularizers.l1_l2(l1=1e-8, l2=1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(128, kernel_regularizer=regularizers.l1_l2(l1=1e-8, l2=1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(output_dim, activation='softmax')
    ])
    return model

# Training and evaluation function
def train_and_evaluate(training_data_path, test_data):
    """Trains and evaluates the model using the provided training data from .xlsx."""
    
    # Load the training dataset from .xlsx file
    train_df = pd.read_excel(training_data_path)

    # Convert TransactionData objects to DataFrame for testing (without the 'Category' column)
    test_df = pd.DataFrame([tx.to_formatted_dict() for tx in test_data])

    # Ensure 'Category' column is not present in test_df
    if 'Category' in test_df.columns:
        test_df = test_df.drop('Category', axis=1)

    # Preprocess the data
    X_train, X_test, scaler, tfidf_vectorizer_notes, tfidf_vectorizer_merchant, category_encoding_layer = preprocess_transaction_data(train_df, test_df)

    # Encode the target labels for training data
    le_category = LabelEncoder()
    y_train = le_category.fit_transform(train_df['Category'])
    
    # Since there's no 'Category' in the test data, this line will be ignored.
    y_test = le_category.transform(test_df.get('Category', []))  # Will be empty if no 'Category' in test_df

    save_pickle(le_category, 'trained/label_encoder.pkl')

    # One-hot encode the target labels
    y_train_onehot = tf.keras.utils.to_categorical(y_train)
    y_test_onehot = tf.keras.utils.to_categorical(y_test)

    # Create the model
    model = create_model(X_train.shape[1], y_train_onehot.shape[1], category_encoding_layer, tfidf_vectorizer_notes, tfidf_vectorizer_merchant)
    
    # Compile the model
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    history = model.fit(X_train, y_train_onehot, epochs=50, batch_size=64, validation_split=0.2, verbose=1)

    # Evaluate the model on the test set
    test_loss, test_accuracy = model.evaluate(X_test, y_test_onehot, verbose=0)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test Loss: {test_loss:.4f}")

    # Predict the categories for the test data
    y_test_pred = model.predict(X_test)

    # Convert predictions from one-hot encoding back to label encoding
    y_test_pred_labels = np.argmax(y_test_pred, axis=1)

    # Optionally, decode the predicted labels back to the original category names
    category_labels = le_category.classes_
    y_test_pred_categories = category_labels[y_test_pred_labels]

    print("Predicted Categories for Test Data:")
    print(y_test_pred_categories)

    # Plot the training and validation accuracy
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.show()

    return model

# Example paths (replace with actual file paths)
training_data_path = 'Training_Dataset.xlsx'
trx_data = TransactionData()
trx_data.trx_id = "MB202408171843272383"
trx_data.date = datetime.now()
trx_data.merchant = "Payssion"
trx_data.amount = Decimal(16483)
trx_data.currency = "IDR"
trx_data.payment_method = "OCBC"
trx_data.is_incoming = False
trx_data.description = "QR Payment Merchant PAN 9360091503607510"
test_data = trx_data    

# Train and evaluate the model
model = train_and_evaluate(training_data_path, test_data)

# Save the model in .keras format
model.save("trained/category_prediction_model.keras")
print("Model saved as category_prediction_model.keras")