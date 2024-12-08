from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class MandiriExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        # return (
        #     ("transfer berhasil" in title.lower() or "top-up berhasil" in title.lower()) 
        #     and email_from == "m320b4ky1551@bangkit.academy"
        # )
    
        valid_titles = [
            "transfer berhasil",
            "top-up berhasil",
            "pembayaran berhasil"
        ]
        valid_emails = [
            "noreply.livin@bankmandiri.co.id"
        ]
        is_title_valid = any(valid_title in title.lower() for valid_title in valid_titles)
        is_email_valid = any(valid_email in email_from.lower() for valid_email in valid_emails)

        return is_title_valid and is_email_valid

    def extract_transfer(self, content: EmailContent) -> list[TransactionData]:
        email = content
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

        currency_amount_match = re.search(r"Jumlah Transfer\s*([A-Za-z]+)\s*([\d.,]+)", email)
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = int(Decimal(amount.replace(".", "").replace(",", ".")))

        description_match = re.search(r"Keterangan\s*\\([^\s]+)", email)
        trx.description = description_match.group(1).strip()

        merchant_match = re.search(r"Penerima\s*\n\s*####\s*(.+)", email)
        trx.merchant = merchant_match.group(1).strip()

        trx_id_match = re.search(r"No\. Referensi\s*(\d+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # bulan_map = {
        #     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
        #     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
        #     "Jul": "Jul", "Agt": "Aug", "Sep": "Sep",
        #     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        # }

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # date_str = date_match.group(1)
        # time_str = time_match.group(1)
            
        # for indo, eng in bulan_map.items():
        #     date_str = date_str.replace(indo, eng)
            
        # trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

#         bulan_map = {
#     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
#     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
#     "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
#     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
# }

#         date_str = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email).group(1)
#         time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)
#         date_str = "".join(date_str.replace(indo, eng) for indo, eng in bulan_map.items())
#         trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        bulan_map = {
            "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
            "Apr": "Apr", "Mei": "May", "Jun": "Jun",
            "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
            "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        }

        email = "Tanggal1 Agu 2024\nJam07:42:38 WIB"

        date_str = re.search(r"Tanggal\s*(\d{1,2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)

        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        return [trx]

    def extract_topup(self, content: EmailContent) -> list[TransactionData]:
        email = content
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

        currency_amount_match = re.search(r"Total Transaksi\s*([A-Za-z]+)\s*([\d.,]+)", email)
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = int(Decimal(amount.replace(".", "").replace(",", ".")))

        trx.description = '-'
        merchant_match = re.search(r"Penyedia Jasa\s*\n\s*####\s*(.+)", email)
        trx.merchant = merchant_match.group(1).strip()

        trx_id_match = re.search(r"No\. Referensi\s*(\d+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # bulan_map = {
        #     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
        #     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
        #     "Jul": "Jul", "Agt": "Aug", "Sep": "Sep",
        #     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        # }

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # date_str = date_match.group(1)
        # time_str = time_match.group(1)
            
        # for indo, eng in bulan_map.items():
        #     date_str = date_str.replace(indo, eng)
            
        # trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

#         bulan_map = {
#     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
#     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
#     "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
#     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
# }

#         date_str = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email).group(1)
#         time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

#         for indo, eng in bulan_map.items():
#             date_str = date_str.replace(indo, eng)

#         trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        # bulan_map = {
        #     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
        #     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
        #     "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
        #     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        # }

        # email = "Tanggal1 Agu 2024\nJam07:42:38 WIB"

        # date_str = re.search(r"Tanggal\s*(\d{1,2} \w{3} \d{4})", email).group(1)
        # time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

        # for indo, eng in bulan_map.items():
        #     date_str = date_str.replace(indo, eng)

        # trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        bulan_map = {
    "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
    "Apr": "Apr", "Mei": "May", "Jun": "Jun",
    "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
    "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
}

        email = "Tanggal1 Agu 2024\nJam07:42:38 WIB"

        date_str = re.search(r"Tanggal\s*(\d{1,2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)

        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        return [trx]
    
    def extract_payment(self, content: EmailContent) -> list[TransactionData]:
        email = content
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

        currency_amount_match = re.search(r"Nominal Transaksi\s*([A-Za-z]+)\s*([\d.,]+)", email)
        trx.currency, amount = currency_amount_match.groups()
        if trx.currency == "Rp":
            trx.currency = "IDR"
        trx.amount = int(Decimal(amount.replace(".", "").replace(",", ".")))

        trx.description = "-"

        merchant_match = re.search(r"Penerima\s*\n\s*####\s*(.+)", email)
        trx.merchant = merchant_match.group(1).strip()

        trx_id_match = re.search(r"No\. Referensi\s*(\d+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # bulan_map = {
        #     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
        #     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
        #     "Jul": "Jul", "Agt": "Aug", "Sep": "Sep",
        #     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        # }

        # date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email)
        # time_match = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email)

        # date_str = date_match.group(1)
        # time_str = time_match.group(1)
            
        # for indo, eng in bulan_map.items():
        #     date_str = date_str.replace(indo, eng)
            
        # trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

#         bulan_map = {
#     "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
#     "Apr": "Apr", "Mei": "May", "Jun": "Jun",
#     "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
#     "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
# }

#         date_str = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4})", email).group(1)
#         time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

#         for indo, eng in bulan_map.items():
#             date_str = date_str.replace(indo, eng)

#         trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")

        bulan_map = {
            "Jan": "Jan", "Feb": "Feb", "Mar": "Mar",
            "Apr": "Apr", "Mei": "May", "Jun": "Jun",
            "Jul": "Jul", "Agu": "Aug", "Sep": "Sep",
            "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
        }

        email = "Tanggal1 Agu 2024\nJam07:42:38 WIB"

        date_str = re.search(r"Tanggal\s*(\d{1,2} \w{3} \d{4})", email).group(1)
        time_str = re.search(r"Jam\s*(\d{2}:\d{2}:\d{2})", email).group(1)

        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)

        trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M:%S")


        return [trx]
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        if "Transfer Berhasil" in email:
            print("Transfer Berhasil")
            return self.extract_transfer(email)
        elif "Top-up Berhasil" in email:
            print("Top-up Berhasil")
            return self.extract_topup(email)
        elif "Pembayaran Berhasil" in email:
            print("Pembayaran Berhasil")
            return self.extract_payment(email)
        return []