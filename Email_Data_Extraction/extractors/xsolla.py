import re
from decimal import Decimal
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class XsollaExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the Xsolla purchase format.
        """
        return email_from == "mailer@xsolla.com" and "Your Receipt No." in title
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        # Debugging: Print cleaned-up email content to verify
        print("Cleaned email content:")
        print(email)
        print("\n" + "-"*50 + "\n")

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Xsolla"

        # Extract product name
        product_match = re.search(r"Product\s*-\s*(.*?)\s*Company", email)
        if product_match:
            trx.description = product_match.group(1).strip()

        # Extract company name
        company_match = re.search(r"Company\s+([A-Za-z0-9\s\(\),\.]+(?:\sInc\.\s?))\s*", email)
        if company_match:
            trx.merchant = company_match.group(1).strip()

        # Extract transaction number
        trx_id_match = re.search(r"Transaction number\s*(\d+)", email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # Extract transaction date
        date_match = re.search(r"Transaction date\s*(\d{2}/\d{2}/\d{4})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%m/%d/%Y")

        # Extract total
        total_match = re.search(r"Total\s+Rp([\d\s,\.]+)", email)
        if total_match:
            trx.amount = Decimal(total_match.group(1).replace(" ", "").replace(",", "").strip())

        # Extract VAT amount
        vat_match = re.search(r"Including\s+11%\s+VAT\s*:\s*Rp([\d\s,\.]+)", email)
        if vat_match:
            trx.fees = Decimal(vat_match.group(1).replace(" ", "").replace(",", "").strip())

        return [trx]