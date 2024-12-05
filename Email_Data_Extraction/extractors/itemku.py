from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime
import locale

class ItemkuExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return (
        "pembayaran pesanan" in title.lower() and
        "telah kami terima" in title.lower() and
        "no-reply@itemku.com" in email_from.lower()
    )
    
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
        payment_method_match = re.search(r"Biaya Layanan\s*(\w+)", email)
        trx.payment_method = payment_method_match.group(1).strip() if payment_method_match else "Unknown"
        
        # total_match = re.search(r"Total Pembayaran\s*(Rp\.\s*[\d,\.]+)", email)
        # trx.currency = "IDR" 
        # amount_str = total_match.group(1).replace(".", "").replace(",", ".").strip()
        # amount_str = "".join(c for c in amount_str if c.isdigit() or c == ".")
        # trx.amount = Decimal(amount_str)

        total_match = re.search(r"Total Pembayaran\s*([^\d\s]+)\.?\s*([\d,\.]+)", email)
        currency_symbol = total_match.group(1).strip()
        amount_str = total_match.group(2).replace(".", "").replace(",", ".").strip()
        if currency_symbol == "Rp." or currency_symbol == "Rp":
            trx.currency = "IDR"
        else:
            trx.currency = currency_symbol  

        amount_str = "".join(c for c in amount_str if c.isdigit() or c == ".")
        trx.amount = Decimal(amount_str)
        
        description_match = re.search(r"(Akun .+)", email)
        trx.description = description_match.group(1) if description_match else ""
        
        trx.merchant = "Itemku"
        
        date_match = re.search(r"Tanggal transaksi:\s*(\d{1,2} \w{3} \d{4}) pukul (\d{2}:\d{2}:\d{2})", email)
        date_str = f"{date_match.group(1)} {date_match.group(2)}"
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y %H:%M:%S")
        
        trx_id_match = re.search(r"No. Transaksi:\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else ""
        
        return [trx]