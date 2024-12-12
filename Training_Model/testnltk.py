import random
from nltk.corpus import wordnet
import tensorflow as tf
from tensorflow.keras.layers import Attention
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU
from tensorflow.keras.regularizers import l1_l2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.utils import to_categorical
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import nltk
from tensorflow.keras.layers import GaussianDropout
from tensorflow.keras import regularizers
from sklearn.utils.class_weight import compute_class_weight

# Ensure nltk WordNet is downloaded
nltk.download('wordnet')

# Load datasets
train_data = pd.read_excel("Training_Datasets.xlsx")
test_data = pd.read_excel("Testing_Datasets.xlsx")

# Function for synonym replacement in the "Notes" column
def augment_text_with_synonyms(text, num_replacements=2):
    words = text.split()
    for _ in range(num_replacements):
        word_idx = random.randint(0, len(words) - 1)
        synonyms = wordnet.synsets(words[word_idx])
        if synonyms:
            synonym = synonyms[0].lemmas()[0].name()
            if synonym != words[word_idx]:
                words[word_idx] = synonym
    return ' '.join(words)

# Apply text augmentation on "Notes" and "Merchant Name"
train_data_augmented = train_data.copy()
train_data_augmented['Notes'] = train_data_augmented['Notes'].apply(
    lambda x: augment_text_with_synonyms(str(x), num_replacements=2)
)
train_data_augmented['Merchant Name'] = train_data_augmented['Merchant Name'].apply(
    lambda x: augment_text_with_synonyms(str(x), num_replacements=1)
)

# Preprocessing function
def preprocess_data_aligned(train_df, test_df):
    # Processing datetime-related features
    for df in [train_df, test_df]:
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df['Year'] = df['Datetime'].dt.year
        df['Month'] = df['Datetime'].dt.month
        df['DayOfWeek'] = df['Datetime'].dt.dayofweek
        df['DayOfMonth'] = df['Datetime'].dt.day
        df['WeekOfYear'] = df['Datetime'].dt.isocalendar().week
        df['IsWeekend'] = df['Datetime'].dt.dayofweek.isin([5, 6]).astype(int)

        # Convert 'Notes' and 'Merchant Name' to strings
        df['Notes'] = df['Notes'].astype(str)
        df['Merchant Name'] = df['Merchant Name'].astype(str)

    # TF-IDF for 'Notes' column
    tfidf_vectorizer_notes = TfidfVectorizer(max_features=150, ngram_range=(1, 2))
    tfidf_train_notes = tfidf_vectorizer_notes.fit_transform(train_df['Notes']).toarray()
    tfidf_test_notes = tfidf_vectorizer_notes.transform(test_df['Notes']).toarray()

    # TF-IDF for 'Merchant Name' column
    tfidf_vectorizer_merchant = TfidfVectorizer(max_features=150)
    tfidf_train_merchant = tfidf_vectorizer_merchant.fit_transform(train_df['Merchant Name']).toarray()
    tfidf_test_merchant = tfidf_vectorizer_merchant.transform(test_df['Merchant Name']).toarray()

    # Creating DataFrames from the TF-IDF arrays
    tfidf_train_df = pd.DataFrame(np.hstack((tfidf_train_notes, tfidf_train_merchant)),
                                  columns=[f"TFIDF_N_{i}" for i in range(tfidf_train_notes.shape[1])] +
                                          [f"TFIDF_M_{i}" for i in range(tfidf_train_merchant.shape[1])])
    tfidf_test_df = pd.DataFrame(np.hstack((tfidf_test_notes, tfidf_test_merchant)),
                                 columns=[f"TFIDF_N_{i}" for i in range(tfidf_test_notes.shape[1])] +
                                         [f"TFIDF_M_{i}" for i in range(tfidf_test_merchant.shape[1])])

    # One-hot encoding for categorical columns
    categorical_train = pd.get_dummies(train_df[['Transaction Type', 'Payment Method']])
    categorical_test = pd.get_dummies(test_df[['Transaction Type', 'Payment Method']])

    categorical_train, categorical_test = categorical_train.align(categorical_test, join='outer', axis=1, fill_value=0)

    # Extracting numerical features and log transformation
    numerical_features = ['Amount', 'Year', 'Month', 'DayOfWeek', 'DayOfMonth', 'WeekOfYear', 'IsWeekend']
    numerical_train = train_df[numerical_features].copy()
    numerical_test = test_df[numerical_features].copy()

    numerical_train['Amount_Log'] = np.log1p(numerical_train['Amount'])
    numerical_test['Amount_Log'] = np.log1p(numerical_test['Amount'])

    # Combining the features
    train_combined = pd.concat([numerical_train, categorical_train, tfidf_train_df], axis=1)
    test_combined = pd.concat([numerical_test, categorical_test, tfidf_test_df], axis=1)

    return train_combined, test_combined

