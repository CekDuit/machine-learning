from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime
import locale


class PaypalExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        valid_titles = [
            "anda mengirim pembayaran",
            "anda telah menerima",
            "you've received",
            "you sent a payment",
            "you have received",
            "receipt for your payment"
        ]
        valid_emails = [
            "service@intl.paypal.com"
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
        # currency_amount_match = re.search(r"(?:Pembayaran terkirim|You paid|Payment)\s*[€$£]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*([A-Za-z]{3})",email)
        # trx.currency = currency_amount_match.group(2).strip()
        # amount = currency_amount_match.group(1).replace(".", "").replace(",", ".")  
        # trx.amount = Decimal(amount)

        # currency_amount_match = re.search(r"You paid\s*\$([\d,\.]+)\s*(\w+)", email)
        # trx.currency = currency_amount_match.group(2).strip()  # Ambil 'USD'
        # amount = currency_amount_match.group(1).replace(",", ".")  # Ubah koma menjadi titik
        # trx.amount = Decimal(amount)

        patterns = [
    r"You paid\s*\$([\d,\.]+)\s*(\w+)",         
    r"Payment\s*\$([\d,\.]+)\s*\$\s*(\w+)",       
    r"Anda membayar\s*\$([\d,\.]+)\s*(\w+)"       
]

        for pattern in patterns:
            currency_amount_match = re.search(pattern, email)
            if currency_amount_match:
                currency = currency_amount_match.group(2).strip()
                amount = currency_amount_match.group(1).replace(",", ".")
                trx.amount = Decimal(amount)
                trx.currency = currency

        description_match = re.search(r"(?:CATATAN ANDA UNTUK|YOUR NOTES FOR).*?\n\s*\n\s*(.+?)\n", email, re.DOTALL)
        trx.description = description_match.group(1).strip() if description_match else ""

        trx.merchant = "Paypal"

        # date_match = re.search(r"(?:Tanggal transaksi|Transaction date)\s*\n\s*(.+)", email)
        # date_str = date_match.group(1).strip()
        # bulan_map = {
        #     "Januari": "January", "Februari": "February", "Maret": "March",
        #     "April": "April", "Mei": "May", "Juni": "June",
        #     "Juli": "July", "Agustus": "August", "September": "September",
        #     "Oktober": "October", "November": "November", "Desember": "December"
        # }
        # for indo, eng in bulan_map.items():
        #     date_str = date_str.replace(indo, eng)

        # try:
        #     trx.date = datetime.datetime.strptime(date_str, "%d %b %Y")
        # except ValueError:
        #     trx.date = datetime.datetime.strptime(date_str, "%d %B %Y")

        date_match = re.search(r"(?:Tanggal transaksi|Transaction date)\s*\n\s*(.+)", email)
        date_str = date_match.group(1).strip()
        
        bulan_map = {
            "Januari": "January", "Februari": "February", "Maret": "March",
            "April": "April", "Mei": "May", "Juni": "June",
            "Juli": "July", "Agustus": "August", "September": "September",
            "Oktober": "October", "November": "November", "Desember": "December"
        }
        
        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)
        
        date_str = re.sub(r'\s+\d{2}\.\d{2}\.\d{2}\s+(?:WIB|WITA|WIT)', '', date_str)
  
        date_formats = [
            "%d %B %Y", 
            "%d %b %Y",
            "%d %B %Y %H.%M.%S WIB",  
            "%d %B %Y %H.%M.%S WITA", 
            "%d %B %Y %H.%M.%S WIT"  
        ]
        
        for date_format in date_formats:
            try:
                trx.date = datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                continue
    
        trx_id_match = re.search(r"(?:ID transaksi|Transaction ID)\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        return [trx]
    
    def extractPembayaranPayment(self, content: EmailContent) -> list[TransactionData]:
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
        # currency_amount_match = re.search(r"(?:Pembayaran terkirim|You paid|Payment)\s*[€$£]?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*([A-Za-z]{3})",email)
        # trx.currency = currency_amount_match.group(2).strip()
        # amount = currency_amount_match.group(1).replace(".", "").replace(",", ".")  
        # trx.amount = Decimal(amount)

        currency_amount_match = re.search(r"Total\s*€\s*([\d,\.]+)\s*€\s*(\w+)", email)

        trx.currency = currency_amount_match.group(2).strip()
        amount = currency_amount_match.group(1).replace(",", ".")  # Ubah koma menjadi titik untuk Decimal
        trx.amount = Decimal(amount)

            # Ambil simbol mata uang
        # currency_symbol = currency_amount_match.group(1)
        # # Ambil jumlah angka
        # amount = currency_amount_match.group(2).replace(",", ".")  # Ubah koma ke titik
        # # Ambil kode mata uang (jika ada), atau gunakan simbol sebagai default
        # currency_code = currency_amount_match.group(3) if currency_amount_match.group(3) else currency_symbol
        
        # # Konversi ke Decimal untuk keamanan finansial
        # amount_decimal = Decimal(amount)

        description_match = re.search(r"(?:CATATAN ANDA UNTUK|YOUR NOTES FOR).*?\n\s*\n\s*(.+?)\n", email, re.DOTALL)
        trx.description = description_match.group(1).strip() if description_match else ""

        trx.merchant = "Paypal"

        date_match = re.search(r"(?:Tanggal transaksi|Transaction date)\s*\n\s*(.+)", email)
        date_str = date_match.group(1).strip()
        bulan_map = {
            "Januari": "January", "Februari": "February", "Maret": "March",
            "April": "April", "Mei": "May", "Juni": "June",
            "Juli": "July", "Agustus": "August", "September": "September",
            "Oktober": "October", "November": "November", "Desember": "December"
        }
        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)

        try:
            trx.date = datetime.datetime.strptime(date_str, "%d %b %Y")
        except ValueError:
            trx.date = datetime.datetime.strptime(date_str, "%d %B %Y")

        trx_id_match = re.search(r"(?:ID transaksi|Transaction ID)\s*(\S+)", email)
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
        currency_amount_match = re.search(r"(?:Jumlah yang diterima|Amount received)\s*\$(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(\w+)", email)
        trx.currency = currency_amount_match.group(2).strip()
        amount = currency_amount_match.group(1).replace(".", "").replace(",", ".")  
        trx.amount = Decimal(amount)

        description_match = re.search(r"(?:CATATAN|NOTED).*?\n\s*\n\s*(.+?)\n", email, re.DOTALL)
        trx.description = description_match.group(1).strip() if description_match else ""

        trx.merchant = "Paypal"
        
        date_match = re.search(r"(?:Tanggal transaksi|Transaction date)\s*\n\s*(.+)", email)
        date_str = date_match.group(1).strip()
        bulan_map = {
            "Januari": "January", "Februari": "February", "Maret": "March",
            "April": "April", "Mei": "May", "Juni": "June",
            "Juli": "July", "Agustus": "August", "September": "September",
            "Oktober": "October", "November": "November", "Desember": "December"
        }
        for indo, eng in bulan_map.items():
            date_str = date_str.replace(indo, eng)

        try:
            trx.date = datetime.datetime.strptime(date_str, "%d %b %Y")
        except ValueError:
            trx.date = datetime.datetime.strptime(date_str, "%d %B %Y")

        trx_id_match = re.search(r"(?:ID transaksi|Transaction ID)\s*(\S+)", email)
        trx.trx_id = trx_id_match.group(1) if trx_id_match else None

        return [trx]

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        if "anda mengirim" in email.lower() or "you sent" in email.lower():
            print("masuk anda mengirim")
            return self.extractPembayaran(email)
        elif "anda menerima" in email.lower() or "has sent you" in email.lower():
            print("masuk anda menerima")
            return self.extractPenerimaan(email)
        elif "pembayaran anda" in email.lower() or "you paid" in email.lower():
            print("masuk anda payment")
            return self.extractPembayaranPayment(email)
        return []