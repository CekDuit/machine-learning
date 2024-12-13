# transaction_classifier/data_processing.py
import pandas as pd
import numpy as np
import random
import nltk
from nltk.corpus import wordnet
import tensorflow as tf
import keras
from sklearn.preprocessing import StandardScaler
from utils import save_pickle, load_pickle

nltk.download('wordnet')

def augment_text_with_synonyms(text, num_replacements=2):
    words = text.split()
    for _ in range(num_replacements):
        word_idx = random.randint(0, len(words) - 1)
        synonyms = wordnet.synsets(words[word_idx])
        if synonyms:
            if synonyms[0] is not None:
                synonym = synonyms[0].lemmas()[0].name()
                if synonym != words[word_idx]:
                    words[word_idx] = synonym
    return ' '.join(words)

def process_datetime_features(df):
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Year'] = df['Datetime'].dt.year.astype(np.int32)
    df['Month'] = df['Datetime'].dt.month.astype(np.int32)
    df['DayOfWeek'] = df['Datetime'].dt.dayofweek.astype(np.int32)
    df['DayOfMonth'] = df['Datetime'].dt.day.astype(np.int32)
    df['WeekOfYear'] = df['Datetime'].dt.isocalendar().week.astype(np.int32)
    df['IsWeekend'] = df['Datetime'].dt.dayofweek.isin([5, 6]).astype(np.int32)
    return df

def preprocess_transaction_data(train_df, test_df):
    train_df = process_datetime_features(train_df)
    test_df = process_datetime_features(test_df)

    # Ensure string columns
    train_df['Notes'] = train_df['Notes'].astype(str)
    train_df['Merchant Name'] = train_df['Merchant Name'].astype(str)
    test_df['Notes'] = test_df['Notes'].astype(str)
    test_df['Merchant Name'] = test_df['Merchant Name'].astype(str)

    # Augmentation
    train_df['Notes'] = train_df['Notes'].apply(lambda x: augment_text_with_synonyms(x, num_replacements=2))
    train_df['Merchant Name'] = train_df['Merchant Name'].apply(lambda x: augment_text_with_synonyms(x, num_replacements=1))

    # TF-IDF
    tfidf_notes = keras.layers.TextVectorization(max_tokens=150, output_mode='tf-idf')
    tfidf_notes.adapt(tf.constant(train_df['Notes']))
    tfidf_train_notes = tfidf_notes(tf.constant(train_df['Notes'])).numpy()
    tfidf_test_notes = tfidf_notes(tf.constant(test_df['Notes'])).numpy()

    tfidf_merchant = keras.layers.TextVectorization(max_tokens=150, output_mode='tf-idf')
    tfidf_merchant.adapt(tf.constant(train_df['Merchant Name']))
    tfidf_train_merchant = tfidf_merchant(tf.constant(train_df['Merchant Name'])).numpy()
    tfidf_test_merchant = tfidf_merchant(tf.constant(test_df['Merchant Name'])).numpy()

    save_pickle(tfidf_notes.get_config(), 'trained/tfidf_notes_config.pkl')
    save_pickle(tfidf_notes.get_vocabulary(), 'trained/tfidf_notes_vocabulary.pkl')
    save_pickle(tfidf_merchant.get_config(), 'trained/tfidf_merchant_config.pkl')
    save_pickle(tfidf_merchant.get_vocabulary(), 'trained/tfidf_merchant_vocabulary.pkl')

    # Scaling
    numerical_features = ['Amount', 'Year', 'Month', 'DayOfWeek', 'DayOfMonth', 'WeekOfYear', 'IsWeekend']
    scaler = StandardScaler()
    numerical_train = scaler.fit_transform(train_df[numerical_features])
    numerical_test = scaler.transform(test_df[numerical_features])

    save_pickle(scaler, 'trained/scaler.pkl')

    # Combine features
    X_train = np.hstack((numerical_train, tfidf_train_notes, tfidf_train_merchant))
    X_test = np.hstack((numerical_test, tfidf_test_notes, tfidf_test_merchant))
    return X_train, X_test, scaler, tfidf_notes, tfidf_merchant