X_train_full, X_test_full = preprocess_data_aligned(train_data, test_data)
X_train_augmented, _ = preprocess_data_aligned(train_data_augmented, test_data)

# Scaling the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test_full)
X_train_scaled_augmented = scaler.transform(X_train_augmented)

# Combining original and augmented data
X_train_combined = np.vstack([X_train_scaled, X_train_scaled_augmented])

# Encoding target labels
le_category = LabelEncoder()
y_train = le_category.fit_transform(train_data['Category'])
y_test = le_category.transform(test_data['Category'])

y_train_onehot = to_categorical(y_train)
y_test_onehot = to_categorical(y_test)

y_train_combined = np.vstack([y_train_onehot, y_train_onehot])

# Adjusted model with increased complexity
def create_complex_model(input_dim, output_dim):
    model = Sequential([
        Dense(1024, kernel_regularizer=l1_l2(l1=1e-8, l2=1e-7),bias_regularizer=regularizers.l2(1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(512, kernel_regularizer=l1_l2(l1=1e-8, l2=1e-7),bias_regularizer=regularizers.l2(1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(256, kernel_regularizer=l1_l2(l1=1e-8, l2=1e-7),bias_regularizer=regularizers.l2(1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(128, kernel_regularizer=l1_l2(l1=1e-8, l2=1e-7),bias_regularizer=regularizers.l2(1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),
        Dense(64, kernel_regularizer=l1_l2(l1=1e-8, l2=1e-7),bias_regularizer=regularizers.l2(1e-7)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        Dropout(0.1),

        Dense(output_dim, activation='softmax')
    ])
    return model

# Early stopping and learning rate scheduler
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=15,
    restore_best_weights=True
)

# reduce_lr = ReduceLROnPlateau(
#     monitor='val_loss',
#     factor=0.2,
#     patience=5,
#     min_lr=1e-6
# )

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=1e-7
)

# Train the adjusted model
complex_model = create_complex_model(X_train_combined.shape[1], y_train_combined.shape[1])
complex_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history_complex = complex_model.fit(
    X_train_combined, y_train_combined,
    epochs=300,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)

# Save the trained model to an .h5 file
complex_model.save("transaction_prediction_model.h5")
print("Model saved as transaction_prediction_model.h5")

test_loss_complex, test_accuracy_complex = complex_model.evaluate(X_test_scaled, y_test_onehot, verbose=0)
print(f"Test Accuracy (Complex Model): {test_accuracy_complex:.4f}")
print(f"Test Loss (Complex Model): {test_loss_complex:.4f}")

# Plot results
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history_complex.history['accuracy'], label='Training Accuracy (Complex)')
plt.plot(history_complex.history['val_accuracy'], label='Validation Accuracy (Complex)')
plt.title('Model Accuracy (Complex)')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history_complex.history['loss'], label='Training Loss (Complex)')
plt.plot(history_complex.history['val_loss'], label='Validation Loss (Complex)')
plt.title('Model Loss (Complex)')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.tight_layout()
plt.show()