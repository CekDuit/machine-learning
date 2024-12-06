import re
from decimal import Decimal
from typing import Optional
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class OCBCExtractor(BaseExtractor):

    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OCBC payment receipt format.
        """
        return title in ["Successful Bill Payment", "TRANSFER DANA MASUK BI-FAST"] and email_from == "onlinetransaction@ocbc.id"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract transactions from the OCBC email content.
        """
        email = content.get_plaintext()

        # Normalize whitespace
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "OCBC"
        trx.extra_data = {}

        if self._is_extract_transfer(email):
            self._extract_transfer(email, trx)
        elif self._is_extract_top_up(email):
            self._extract_top_up(email, trx)

        return [trx]
    
    def _is_extract_transfer(self, email: str) -> bool:
        """
        Check if the email is a transfer receipt.
        """
        return "TRANSFER DANA" in email
    
    def _is_extract_top_up(self, email: str) -> Optional[bool]:
        """
        Check if the email is in the 'Successful Bill Payment' format for top-up.
        """
        if "PAYMENT AMOUNT" in email and "TO" in email:
            return True
        return False
    
    def _extract_transfer(self, email: str, trx: TransactionData) -> None:
        """
        Extract the transfer details from the OCBC email.
        """

        # 1. Extract Sender Bank
        sender_bank_pattern = r"Bank Pengirim\s*:\s*(.*?)\s*(?=\n|Nama Pengirim)"
        sender_bank_match = re.search(sender_bank_pattern, email)
        if sender_bank_match:
            trx.extra_data['sender_bank'] = sender_bank_match.group(1)

        # 2. Extract Sender Name
        sender_name_pattern = r"Nama Pengirim\s*:\s*(.*?)\s*(?=\n|No Rekening Pengirim)"
        sender_name_match = re.search(sender_name_pattern, email)
        if sender_name_match:
            trx.extra_data['sender_name'] = sender_name_match.group(1)

        # 3. Extract Sender Account
        sender_account_pattern = r"No Rekening Pengirim\s*:\s*(\d+)\s*"
        sender_account_match = re.search(sender_account_pattern, email)
        if sender_account_match:
            trx.extra_data['sender_account'] = sender_account_match.group(1)

        # 4. Extract Nominal (Amount)
        nominal_pattern = r"Nominal\s*:\s*Rp\s*([\d\.]+),(\d{2})\s*"
        nominal_match = re.search(nominal_pattern, email)
        if nominal_match:
            # Remove thousands separator (.) and ignore the decimal part
            nominal_value = nominal_match.group(1).replace(".", "")  # Remove periods
            trx.amount = Decimal(nominal_value)  # Convert to Decimal
            trx.currency = "IDR"  # Set currency


        # 5. Extract Receiver Bank
        receiver_bank_pattern = r"Bank Penerima\s*:\s*(.*?)\s*(?=\n|Nama Penerima)"
        receiver_bank_match = re.search(receiver_bank_pattern, email)
        if receiver_bank_match:
            trx.extra_data['receiver_bank'] = receiver_bank_match.group(1)

        # 6. Extract Receiver Name
        receiver_name_pattern = r"Nama Penerima\s*:\s*(.*?)\s*(?=\n|No Rekening Penerima)"
        receiver_name_match = re.search(receiver_name_pattern, email)
        if receiver_name_match:
            trx.extra_data['receiver_name'] = receiver_name_match.group(1)

        # 7. Extract Receiver Account
        receiver_account_pattern = r"No Rekening Penerima\s*:\s*(\d+)\s*"
        receiver_account_match = re.search(receiver_account_pattern, email)
        if receiver_account_match:
            trx.extra_data['receiver_account'] = receiver_account_match.group(1)

        # 8. Extract Transaction Date
        date_pattern = r"Tanggal Transaksi\s*:\s*(\d{2} \w+ \d{4})\s*"
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %B %Y")

        # 9. Extract Transaction Time
        time_pattern = r"Waktu Transaksi\s*:\s*(\d{2}:\d{2}:\d{2})\s*"
        time_match = re.search(time_pattern, email)
        if time_match:
            # Combine the date and time into a full datetime object
            if trx.date:
                time_str = time_match.group(1)
                trx.date = datetime.combine(trx.date, datetime.strptime(time_str, "%H:%M:%S").time())

        # Description (can be customized if needed, currently we set it as 'Transfer Dana')
        trx.description = "Transfer Dana"

    def _extract_top_up(self, email: str, trx: TransactionData) -> Optional[bool]:
        """
        Extract details from the top-up email format.
        """
        # Extract sender name
        sender_name_pattern = r"FROM\s*(.*?)\s*IDR"
        sender_name_match = re.search(sender_name_pattern, email)
        if sender_name_match:
            trx.extra_data['sender_name'] = sender_name_match.group(1).strip()

        # Extract sender account number
        sender_account_pattern = r"IDR\s*(\S+)"
        sender_account_match = re.search(sender_account_pattern, email)
        if sender_account_match:
            trx.extra_data['sender_account'] = sender_account_match.group(1).strip()

        # Extract recipient name
        receiver_name_pattern = r"TO\s*(.*?)\s*\d{10,}"
        receiver_name_match = re.search(receiver_name_pattern, email)
        if receiver_name_match:
            trx.extra_data['receiver_name'] = receiver_name_match.group(1).strip()

        # Extract receiver account number
        receiver_account_pattern = r"TO\s*.*?(\d{10,})"
        receiver_account_match = re.search(receiver_account_pattern, email)
        if receiver_account_match:
            trx.extra_data['receiver_account'] = receiver_account_match.group(1).strip()

        # Extract the amount (remove 'IDR', commas, and parse the number)
        amount_pattern = r"IDR\s*([\d,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            # Remove commas and convert to Decimal
            amount_str = amount_match.group(1).replace(",", "")
            trx.amount = Decimal(amount_str)
            # Set currency
            trx.currency = "IDR"

        # Extract transaction date
        date_pattern = r"PAYMENT DATE:\s*(\d{2} \w+ \d{4} \d{2}:\d{2}:\d{2})"
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %b %Y %H:%M:%S")

        # Set merchant name
        trx.merchant = trx.extra_data['receiver_name']

        # Set description
        trx.description = "Top-up Payment"

    def _extract_value(self, pattern: str, email: str) -> Optional[str]:
        """
        Helper function to extract the first match of a given regex pattern from the email content.
        """
        match = re.search(pattern, email)
        return match.group(1) if match else None
