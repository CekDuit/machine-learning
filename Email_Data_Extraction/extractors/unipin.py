from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class UniPinExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the UniPin transaction receipt format.
        """
        return email_from == "cs@unipin.com" and "Receipt" in title
    
    def _extract_title(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract payment details based on the email title and content.
        """
        if "Receipt" in title:
            return self._extract_payment(email, title)
        else:
            raise ValueError("Unknown UniPin email format")
    
    def _extract_payment(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the payment format.
        """
        trx = TransactionData()
        trx.currency = "IDR"
        
        # Extract general fields
        ref_match = re.search(r"Nomor Transaksi\s*(S\d+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")
        
        # Extract description
        voucher_match = re.search(r"Tipe Voucher\s*[:\s]*([^\n]+)", email)
        if voucher_match:
            trx.description = voucher_match.group(1).strip()  # Capture the value after "Tipe Voucher"
        else:
            trx.description = "Unknown Description"
        
        # Extract payment details
        amount_match = re.search(r"Nominal Transaksi\s*IDR\s([\d\.]+)", email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", ""))
        else:
            raise ValueError("Amount not found in email")
        
        return [trx]