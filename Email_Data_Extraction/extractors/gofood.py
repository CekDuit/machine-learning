from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class GoFoodExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "Gojek" in title.lower() and "no-reply@invoicing.gojek.com" in email_from.lower()

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # gofood
        # Wednesday, 2 August 2023
        # Order ID: F-2178695239
        # Hi KIKO,
        # Thanks for ordering GoFood
        # Total paid: Rp57.000
        # Order details:
        # 3 Mie Gacoan IV 0 @Rp14.000 Rp42.000
        # 1 Udang Rambutan @Rp13.000 Rp13.000
        # Total Price: Rp55.000
        # Delivery fee: Rp13.000
        # Other fee(s): Rp3.000
        # Discounts: -Rp14.000
        # Total payment: Rp57.000
        # Paid with GoPay: Rp50.000
        # Paid with Cash: Rp7.000
        # Delivery details:
        # Zainur Rahman
        # Delivered on 2 August 2023 at 13:47
        # Distance: 3.9 km
        # Delivery time: 45 mins

        # Create transaction object
        trx = TransactionData()
        trx.is_incoming = False
        trx.merchant = "GoFood"
        trx.currency = "IDR"

        total_payment_match = re.search(r"Total payment: Rp([\d.]+)", email)
        if total_payment_match:
            trx.amount = Decimal(total_payment_match.group(1).replace('.', ''))

        gopay_match = re.search(r"Paid with GoPay: Rp([\d.]+)", email)
        cash_match = re.search(r"Paid with Cash: Rp([\d.]+)", email)
        
        payment_methods = []
        if gopay_match:
            payment_methods.append("GoPay")
        if cash_match:
            payment_methods.append("Cash")
        
        trx.payment_method = " + ".join(payment_methods)

        date_match = re.search(r"Delivered on (\d+ \w+ \d{4}) at (\d{2}:\d{2})", email)
        if date_match:
            trx.date = datetime.datetime.strptime(
                f"{date_match.group(1)} {date_match.group(2)}", 
                "%d %B %Y %H:%M"
            )

        match = re.search(r"Order ID:\s*(\S+)", email)
        trx.trx_id = match.group(1)

        return [trx]