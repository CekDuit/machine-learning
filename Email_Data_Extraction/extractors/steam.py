from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime
import locale


class SteamExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "steam purchase" in title.lower() and "noreply@steampowered.com" in email_from.lower()

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # You've earned Steam Points
        # Fallout 4: Game of the Year Edition
        # Subtotal (excl. VAT): Rp 119,820
        # VAT at 11%: Rp 13,180
        # Total: Rp 133,000
        # NBA 2K24 Kobe Bryant Edition
        # Subtotal (excl. VAT): Rp 94,991
        # VAT at 11%: Rp 10,449
        # Total: Rp 105,440
        # Account name: darkiki27
        # Invoice: 3869230398088464184
        # Date issued: 17 Apr, 2024 @ 8:58pm WIB
        # Billing address: ...
        # Total: Rp 238,440
        # Payment method: Visa


        trx = TransactionData()
        trx.is_incoming = False
        payment_method_match = re.search(r"Payment method:\s*(\w+)", email)
        trx.payment_method = payment_method_match.group(1).strip()

        # Split per line and match
        total_match = re.search(r"Your total for this transaction:\s*([A-Za-z]+)\s*([\d\s,\.]+)", email)
        trx.currency = total_match.group(1).strip()

        amount = total_match.group(2).replace(" ", "").replace(",", ".")
        trx.amount = Decimal(amount)
        if trx.currency == "Rp":
            trx.currency = "IDR"

        trx.description = ""

        trx.merchant = "Steam"
        
        date_match = re.search(r"Date issued:\s*(\d{1,2} \w{3}, \d{4}) @ (\d{1,2}:\d{2}[a-z]{2})", email)
        date_str = date_match.group(1)
        time_str = date_match.group(2)
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8') 
        combined_str = f"{date_str} {time_str}"
        trx.date = datetime.datetime.strptime(combined_str, "%d %b, %Y %I:%M%p") 
        
        trx.trx_id = re.search(r"Invoice:\s*(\S+)", email).group(1)

        return [trx]