from decimal import Decimal
from base_extractor import BaseExtractor, TransactionData
import re
import datetime


class JagoExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "Kamu telah membayar" in title and email_from == "noreply@jago.com"

    def extract(self, title: str, email_from: str, email: str) -> list[TransactionData]:
        # Example format:
        # Dari           MA • 1039984xxxxx
        # Ke             DODO
        # BCA • 92385xx182
        # Jumlah        Rp25.000
        # Tanggal transaksi 23 February 2024 14:40 WIB

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Jago"

        # Split per line and match
        currency_amount_match = re.search(
            r"Jumlah\s*:?[\s]*([A-Za-z]+)\s*([\d,\.]+)", email
        )
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(",", ""))

        trx.description = "Bank Jago Transaction"  # Gak ada deskripsi di bank jago
        trx.merchant = re.search(r"Ke\s*:\s*(.+)", email).group(1)
        date_str = re.search(r"Tanggal transaksi\s*:\s*(.+)", email).group(1)
        trx.date = datetime.datetime.strptime(
            date_str.replace(" WIB", ""), "%d %B %Y %H:%M"
        )
        trx.trx_id = trx.date.strftime("%Y%m%d%H%M")

        return [trx]
