import re
from decimal import Decimal
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class MobaPayExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the Mobapay payment confirmation format.
        """
        return "Payment Successful" in title and "mobapay@mail.mobapay.com" in email_from
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.merchant = "Mobapay"
        trx.fees = 0

        # Extract Order No.
        order_no_match = re.search(r"Order No\.\:\s*(\S+)", email)
        if order_no_match:
            trx.trx_id = str(order_no_match.group(1))

        # Extract Payment Time
        payment_time_match = re.search(r"Payment Time:\s*(\S+\s\d{2}:\d{2}:\d{2} \(\w{3}\))", email)
        if payment_time_match:
            trx.date = datetime.datetime.strptime(payment_time_match.group(1), "%Y-%m-%d %H:%M:%S (%Z)")

        # Extract Item Name
        item_name_match = re.search(r"Item Name:\s*(.*?)\s*Currency", email)
        if item_name_match:
            trx.description = item_name_match.group(1).strip()

        # Extract Currency (should be IDR based on the format)
        currency_match = re.search(r"Currency:\s*(\S+)", email)
        if currency_match:
            trx.currency = currency_match.group(1)

        # Extract Price
        price_match = re.search(r"Price:\s*([\d,]+)", email)
        if price_match:
            trx.amount = Decimal(price_match.group(1).replace(",", ""))

        # Extract Payment Methods
        payment_methods_match = re.search(r"Payment Methods:\s*(.*?)\s*Subtotal", email)
        if payment_methods_match:
            trx.payment_method = payment_methods_match.group(1).strip()

        return [trx]