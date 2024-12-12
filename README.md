# CekDuit - Machine Learning
Welcome to the CekDuit Machine Learning repository. This project is a part of Bangkit Academy 2024 Batch 2, a career-readiness program supported by Google, GoTo, Tokopedia, and Traveloka.

## Members
| Name | Student ID | Role |
|---|---|---|
| Darius Mulyadi Putra | M320B4KY1002 | ML |
| Fransiscus Xaverius Surya Darmawan | M320B4KY1551 | ML |
| Nathan Adhitya | M244B4KY3263 | ML |
| Aristo Tely | C134B4KY0653 | CC |
| Nicholas Fransisco | C244B4KY3356 | CC |
| Johan Hadi Winarto | A389B4KY2081 | MD |
| Aca Maulana | A413B4KY0055 | MD |

## Introduction
The machine learning section of this capstone project focuses on:
1. Identifying email titles that are related to successful payments/transactions.
2. Extracting transaction details from email content.
3. Classifying email titles into predefined categories.

## How does it work?
### Summary
1. For each email, we extract the title and check whether it is a transactional email. This check is done with existing parsers and the title classifier model.
2. For each transactional email with an existing parser, we extract the transaction detail.
3. For each transactional email without an existing parser, we dump it into `Email_Data_Extraction/dumped` folder.
4. For each transaction detail, we run the classification model to classify the type of transaction.

### Classifying transactional emails
#### Explanation
To classify transactional emails, we created a machine learning model that is trained on pairs of (title, is_transaction).

#### Creating the dataset
We do not have a public dataset. However, you can create your own dataset by following the steps below:
1. Create a Google Console Project and enable the Gmail API.
2. Add a Gmail readonly API access to your project.
3. Create a Desktop OAuth Client ID and download the credentials.
4. Place the `client_secret.json` file in the `Email_Data_Extraction` folder.
5. Run the (extract_email_titles.py)[./Email_Data_Extraction/extract_email_titles.py] script to extract email titles from your Gmail account. The script will ask you to authorize the script to access your Gmail account. Once done, the script will create a `email-titles.csv` file in the `Email_Data_Extraction` folder.
6. You may then add is_transaction labels to the `email-titles.csv` file using the (titles-labeller.ipynb)[./Email_Data_Extraction/tools/titles-labeller.ipynb] notebook. The notebook uses a local LLM model through Ollama to help label the titles. This can also be done manually.

#### Training the transaction classifier
We use primarily the [TensorFlow](https://www.tensorflow.org/) library for training the classification model.
Refer to the [email_titles_nlp.ipynb](./Email_Data_Extraction/email_titles_nlp.ipynb) notebook for more details.
The resulting model is saved in the `trained` folder. A small library to use the model is provided in the [title_classifier.py](./Email_Data_Extraction/title_classifier.py) file.

### Extracting transaction details
The script [extract_email_data.py](./Email_Data_Extraction/extract_email_data.py) is used to extract transaction details from email content.

The extractor implementations are placed in the `Email_Data_Extraction/extractors` folder. Each extractor is a class that implements the `BaseExtractor` class. The `BaseExtractor` class defines the `match` method, which checks if the email matches the extractor, and the `extract` method, which extracts the transaction details from the email.

For each transactional email, we extract the following details:
- Datetime
- Merchant Name
- Sub Category
- Category
- Amount
- Currency
- Transaction Type
- Payment Method
- Transaction ID
- Notes

Once extracted, each transaction is saved in `email-extract.csv` in the `Email_Data_Extraction` folder. Emails which match an existing extractor/is likely a transactional email are also dumped into the `Email_Data_Extraction/dumped` folder.

### Classifying transactions
WIP

## Development Notes
1. Install the required packages by running `pip install -r requirements.txt`.
