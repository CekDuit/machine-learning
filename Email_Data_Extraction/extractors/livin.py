from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class MandiriExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return (
            ("transfer berhasil" in title.lower() or "top-up berhasil" in title.lower()) 
            and email_from == "noreply@mandiri.com"
        )


    def extract_transfer(self, email: str) -> TransactionData:
        # Penerima : FLIPTECH LENTERA INS
        # Bank Mandiri - 157000534545393
        # Tanggal : 13 Nov 2024
        # Jam : 15:53:45 WIB
        # Jumlah Transfer : Rp200.406,00
        # No. Referensi : 2411131121092046786
        # Keterangan : -
        # Rekening Sumber : DADADA TELY
        # *****5683

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Livin' by Mandiri"

        currency_amount_match = re.search(
            r"Jumlah Transfer\s*:\s*([A-Za-z]+)\s*([\d,\.]+)", email
        )
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", "").replace(",", "."))

        trx.description = re.search(r"Keterangan\s*:\s*(.+)", email).group(1)
        trx.merchant = re.search(r"Penerima\s*:\s*(.+)", email).group(1)
        date_str = re.search(r"Tanggal\s*:\s*(\d{2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*:\s*(\d{2}:\d{2}:\d{2})", email).group(1)
        trx.trx_id = re.search(r"No\. Referensi\s*:\s*(\d+)", email).group(1)
        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        return trx

    def extract_topup(self, email: str) -> TransactionData:
        # Penyedia Jasa : 3 Prepaid
        # ****0248
        # Tanggal : 13 Nov 2024
        # Jam : 13:10:26 WIB
        # Nominal Top-up : Rp 40.000,00
        # Biaya Transaksi : Rp 0,00
        # Total Transaksi : Rp 40.000,00
        # No. Referensi : 702410291310161710
        # Rekening Sumber : ARISTO TELY
        # *****5683

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Livin' by Mandiri"

        currency_amount_match = re.search(
            r"Total Transaksi\s*:\s*([A-Za-z]+)\s*([\d,\.]+)", email
        )
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", "").replace(",", "."))

        trx.description = '-' #tidak ada deskripsi saat top up
        trx.merchant = re.search(r"Rekening Sumber\s*:\s*(.+)", email).group(1)
        date_str = re.search(r"Tanggal\s*:\s*(\d{2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*:\s*(\d{2}:\d{2}:\d{2})", email).group(1)
        trx.trx_id = re.search(r"No\. Referensi\s*:\s*(\d+)", email).group(1)
        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        return trx
    
    def extract_payment(self, email: str) -> TransactionData:
        # Penerima : KOPI 7 KAMBANG IWAK -HO
        # PALEMBANG - ID
        # Tanggal : 29 Okt 2024
        # Jam : 18:35:00 WIB
        # Nominal Transaksi : Rp 124.300,00
        # No. Referensi : 2410291122532788441
        # No. Referensi QRIS : 410698015472
        # Merchant PAN : 9360001430019008082
        # Customer PAN : 9360000812187256836
        # Pengakuisisi : Bank BCA
        # Terminal ID : A2917806
        # Sumber Dana : ARISTO TELY
        # *****5683

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Livin' by Mandiri"

        currency_amount_match = re.search(
            r"Nominal Transaksi\s*:\s*([A-Za-z]+)\s*([\d,\.]+)", email
        )
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = Decimal(amount.replace(".", "").replace(",", "."))

        trx.description = '-' #tidak ada deskripsi saat top up
        trx.merchant = re.search(r"Penerima\s*:\s*(.+)", email).group(1)
        date_str = re.search(r"Tanggal\s*:\s*(\d{2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*:\s*(\d{2}:\d{2}:\d{2})", email).group(1)
        trx.trx_id = re.search(r"No\. Referensi\s*:\s*(\d+)", email).group(1)
        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        return trx
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        if "Data_Transfer" in email:
            return [self.extract_transfer(email)]
        elif "Data_TopUp" in email:
            return [self.extract_topup(email)]
        elif "Data_Payment" in email:
            return [self.extract_payment(email)]
        return []
