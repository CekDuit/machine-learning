# transaction_classifier/main.py
import pandas as pd
from transaction_classifier.data_processing import preprocess_transaction_data
from transaction_classifier.model import train_and_evaluate
from sklearn.preprocessing import LabelEncoder

def main():
    training_data_path = 'Training_Datasets.xlsx'
    testing_data_path = 'Testing_Datasets.xlsx'

    train_df = pd.read_excel(training_data_path)
    test_df = pd.read_excel(testing_data_path)
    test_df['Category'] = None

    X_train, X_test, scaler, tfidf_notes, tfidf_merchant = preprocess_transaction_data(train_df, test_df)

    le_category = LabelEncoder()
    y_train = le_category.fit_transform(train_df['Category'])
    y_test = le_category.transform(test_df['Category'].dropna()) if 'Category' in test_df.columns else []

    train_and_evaluate(train_df, test_df, X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()