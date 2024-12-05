from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class JagoExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return (
        "kamu telah membayar" in title.lower() and
        "noreply@jago.com" in email_from.lower()
    )

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
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
        trx.currency = currency_amount_match.group(1).strip()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", ""))

        trx.description = ""  # Gak ada deskripsi di bank jago
        merchant_match = re.search(r"Ke\s*(.+)", email)
        trx.merchant = merchant_match.group(1)

        date_match = re.search(r"Tanggal transaksi\s*(\d{1,2} \w+ \d{4} \d{2}:\d{2})", email)
        date_str = date_match.group(1)
        date_str = re.sub(r'\s+[A-Za-z]+$', '', date_str)
        trx.date = datetime.datetime.strptime(date_str, "%d %B %Y %H:%M")

        trx.trx_id = trx.date.strftime("%Y%m%d%H%M")

        return [trx]