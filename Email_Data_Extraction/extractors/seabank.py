from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class SeaBankExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        valid_titles = ["notifikasi transaksi seabank", "notifikasi transfer seabank"]
        valid_emails = ["alerts@seabank.co.id"]
        is_title_valid = any(
            valid_title in title.lower() for valid_title in valid_titles
        )
        is_email_valid = any(
            valid_email in email_from.lower() for valid_email in valid_emails
        )

        return is_title_valid and is_email_valid

    #     return (
    #     "notifikasi transaksi seabank" in title.lower() and
    #     "alerts@seabank.co.id" in email_from.lower()
    # )

    # alerts@seabank.co.id
    def extract_instant_payment_transaction(
        self, content: EmailContent
    ) -> list[TransactionData]:
        email = content
        # Example format:
        # Hai FX. SURYA DARMAWAN,
        # Terima kasih telah menggunakan layanan SeaBank. Permintaan pembayaran kamu berhasil diproses. Berikut ini adalah detail transaksi kamu:
        # Waktu Transaksi: 30 Nov 2024 11:11
        # Jenis Transaksi: SeaBank Bayar Instan
        # Transfer Dari: FX. SURYA DARMAWAN - XXXXXXXXX6749
        # Nama Merchant: Shopee
        # Username: fransxeagle
        # Jumlah: Rp38.000
        # Biaya: Rp0
        # No. Referensi: 20241130435053419703
        # Catatan: Note

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "SeaBank"

        # Split per line and match
        match = re.search(r"Jumlah\s*[\r\n]+\s*Rp([\d,\.]+)", email)

        amount = match.group(1)
        trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", ""))

        match = re.search(r"Catatan\s*[\r\n]+\s*(\S+)", email)
        trx.description = match.group(1).strip()
        match = re.search(r"Nama Merchant\s*[\r\n]+\s*(\S+)", email)
        trx.merchant = match.group(1)

        match = re.search(r"No\. Referensi\s*[\r\n]+\s*(\d+)", email)
        trx.trx_id = str(match.group(1))

        match = re.search(
            r"Waktu Transaksi\s*[\r\n]+\s*(\d{2} \w{3} \d{4} \d{2}:\d{2})", email
        )
        date_str = match.group(1)
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y %H:%M")

        return [trx]

    def extract_transfer_transaction(
        self, content: EmailContent
    ) -> list[TransactionData]:
        email = content
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
        match = re.search(r"Jumlah\s*[\r\n]+\s*Rp([\d,\.]+)", email)

        amount = match.group(1)
        trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", ""))

        match = re.search(r"Catatan\s*[\r\n]+\s*(\S+)", email)
        if match:
            trx.description = match.group(1).strip()
        else:
            trx.description = ""
        match = re.search(r"Rekening Tujuan\s*[\r\n]+\s*(\S+)", email)
        trx.merchant = match.group(1)

        match = re.search(r"No\. Referensi\s*[\r\n]+\s*(\d+)", email)
        trx.trx_id = str(match.group(1))

        match = re.search(
            r"Waktu Transaksi\s*[\r\n]+\s*(\d{2} \w{3} \d{4} \d{2}:\d{2})", email
        )
        date_str = match.group(1)
        trx.date = datetime.datetime.strptime(date_str, "%d %b %Y %H:%M")

        return [trx]

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        if "SeaBank Bayar Instan" in email:
            return self.extract_instant_payment_transaction(email)
        elif "Real Time (BI-FAST)" in email:
            return self.extract_transfer_transaction(email)
        return []
