from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class EGExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the EG transaction receipt format.
        """
        return email_from == "help@acct.epicgames.com" and "Receipt" in title
    
    def _extract_title(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract payment details based on the email title and content.
        """
        if "Your Epic Games Receipt" in title:
            return self._extract_payment(email, title)
        else:
            raise ValueError("Unknown EG email format")
    
    def _extract_payment(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the Payment format.
        """
        trx = TransactionData()
        trx.currency = "IDR"
        
        # Extract general fields
        ref_match = re.search(r"INVOICE ID:\s*(.+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")
        
        date_match = re.search(r"Order Date:\s*(\w+ \d{1,2}, \d{4})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%B %d, %Y")
        else:
            raise ValueError("Date not found in email")

        # Extract sender name
        sender_match = re.search(r"Source:\s*(.+)", email)
        trx.sender_name = sender_match.group(1) if sender_match else "Unknown Sender"
        
        # Extract recipient name
        recipient_match = re.search(r"Bill To:\s*(.+)", email)
        trx.recipient_name = recipient_match.group(1) if recipient_match else "Unknown Recipient"

        # Extract merchant
        publisher_match = re.search(r"Publisher:\s*(.+)", email)
        trx.merchant = publisher_match.group(1) if publisher_match else "Unknown Merchant"

        # Extract description
        desc_match = re.search(r"Description: \s*(.+)", email)
        trx.description = desc_match.group(1) if desc_match else "Unknown Merchant"
        
        # Extract payment details
        amount_match = re.search(r"Price:\s*Rp([\d,\.]+)\s*IDR", email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1))
        else:
            raise ValueError("Amount not found in email")
        
        return [trx]