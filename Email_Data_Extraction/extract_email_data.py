import asyncio
import datetime
import email
import importlib
import os
import pickle
import random
from aiogoogle.client import Aiogoogle
from aiogoogle.excs import HTTPError
from aiogoogle.auth.creds import UserCreds, ClientCreds
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import re
import json
import pandas as pd
import html2text
import base64
import csv

from extractors.grabfood import GrabFoodExtractor
from extractors.gotagihan import GoTagihanExtractor
from extractors.google_play import GooglePlayExtractor
from extractors.grab import GrabExtractor
from extractors.itemku import ItemkuExtractor
from extractors.jago import JagoExtractor
from extractors.mobapay import MobaPayExtractor
from extractors.mybca import MyBCAExtrator
from extractors.ocbc import OCBCExtractor
from extractors.ovo import OVOExtractor
from extractors.paypal import PaypalExtractor
from extractors.seabank import SeaBankExtractor
from extractors.steam import SteamExtractor
from extractors.unipin import UniPinExtractor
from extractors.xsolla import XsollaExtractor
from extractors.gofood import GoFoodExtractor
from extractors.base_extractor import BaseExtractor, EmailContent, TransactionData
from extractors.bri import BRIExtractor
from extractors.eg import EGExtractor



exs: list[BaseExtractor] = [
    BRIExtractor(),
    EGExtractor(),
    GoFoodExtractor(),
    GooglePlayExtractor(),
    GrabExtractor(),
    ItemkuExtractor(),
    JagoExtractor(),
    UniPinExtractor(),
    MobaPayExtractor(),
    MyBCAExtrator(),
    OCBCExtractor(),
    OVOExtractor(),
    PaypalExtractor(),
    SeaBankExtractor(),
    SteamExtractor(),
    UniPinExtractor(),
    XsollaExtractor(),
    GoTagihanExtractor(),
    GrabFoodExtractor(),
]

import email
import email.parser
import email.message
import email.policy

parser = email.parser.BytesParser(
    email.message.EmailMessage, policy=email.policy.default
)

import extractors.base_extractor
import title_classifier

# Warning: this script loads all the results into memory, might not be suitable for large datasets

# Initialize InstalledAppFlow with your client secret file
TOKEN_PICKLE = "token.pickle"
tc = title_classifier.EmailTitleClassifier(
    "trained/email_titles_nlp.keras", "trained/tv_layer.pkl"
)


def get_credentials():
    credentials = None

    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            )

            # Run the flow to obtain credentials
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(credentials, token)

    return credentials


# Convert the credentials to a format that aiogoogle can use
raw_creds = get_credentials()
user_creds = UserCreds(
    access_token=raw_creds.token,
    refresh_token=raw_creds.refresh_token,
    token_uri=raw_creds.token_uri,
    id_token=raw_creds.id_token,
)
client_creds = ClientCreds(
    client_id=raw_creds.client_id, client_secret=raw_creds.client_secret
)


def extract_domain(email):
    """Extracts the domain name from an email address.

    Args:
      email: The email address to extract the domain from.

    Returns:
      The domain name, or None if the email address is invalid.
    """
    match = re.search(r"@[\w.\-]+", email)
    if match:
        return match.group().lstrip("@")
    return None


async def fetch_email_data(gmail, message_id) -> list[TransactionData]:
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        try:
            msg = await aiogoogle.as_user(
                gmail.users.messages.get(userId="me", id=message_id, format="metadata")
            )
            headers = msg["payload"]["headers"]

            subject = next(
                (header["value"] for header in headers if header["name"] == "Subject"),
                "",
            )
            from_email = next(
                (header["value"] for header in headers if header["name"] == "From"), ""
            )
            from_domain = extract_domain(from_email)

            # Classify the email title
            [is_tx] = tc.predict([subject])
            if not is_tx:
                return []

            full_msg = await aiogoogle.as_user(
                gmail.users.messages.get(userId="me", id=message_id, format="raw")
            )

            # Try to go through all the extractors
            trxs = []

            # Load the email content
            data = parser.parsebytes(base64.urlsafe_b64decode(full_msg["raw"]))
            content = EmailContent(data)
            
            # Extract transactions
            
            for ex in exs:
                try:
                    if ex.match(content.title, content.from_email):
                        trxs.extend(ex.extract(content))
                except Exception as e:
                    print(f"Error while extracting transactions for {subject} from:{from_domain}: {e}")

            if not trxs:
                dump_path = f"dumped/{from_domain}-{message_id}.eml"
                print(
                    f"No transactions found in {subject} from:{from_domain}. Dumping the message to {dump_path}"
                )
                with open(dump_path, "wb") as f:
                    f.write(base64.urlsafe_b64decode(full_msg["raw"]))
            return trxs
        except HTTPError as e:
            if e.res.status_code == 429:
                print("Rate limit exceeded, waiting...")
                await asyncio.sleep(random.uniform(1, 10))
                return await fetch_email_data(gmail, message_id)
            else:
                raise e


async def extract_tx(gmail, w: csv.DictWriter, page_token=None):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        response = await aiogoogle.as_user(
            gmail.users.messages.list(userId="me", maxResults=500, pageToken=page_token)
        )

        messages = response.get("messages", [])
        next_page_token = response.get("nextPageToken", None)
        txs = []

        if not messages:
            return txs, next_page_token

        chunk_size = 48
        for i in range(0, len(messages), chunk_size):
            chunk = messages[i : i + chunk_size]
            tasks = [fetch_email_data(gmail, message["id"]) for message in chunk]
            chunk_txs = await asyncio.gather(*tasks)
            txs.extend(tx for txs in chunk_txs for tx in txs)
            
            # Write to disk
            for tx in txs:
                if tx.is_proper():
                    w.writerow(tx.to_formatted_dict())
                else:
                    print(f"Transaction {tx} is not proper")

            # Sleep to prevent hitting the rate limit (Gmail API limits to 50 requests per second for message.get)
            await asyncio.sleep(1)

    return txs, next_page_token


async def main():
    start_time = datetime.datetime.now()
    with open("email-extract.csv", "w", newline='') as f:
        fieldnames = ["Datetime", "Merchant Name", "Sub Category", "Category", "Amount", "Currency", "Transaction Type", "Payment Method", "Transaction ID", "Notes"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
            gmail = await aiogoogle.discover("gmail", "v1")

            extract_limit = 50
            extracted_count = 0
            next_page_token = None

            while extracted_count < extract_limit:
                titles, next_page_token = await extract_tx(gmail, w, next_page_token)
                extracted_count += len(titles)

                if next_page_token is None or extracted_count >= extract_limit:
                    break

                print(f"Extracted {extracted_count}/{extract_limit} emails so far...")
                print(f"Time elapsed: {datetime.datetime.now() - start_time} seconds")


# Run the main function
asyncio.run(main())
