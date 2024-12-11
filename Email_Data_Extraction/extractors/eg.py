import re
from decimal import Decimal
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class EGExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the EG transaction receipt format.
        """
        return title.startswith("Your Epic Games Receipt ") and email_from == "help@accts.epicgames.com" 
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Initialize a TransactionData object
        trx = TransactionData()
        trx.is_incoming = False
        trx.currency = "IDR"

        # Extract invoice ID
        trx_id_pattern = r"INVOICE ID:\s*([A-Za-z0-9]+)"
        trx_id_match = re.search(trx_id_pattern, email)
        if trx_id_match:
            trx.trx_id = str(trx_id_match.group(1))

        # Regex pattern for Description (Game Name), Publisher, and Amount (Price)
        #description_pattern = r"Price:\s*([A-Za-z0-9\s:]+)\s+([A-Za-z0-9\s\.]+)\sIDR\s*Rp\s([\d,]+)"
        description_pattern = r"Price:\s*([^\d]+)\s+([\w\s.,&'-]+)\s+Rp([\d,]+(?:\.\d{2})?)\s*IDR"
        # Applying the regex to extract values
        description_match = re.search(description_pattern, email)
        if description_match:
            trx.description = (description_match.group(1) + " " + description_match.group(2)).strip()  # Description (Game Name + Publisher)
            trx.amount = Decimal(description_match.group(3).replace(".00", "").replace(",", ""))  # Amount (Price)
            trx.fees = 0  # No fees for EG transactions

        # Regex for Order Date and Source
        order_date_pattern = r"Source:\s*([A-Za-z\s]+)\s+([A-Za-z]+\s\d{1,2},\s\d{4})\s*(.*)"
        order_date_match = re.search(order_date_pattern, email)
        if order_date_match:
            order_date_str = order_date_match.group(2)
            trx.merchant = order_date_match.group(3).strip()
            # Convert order date to yyyy-MM-dd format
            trx.date = datetime.strptime(order_date_str, "%B %d, %Y").strftime("%Y-%m-%d %H:%M:%S")

        # Extract payment method
        if "PAID FROM" in email:
            payment_method_pattern = r"PAID FROM:\s*([A-Za-z]+)\[IDR\]"
            payment_method_match = re.search(payment_method_pattern, email)
            if payment_method_match:
                trx.payment_method = payment_method_match.group(1)
        else:
            trx.payment_method = "-"
        
        # Return the populated TransactionData object
        return [trx]