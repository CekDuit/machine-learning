from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class MobaPayExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the MobaPay transaction receipt format.
        """
        return email_from == "mobapay@mail.mobapay.com" and "Payment Successful" in title
    
    def _extract_title(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract payment details based on the email title and content.
        """
        if "Payment Successful" in title:
            return self._extract_payment(email, title)
        else:
            raise ValueError("Unknown MobaPay email format")
        
    def _extract_payment(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the payment format.
        """
        trx = TransactionData()
        trx.currency = "IDR"

        # Extract general fields (Order No.)
        ref_match = re.search(r"Order No\.\s*[:\s]*([0-9]+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")

        # Extract payment time
        date_match = re.search(r"Payment Time:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("Date not found in email")

        # Extract recipient account (Username)
        recipient_match = re.search(r"Username:\s*([^\n]+)", email)
        trx.recipient_name = recipient_match.group(1) if recipient_match else "Unknown Recipient"

        # Extract description (Item Name)
        desc_match = re.search(r"Item Name:\s*([^\n]+)", email)
        if desc_match:
            description = desc_match.group(1)
            # If description contains a " + ", split it
            if " + " in description:
                trx.description = description.split(" + ")[0]  # Only take the first part before the " + "
            else:
                trx.description = description
        else:
            trx.description = "Unknown Description"

        # Extract payment details (Price)
        amount_match = re.search(r"Price:\s*([\d\.]+)\.\.(\d{2})\s*IDR", email)
        if amount_match:
            # Combine the parts of the amount (before and after the "..")
            whole_number = amount_match.group(1)  # e.g. "12.000"
            fractional_part = amount_match.group(2)  # e.g. "00"

            # Remove internal dots from the whole number part and combine with the fractional part
            whole_number = whole_number.replace(".", "")  # Remove dots like "12.000" -> "12000"

            # Create the decimal value by inserting the fractional part
            price = f"{whole_number}.{fractional_part}"

            # Parse it into Decimal
            trx.amount = Decimal(price)
        else:
            raise ValueError("Amount not found in email")

        # Extract payment method
        payment_method_match = re.search(r"Payment Methods:\s*([^\n]+)", email)
        trx.payment_method = payment_method_match.group(1) if payment_method_match else "Unknown Payment Method"

        return [trx]