from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class GoFoodExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        valid_titles = [
            "your food order",
            "pesanan makanan anda"
        ]
        valid_emails = [
            "no-reply@invoicing.gojek.com"
            # "m320b4ky1551@bangkit.academy"
        ]
        is_title_valid = any(valid_title in title.lower() for valid_title in valid_titles)
        is_email_valid = any(valid_email in email_from.lower() for valid_email in valid_emails)

        return is_title_valid and is_email_valid

        # return "your food order" in title.lower() and "no-reply@invoicing.gojek.com" in email_from.lower()

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

        total_payment_match = re.search(r"Total (payment|pembayaran)\s*Rp([\d.]+)", email)
        trx.amount = Decimal(total_payment_match.group(2).replace('.', ''))

        payment_match = re.findall(r"(?:Paid with|Bayar pakai)\s+([A-Za-z\s]+)(?=\s+Rp|$)", email)

        payment_methods = []
        payment_methods.extend(payment_match)
        trx.payment_method = " + ".join(payment_methods)
        
        trx.description = ""

        bulan_map = {
            "Januari": "January", "Februari": "February", "Maret": "March",
            "April": "April", "Mei": "May", "Juni": "June",
            "Juli": "July", "Agustus": "August", "September": "September",
            "Oktober": "October", "November": "November", "Desember": "December"
        }

        date_match = re.search(r"(?:Delivered on|Diantarkan)\s+(\d+ \w+ \d{4}) at (\d{2}:\d{2})", email)
        if date_match:
            date_str = date_match.group(1)
            time_str = date_match.group(2)
            for indo, eng in bulan_map.items():
                date_str = date_str.replace(indo, eng)
            trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %B %Y %H:%M")

        match = re.search(r"(?:Order ID|ID pesanan):\s*(\S+)", email)
        trx.trx_id = match.group(1)

        return [trx]