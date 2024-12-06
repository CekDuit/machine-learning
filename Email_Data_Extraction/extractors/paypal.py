from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime
import locale


class PaypalExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        valid_titles = [
            "anda mengirim pembayaran",
            "anda telah menerima"
        ]
        valid_emails = [
            "service@intl.paypal.com"
            # "m320b4ky1551@bangkit.academy"
        ]
        is_title_valid = any(valid_title in title.lower() for valid_title in valid_titles)
        is_email_valid = any(valid_email in email_from.lower() for valid_email in valid_emails)

        return is_title_valid and is_email_valid

        # return "Paypal" in title.lower() and "service@intl.paypal.com" in email_from.lower()

    def extractPembayaran(self, content: EmailContent) -> list[TransactionData]:
        email = content
        # Example format:
        # Anda mengirim $2,00 USD ke asukti
        # CATATAN ANDA UNTUK asukti asukti
        # “Transfer Jajan”
        # Perincian Transaksi
        # ID transaksi: 49S77625NF073893R
        # Tanggal transaksi: 1 Mei 2023
        # Pembayaran terkirim: $2,00 USD
        # Biaya: $0,00 USD
        # Dibayar dengan: Saldo PayPal (USD)
        # Anda membayar: $2,00 USD

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Paypal"

        # Split per line and match
        currency_amount_match = re.search(r"Pembayaran terkirim\s*\$(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(\w+)", email)
        trx.currency = currency_amount_match.group(2).strip()
        amount = currency_amount_match.group(1).replace(".", "").replace(",", ".")  
        trx.amount = Decimal(amount) 

        description_match = re.search(r"CATATAN ANDA UNTUK.*?\n\s*\n\s*(.+?)\n", email, re.DOTALL)
        trx.description = description_match.group(1).strip() if description_match else ""

        trx.merchant = "Paypal"
        date_match = re.search(r"Tanggal transaksi\s*\n\s*(.+)", email)
        date_str = date_match.group(1).strip()
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y")

        trx_id_match = re.search(r"ID transaksi\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        return [trx]
    
    def extractPenerimaan(self, content: EmailContent) -> list[TransactionData]:
        email = content
        # Example format:
        # Run Jie Soo telah mengirim $2,50 USD kepada Anda
        # Perincian Transaksi
        # ID transaksi: 1JE26965PL263253S
        # Tanggal transaksi: 12 Mei 2023
        # Jumlah yang diterima: $2,50 USD
        # Biaya: $0,41 USD
        # Total: $2,09 USD

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Paypal"

        # Split per line and match
        currency_amount_match = re.search(r"Jumlah yang diterima\s*\$(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(\w+)", email)
        trx.currency = currency_amount_match.group(2).strip()
        amount = currency_amount_match.group(1).replace(".", "").replace(",", ".")  
        trx.amount = Decimal(amount) 

        description_match = re.search(r"CATATAN.*?\n\s*\n\s*(.+?)\n", email, re.DOTALL)
        trx.description = description_match.group(1).strip() if description_match else ""

        trx.merchant = "Paypal"
        date_match = re.search(r"Tanggal transaksi\s*\n\s*(.+)", email)
        date_str = date_match.group(1).strip()
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y")

        trx_id_match = re.search(r"ID transaksi\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        return [trx]

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        if "Anda mengirim" in email:
            return self.extractPembayaran(email)
        elif "Anda menerima " in email:
            return self.extractPenerimaan(email)
        return []