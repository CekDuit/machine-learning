import asyncio
import datetime
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

# Initialize InstalledAppFlow with your client secret file
TOKEN_PICKLE = "token.pickle"


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


async def fetch_email_data(gmail, message_id):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        try:
            msg = await aiogoogle.as_user(
                gmail.users.messages.get(userId="me", id=message_id, format="metadata")
            )
            headers = msg["payload"]["headers"]

            subject = next(
                (header["value"] for header in headers if header["name"] == "Subject"), ""
            )
            from_email = next(
                (header["value"] for header in headers if header["name"] == "From"), ""
            )
            from_domain = extract_domain(from_email)
    
            return f"{subject} from:{from_domain}"
        except HTTPError as e:
            if e.res.status_code == 429:
                print("Rate limit exceeded, waiting...")
                await asyncio.sleep(random.uniform(1, 10))
                return await fetch_email_data(gmail, message_id)
            else:
                raise e


async def extract_titles(gmail, page_token=None):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        response = await aiogoogle.as_user(
            gmail.users.messages.list(userId="me", maxResults=500, pageToken=page_token)
        )

        messages = response.get("messages", [])
        next_page_token = response.get("nextPageToken", None)
        titles = []

        if not messages:
            return titles, next_page_token

        chunk_size = 48
        for i in range(0, len(messages), chunk_size):
            chunk = messages[i : i + chunk_size]
            tasks = [fetch_email_data(gmail, message["id"]) for message in chunk]
            chunk_titles = await asyncio.gather(*tasks)
            titles.extend(chunk_titles)
            
            # Sleep to prevent hitting the rate limit (Gmail API limits to 50 requests per second for message.get)
            await asyncio.sleep(1)

    return titles, next_page_token


async def main():
    start_time = datetime.datetime.now()
    
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        gmail = await aiogoogle.discover("gmail", "v1")

        extract_limit = 10000
        extracted_count = 0
        all_titles = []
        next_page_token = None

        while extracted_count < extract_limit:
            titles, next_page_token = await extract_titles(gmail, next_page_token)
            all_titles.extend(titles)
            extracted_count += len(titles)

            if next_page_token is None or extracted_count >= extract_limit:
                break

            print(f"Extracted {extracted_count}/{extract_limit} emails so far...")
            print(f"Time elapsed: {datetime.datetime.now() - start_time} seconds")

        print(all_titles[:10])

        # Turn into a CSV and download
        df = pd.DataFrame(all_titles, columns=["title"])
        df.to_csv("email-titles.csv", index=False)


# Run the main function
asyncio.run(main())
