import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.callbacks import LearningRateScheduler, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import GaussianDropout
from tensorflow.keras import regularizers

# file_path = 'Training_Datasets_1.xlsx'
# df = pd.read_excel(file_path)
# category_counts = df['Category'].value_counts()

# print(category_counts)

train_data = pd.read_excel("Training_Datasets.xlsx")
test_data = pd.read_excel("Testing_Datasets.xlsx")

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

    # Ensure 'Notes' and 'Merchant Name' columns are strings
    train_df['Notes'] = train_df['Notes'].fillna('').astype(str)
    test_df['Notes'] = test_df['Notes'].fillna('').astype(str)
    train_df['Merchant Name'] = train_df['Merchant Name'].fillna('').astype(str)
    test_df['Merchant Name'] = test_df['Merchant Name'].fillna('').astype(str)

    # TF-IDF for 'Notes' column
    tfidf_vectorizer_notes = TfidfVectorizer(max_features=150, ngram_range=(1, 2))
    tfidf_train_notes = tfidf_vectorizer_notes.fit_transform(train_df['Notes'].fillna('')).toarray()
    tfidf_test_notes = tfidf_vectorizer_notes.transform(test_df['Notes'].fillna('')).toarray()

    # TF-IDF for 'Merchant Name' column
    tfidf_vectorizer_merchant = TfidfVectorizer(max_features=150)
    tfidf_train_merchant = tfidf_vectorizer_merchant.fit_transform(train_df['Merchant Name'].fillna('')).toarray()
    tfidf_test_merchant = tfidf_vectorizer_merchant.transform(test_df['Merchant Name'].fillna('')).toarray()

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

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test_full)

le_category = LabelEncoder()
y_train = le_category.fit_transform(train_data['Category'])
y_test = le_category.transform(test_data['Category'])

y_train_onehot = to_categorical(y_train)
y_test_onehot = to_categorical(y_test)

def create_model(input_dim, output_dim):
    model = Sequential([
        # Dense(2048, kernel_regularizer=l1_l2(l1=1e-4, l2=1e-3)),
        # BatchNormalization(),
        # LeakyReLU(negative_slope=0.2),
        # Dropout(0.3),

        # Dense(1024, kernel_regularizer=l1_l2(l1=1e-4, l2=1e-3)),
        # BatchNormalization(),
        # LeakyReLU(negative_slope=0.2),
        # Dropout(0.3),

        # Dense(512, kernel_regularizer=l1_l2(l1=1e-4, l2=1e-3)),
        # BatchNormalization(),
        # LeakyReLU(negative_slope=0.2),
        # Dropout(0.3),

        # Dense(256, kernel_regularizer=l1_l2(l1=1e-4, l2=1e-3)),
        # BatchNormalization(),
        # LeakyReLU(negative_slope=0.2),
        # Dropout(0.3),

        # Dense(128),
        # BatchNormalization(),
        # LeakyReLU(alpha=0.2),
        # Dropout(0.3),

        # Dense(64),
        # BatchNormalization(),
        # LeakyReLU(alpha=0.2),
        # Dropout(0.3),

        # Dense(32),
        # BatchNormalization(),
        # LeakyReLU(alpha=0.2),
        # Dropout(0.3),

        # Dense(512, kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4),
        #       bias_regularizer=regularizers.l2(1e-4)),
        # BatchNormalization(momentum=0.9),
        # LeakyReLU(alpha=0.1),
        # GaussianDropout(0.1),

        Dense(512, kernel_regularizer=l1_l2(l1=1e-6, l2=1e-5),
              bias_regularizer=regularizers.l2(1e-4)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        GaussianDropout(0.1),

        # Dense(256, kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4),
        #       bias_regularizer=regularizers.l2(1e-4)),
        # BatchNormalization(momentum=0.9),
        # LeakyReLU(alpha=0.1),
        # GaussianDropout(0.1),

        Dense(256, kernel_regularizer=l1_l2(l1=1e-6, l2=1e-5),
              bias_regularizer=regularizers.l2(1e-4)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        GaussianDropout(0.1),

        # Dense(128, kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4),
        #       bias_regularizer=regularizers.l2(1e-4)),
        # BatchNormalization(momentum=0.9),
        # LeakyReLU(alpha=0.1),
        # GaussianDropout(0.1),

        Dense(128, kernel_regularizer=l1_l2(l1=1e-6, l2=1e-5),
              bias_regularizer=regularizers.l2(1e-4)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        GaussianDropout(0.1),

        # Dense(64, kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4)),
        # BatchNormalization(momentum=0.9),
        # LeakyReLU(alpha=0.1),
        # GaussianDropout(0.1),

        Dense(64, kernel_regularizer=l1_l2(l1=1e-6, l2=1e-5),
              bias_regularizer=regularizers.l2(1e-4)),
        BatchNormalization(momentum=0.9),
        LeakyReLU(alpha=0.1),
        GaussianDropout(0.1),

        Dense(output_dim, activation='softmax')
    ])
    return model

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=15,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=5,
    min_lr=1e-6
)

model = create_model(X_train_scaled.shape[1], y_train_onehot.shape[1])
model.compile(
    # optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    X_train_scaled, y_train_onehot,
    epochs=300,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)

# test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test_onehot, verbose=0)
# print(f"Test Accuracy: {test_accuracy:.4f}")

# plt.figure(figsize=(12, 4))
# plt.subplot(1, 2, 1)
# plt.plot(history.history['accuracy'], label='Training Accuracy')
# plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
# plt.title('Model Accuracy')
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy')
# plt.legend()

# plt.subplot(1, 2, 2)
# plt.plot(history.history['loss'], label='Training Loss')
# plt.plot(history.history['val_loss'], label='Validation Loss')
# plt.title('Model Loss')
# plt.xlabel('Epoch')
# plt.ylabel('Loss')
# plt.legend()
# plt.tight_layout()
# plt.show()

test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test_onehot, verbose=0)

# Extract training loss and accuracy from the final epoch
training_loss = history.history['loss'][-1]
training_accuracy = history.history['accuracy'][-1]

print(f"Training Loss: {training_loss:.4f}")
print(f"Training Accuracy: {training_accuracy:.4f}")
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

plt.figure(figsize=(12, 4))
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