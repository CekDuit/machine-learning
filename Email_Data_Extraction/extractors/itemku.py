from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime
import locale

class ItemkuExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "itemku" in title.lower() and "no-reply@itemku.com" in email_from.lower()
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # You've earned itemku Points
        # Akun pubg lvl 10 up + gmail + victor (PUBG Mobile Indonesia)
        # Subtotal: Rp 15.000
        # Biaya Layanan QRIS - QR CODE: Rp 1.107
        # Total: Rp 16.107
        # Account name: Fransiscuscus Xaverius Surya Darmawan
        # Invoice: TR00128200657
        # Date issued: 12 Aug, 2024 @ 23:43:54
        # Total: Rp 16.107
        # Payment method: QRIS

        trx = TransactionData()
        trx.is_incoming = False
        payment_method_match = re.search(r"Payment method:\s*(\w+)", email)
        trx.payment_method = payment_method_match.group(1).strip() if payment_method_match else "Unknown"
        
        total_match = re.search(r"Total:\s*([A-Za-z]+)\s*([\d,\.]+)", email)
        trx.currency = "IDR" if total_match.group(1).strip() == "Rp" else total_match.group(1).strip()
        amount = total_match.group(2).replace(".", "").replace(",", ".")
        trx.amount = Decimal(amount)
        
        description_match = re.search(r"(Akun .+)", email)
        trx.description = description_match.group(1) if description_match else ""
        
        trx.merchant = "Itemku"
        
        date_match = re.search(r"Date issued:\s*(\d{1,2} \w{3}, \d{4}) @ (\d{2}:\d{2}:\d{2})", email)
        trx.date = datetime.datetime.strptime(f"{date_match.group(1)} {date_match.group(2)}", "%d %b, %Y %H:%M:%S")
        trx_id_match = re.search(r"Invoice:\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else ""
        
        return [trx]