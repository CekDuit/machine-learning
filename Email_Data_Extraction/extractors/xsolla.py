from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class XsollaExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the Xsolla transaction receipt format.
        """
        return email_from == "mailer@xsolla" and "Your receipt" in title
    
    def _extract_title(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract payment details based on the email title and content.
        """
        if "receipt" in title:
            return self._extract_payment(email, title)
        else:
            raise ValueError("Unknown Xsolla email format")
        
    def _extract_payment(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the payment format.
        """
        trx = TransactionData()
        trx.currency = "IDR"
        
        # Extract general fields

        # Extract merchant name (flexible regex for various merchant names)
        merchant_match = re.search(r"Product -\s*([^\n]+)", email)
        trx.merchant = merchant_match.group(1) if merchant_match else "Unknown Merchant"

        # Flexible regex for Transaction number, allowing for different formatting or punctuation
        ref_match = re.search(r"Transaction\s*(?:number|ID)?\s*[:\-]?\s*(\S+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")
        
        date_match = re.search(r"Transaction date\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", email)
        if date_match:
            print(f"Date found: {date_match.group(1)}")  # Debug print
            trx.date = datetime.datetime.strptime(date_match.group(1), "%m/%d/%Y")
        else:
            print(f"Date not found in email: {email}")  # Debug print for email content
            raise ValueError("Date not found in email")

        # Extract description
        desc_match = re.search(r"Purchase description \s*(.+)", email)
        trx.description = desc_match.group(1) if desc_match else "Unknown Description"

        # Extract payment details (Total amount)
        total_match = re.search(r"Subtotal\s*Rp\s*([\d\s,]+(?:\.\d{1,2})?)", email)
        if total_match:
            print(f"Amount found: {total_match.group(1)}")  # Debugging print
            amount_str = total_match.group(1)
            # Remove spaces or commas to normalize the number format before conversion to Decimal
            amount_str = amount_str.replace(" ", "").replace(",", "")
            print(f"Amount after cleaning: {amount_str}")  # Debugging print
            trx.amount = Decimal(amount_str)
        else:
            raise ValueError("Total amount (Subtotal) not found in email")
        
        fees_match = re.search(r"Including 11% VAT : \s*([\d\.]+)", email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1))
        
        return [trx]