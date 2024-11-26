from decimal import Decimal
from base_extractor import BaseExtractor, TransactionData
import re
import datetime


class SeaBankExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "Notifikasi Transfer SeaBank" in title.lower() and email_from == "seabank@seabank.com"

    def extract(self, title: str, email_from: str, email: str) -> list[TransactionData]:
        # Example format:
        # Waktu Transaksi : 22 Nov 2024 18:48
        # Jenis Transaksi : Real Time (BI-FAST)
        # Transfer Dari : BOBO DELONA-XXXXXXXXX3859
        # Rekening Tujuan : JAGO-XXXXXXXXX2337
        # Jumlah : Rp200.000
        # No. Referensi : 202411224350224969367

        trx = TransactionData()
        trx.is_incoming = False 
        trx.payment_method = "SeaBank" 

        # Split per line and match
        amount = re.search(r"Jumlah\s*:\s*Rp([\d,\.]+)", email).group(1)
        trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(",", ""))

        trx.description = "Seabank Transaction"  # Gak ada deskripsi di bank Seabank
        trx.merchant = re.search(r"Rekening Tujuan\s*:\s*(.+)", email).group(1)
        trx.trx_id = re.search(r"No\. Referensi\s*:\s*(\d+)", email).group(1)
        date_str = re.search(r"Waktu Transaksi\s*:\s*(\d{2} \w{3} \d{4} \d{2}:\d{2})", email).group(1)
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y %H:%M")

        return [trx]
