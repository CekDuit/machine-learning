import re
from decimal import Decimal
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class EGExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the EG transaction receipt format.
        """
        return email_from == "help@acct.epicgames.com" and "Your Epic Games Receipt" in title
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email_text = content.get_plaintext()

        # Initialize a TransactionData object
        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "e-wallet"
        trx.currency = "IDR"

        # Extract invoice ID
        trx_id_pattern = r"INVOICE ID:\s*([A-Za-z0-9]+)"
        trx_id_match = re.search(trx_id_pattern, email_text)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # Regex pattern for Description (Game Name), Publisher, and Amount (Price)
        description_pattern = r"Price:\s*([A-Za-z0-9\s:]+)\s+([A-Za-z0-9\s\.]+)\s+IDR\s*Rp\s([\d,\.]+)"
        # Applying the regex to extract values
        description_match = re.search(description_pattern, email_text)
        if description_match:
            trx.description = description_match.group(1) + " " + description_match.group(2)  # Description (Game Name + Publisher)
            trx.amount = Decimal(description_match.group(3).replace(",", ""))  # Amount (Price)

        # Regex for Order Date and Source
        order_date_pattern = r"Source:\s*([A-Za-z\s]+)\s+([A-Za-z]+\s\d{1,2},\s\d{4})\s*(.*)"
        order_date_match = re.search(order_date_pattern, email_text)
        if order_date_match:
            order_date_str = order_date_match.group(2)
            trx.merchant = order_date_match.group(3).strip()
            # Convert order date to yyyy-MM-dd format
            trx.date = datetime.strptime(order_date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        
        # Return the populated TransactionData object
        return [trx]