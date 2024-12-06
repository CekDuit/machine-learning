from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class GooglePlayExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "google play order" in title.lower() and "googleplay-noreply@google.com" in email_from.lower()

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # Order number: GPA.3335-0097-8360-50910
        # Order date: 2 Dec 2024 18:20:35 GMT+7
        # Your account: fxsurya27@gmail.com
        # Item            Price
        # True Premium (xxxxx) Rp 39.000,00/month
        # Auto-renewing subscription
        # Tax: Rp 2.090,00
        # Total: Rp 41.090,00/month
        # Payment method: ShopeePay: **** 6235

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = re.search(r"Payment method:\s*([A-Za-z]+)", email).group(1).strip()

        # Split per line and match
        currency_amount_match = re.search(r"Total\s*:?[\s]*(\D+)\s*([\d.,]+)", email)
        trx.currency = currency_amount_match.group(1).strip()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        else:
            trx.currency = trx.currency  
        amount = currency_amount_match.group(2)
        amount_cleaned = amount.replace(".", "").replace(",", ".")
        trx.amount = int(Decimal(amount_cleaned)) 

        trx.description = ""  # Gak ada deskripsi di google play 
        trx.merchant = "Google Play"

        date_str = re.search(r"Order date\s*:\s*(.+)", email).group(1)
        date_str_cleaned = re.sub(r"\s*GMT[\+\-]\d+", "", date_str).strip()
        trx.date = datetime.datetime.strptime(date_str_cleaned, "%d %b %Y %H:%M:%S")

        order_number_match = re.search(r"Order number\s*:\s*(GPA\.\d{4}-\d{4}-\d{4}-\d{5})", email)
        trx.trx_id = order_number_match.group(1)

        return [trx]