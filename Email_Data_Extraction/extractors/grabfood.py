from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class GrabFoodExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "Your Grab E-Receipt" and email_from == "no-reply@grab.com"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        pt = content.get_plaintext()
        
        if not "Selamat menikmati makanan Anda!" in pt:
            return []

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "OVO" if "OVO" in pt else "Cash"

        trx.merchant = re.search(r"Pesanan Dari:\s*\n(.+)", pt).group(1).strip()
        currency, amount = re.search(r"TOTAL \(INCL\. TAX\)\s+(\w+) (\d+)", pt).groups()
        
        trx.currency = "IDR" if currency == "Rp" else currency
        trx.amount = Decimal(amount.replace(".", "").replace(",", ""))
    
        trx.trx_id = re.search(r"Pesanan ID\s+\n(.+)", pt).group(1).strip()
        trx.description = "GrabFood Order"
        date_str = re.search(r"(\d{2} \w+ \d{2} \d{2}:\d{2})", pt).group(0)
        trx.date = datetime.datetime.strptime(date_str, "%d %b %y %H:%M")
        
        return [trx]
