import re
from datetime import datetime
from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class BRIExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the BRI format.
        """
        return title == "Top Up" or "Pembelian" or "Pembayaran" or "Pemindahan" and email_from == "BankBRI@bri.co.id"
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the BRI email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "BRImo"

        # Check for specific types of transactions
        if self._is_ewallet_top_up(email):
            self._extract_ewallet_top_up(email, trx)
        elif self._is_briva_payment(email):
            self._extract_brivia_payment(email, trx)
        elif self._is_bpjs_payment(email):
            self._extract_bpjs_payment(email, trx)
        elif self._is_qris_payment(email):
            self._extract_qris_payment(email, trx)
        elif self._is_electricity_payment(email):
            self._extract_electricity_payment(email, trx)
        elif self._is_credit_payment(email):
            self._extract_credit_payment(email, trx)
        elif self._is_transfer(email):
            self._extract_transfer(email, trx)

        return [trx]
    
    def _is_ewallet_top_up(self, email: str) -> bool:
        """
        Check if the email is for an e-wallet top-up transaction (e.g., ShopeePay, GoPay, DANA).
        """
        return "Jenis Transaksi ShopeePay" in email or "Jenis Transaksi DANA" in email or "Jenis Transaksi GoPay" in email or "Jenis Transaksi OVO" in email  # Look for 'ShopeePay', 'OVO', 'GoPay', 'DANA' keyword in the transaction type

    def _is_briva_payment(self, email: str) -> bool:
        """
        Check if the email is for a BRIVA payment.
        """
        return "Jenis Transaksi Pembayaran BRIVA" in email  # Check for 'Pembayaran BRIVA' in the transaction type
    
    def _is_bpjs_payment(self, email: str) -> bool:
        """
        Check if the email is for a BPJS Kesehatan payment transaction.
        """
        # Check if the email contains "Institusi BPJS Kesehatan"
        return re.search(r"Institusi\s*BPJS\s", email) is not None  # More flexible pattern
    
    def _is_qris_payment(self, email: str) -> bool:
        """
        Check if the email is for a QRIS payment transaction.
        """
        return "Jenis Transaksi Pembelian QRIS" in email  # Check for 'QRIS' keyword in the email
    
    def _is_electricity_payment(self, email: str) -> bool:
        """
        Check if the email is for an electricity payment transaction.
        """
        return "PembayaranTAGIHAN LISTRIK" in email
    
    def _is_credit_payment(self, email: str) -> bool:
        """
        Check if the email is for a payment transaction.
        """
        return "Jenis Transaksi Pulsa" in email # Example pattern, adjust accordingly
    
    def _is_transfer(self, email: str) -> bool:
        """
        Check if the email is for a bank transfer.
        """
        return "Jenis Transaksi Transfer " in email  # Example pattern, adjust accordingly

    def _extract_ewallet_top_up(self, email: str, trx: TransactionData):
        """
        Extract data for an e-wallet top-up transaction (e.g., ShopeePay, GoPay, OVO, DANA).
        """
        # Extract trx_id
        ref_pattern = r"No\. Ref\s+(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract date
        # Mapping for Indonesian months to English months
        month_translation = {
            "Januari": "Jan", "Februari": "Feb", "Maret": "Mar", "April": "Apr", "Mei": "May", "Juni": "Jun",
            "Juli": "Jul", "Agustus": "Aug", "September": "Sep", "Oktober": "Oct", "November": "Nov", "Desember": "Dec"
        }

        # Corrected date pattern to capture full date with year and time
        date_pattern = r"(\d{2})\s([A-Za-z]+)\s(\d{4}),\s(\d{2}:\d{2}:\d{2})\sWIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract the day, month, year, and time
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)
            time = date_match.group(4)
            # Translate the month to English
            month_english = month_translation.get(month_indonesian, month_indonesian)
            # Combine into a formatted date string
            date_str = f"{day} {month_english} {year}, {time}"
            try:
                # Convert to datetime object and format as required
                trx.date = datetime.strptime(date_str, "%d %b %Y, %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
        else:
            print("Date not found in the email content.")
        
        # Extract merchant
        merchant_pattern = r"Jenis Transaksi\s+([A-Za-z\s]+)(?=\s*Catatan|\s*$)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract fees
        fees_pattern = r"Biaya Admin\s+Rp([0-9\.,]+)"
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", "").replace(",", ""))

        # Extract amount
        amount_pattern = r"Nominal\s+Rp([0-9\.,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract payment method
        trx.payment_method = "BRImo"

        # Extract description
        trx.description = "Top-up e-wallet"


    def _extract_brivia_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a BRIVA payment transaction with flexible source account match.
        """
        # Extract trx_id
        ref_pattern = r"No\.\s*Ref\s*(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract date
        # Mapping for Indonesian months to English months
        month_translation = {
            "Januari": "Jan", "Februari": "Feb", "Maret": "Mar", "April": "Apr", "Mei": "May", "Juni": "Jun",
            "Juli": "Jul", "Agustus": "Aug", "September": "Sep", "Oktober": "Oct", "November": "Nov", "Desember": "Dec"
        }

        # Corrected date pattern to capture full date with year and time
        date_pattern = r"(\d{2})\s([A-Za-z]+)\s(\d{4}),\s(\d{2}:\d{2})\sWIB"
        date_match = re.search(date_pattern, email)

        if date_match:
            # Extract the day, month, year, and time
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)
            time = date_match.group(4)

            # Translate the month to English
            month_english = month_translation.get(month_indonesian, month_indonesian)

            # Combine into a formatted date string
            date_str = f"{day} {month_english} {year}, {time}"

            try:
                # Convert to datetime object and format as required
                trx.date = datetime.strptime(date_str, "%d %b %Y, %H:%M").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
        else:
            print("Date not found in the email content.")

        # Extract merchant
        merchant_pattern = r"Tujuan\s+[A-Za-z]+\s+[A-Za-z0-9]+[\s]+([A-Za-z\s]+)\s+\d{16}"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract fees
        fees_pattern = r"Biaya Admin\s+Rp([0-9\.,]+)"
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", "").replace(",", ""))

        # Extract amount
        amount_pattern = r"Nominal\s+Rp([0-9\.,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract payment method
        payment_method_pattern = r"Jenis Transaksi\s+[A-Za-z]+\s+([A-Za-z]+)"
        payment_method_match = re.search(payment_method_pattern, email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1)

        # Extract description
        trx.description = "BRIVA Payment"
        
    def _extract_bpjs_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a BPJS payment transaction.
        """
        # Extract date
        # Mapping for Indonesian months to English months
        month_translation = {
            "Januari": "Jan", "Februari": "Feb", "Maret": "Mar", "April": "Apr", "Mei": "May", "Juni": "Jun",
            "Juli": "Jul", "Agustus": "Aug", "September": "Sep", "Oktober": "Oct", "November": "Nov", "Desember": "Dec"
        }

        # Regex to extract the date and time from the email
        date_pattern = r"Tanggal\s+(\d{2})\s([A-Za-z]+)\s(\d{4})\s\|\s(\d{2}:\d{2}:\d{2})\sWIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract the day, month, year, and time
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)
            time = date_match.group(4)

            # Translate the month to English (if necessary)
            month_english = month_translation.get(month_indonesian, month_indonesian)

            # Combine the extracted date and time into a single string
            date_str = f"{day} {month_english} {year} {time}"

            # Convert to datetime object and format as required
            try:
                trx.date = datetime.strptime(date_str, "%d %b %Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
        else:
            print("Date not found in the email content.")
    
        # Extract Reference Number (Nomor Referensi)
        ref_match = re.search(r"Nomor Referensi\s*(\S+)", email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract merchant
        merchant_match = re.search(r"Institusi\s+([A-Za-z\s]+)\s+Nomor", email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract description
        trx.description = "Pembayaran BPJS"

        # Extract Nominal Amount (Nominal)
        nominal_match = re.search(r"Nominal\s*Rp([\d,\.]+)", email)
        if nominal_match:
            trx.amount = Decimal(nominal_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract Admin Fee (Biaya Admin)
        admin_fee_match = re.search(r"Biaya Admin\s*Rp([\d,\.]+)", email)
        if admin_fee_match:
            trx.fees = Decimal(admin_fee_match.group(1).replace(".", "").replace(",", ""))

    def _extract_qris_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a QRIS payment transaction.
        """
        # Extract trx_id
        ref_pattern = r"Nomor Referensi\s+(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract date
        date_pattern = r"Tanggal\s+(\d{2}\s[A-Za-z]{3}\s\d{4}\s\|\s\d{2}:\d{2}:\d{2}\sWIB)"
        date_match = re.search(date_pattern, email)
        if date_match:
            date_str = date_match.group(1)
            trx.date = datetime.strptime(date_str, "%d %b %Y | %H:%M:%S WIB").strftime("%Y-%m-%d %H:%M:%S")

        # Extract merchant
        merchant_pattern = r"Nama Merchant\s+([A-Za-z0-9\s\(\)\-\,\.]+?)(?=\s+Lokasi Merchant|$)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Extract fees
        fees_pattern = r"Biaya Admin\s+Rp([\d,]+)"
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(",", ""))

        # Extract amount
        amount_pattern = r"Total\s+Rp([\d\.]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", ""))
            trx.currency = "IDR"

        # Extract payment method
        payment_method_pattern = r"Nama Penerbit\s+([A-Za-z\s]+?)\s+Nama Acquirer"
        payment_method_match = re.search(payment_method_pattern, email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1)

        # Extract description
        description_pattern = r"Jenis Transaksi\s+([A-Za-z\s]+)\s+Nama Merchant\s+([A-Za-z0-9\s]+)\s+Lokasi Merchant\s+([A-Za-z\s]+)"
        description_match = re.search(description_pattern, email)
        if description_match:
            trx.description = description_match.group(1) + " " + description_match.group(2)
        
        
    def _extract_electricity_payment(self, email: str, trx: TransactionData):
        """
        Extract data for an electricity payment transaction.
        """
        # Extract date and time of payment
        date_pattern = r"Tanggal Pembayaran(\d{2} \w+ \d{4}) , (\d{2}:\d{2}) WIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            day, month, year = date_match.group(1).split()
            time = date_match.group(2)
            month_translation = {
                "Januari": "January", "Februari": "February", "Maret": "March", "April": "April",
                "Mei": "May", "Juni": "June", "Juli": "July", "Agustus": "August",
                "September": "September", "Oktober": "October", "November": "November", "Desember": "December"
            }
            month_english = month_translation[month]
            full_date = f"{day} {month_english} {year} {time}"
            trx.date = datetime.strptime(full_date, "%d %B %Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")

        # Extract reference number
        ref_pattern = r"Nomor Referensi(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract billing details
        billing_pattern = r"TARIF/DAYA([A-Za-z0-9\s/]+)"
        billing_match = re.search(billing_pattern, email)
        if billing_match:
            trx.description = billing_match.group(1).strip()

        # Extract payment amounts
        amount_pattern = r"RP TAG PLN\s*Rp([\d,.]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", "").replace(",", "."))

        admin_fee_pattern = r"ADMIN BANK\s*Rp([\d,.]+)"
        admin_fee_match = re.search(admin_fee_pattern, email)
        if admin_fee_match:
            trx.fees = Decimal(admin_fee_match.group(1).replace(".", "").replace(",", "."))

        # Set description
        trx.merchant = "PT. PLN INDONESIA"
        trx.payment_method = "BRI"
        trx.currency = "IDR"

    def _extract_credit_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a credit payment transaction.
        """
        # Extract trx_id
        ref_pattern = r"Nomor Referensi\s+(\d{4}\s\d{4}\s\d{4})"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract date
        # Mapping for Indonesian months to English months
        month_translation = {
            "Januari": "Jan", "Februari": "Feb", "Maret": "Mar", "April": "Apr", "Mei": "May", "Juni": "Jun",
            "Juli": "Jul", "Agustus": "Aug", "September": "Sep", "Oktober": "Oct", "November": "Nov", "Desember": "Dec"
        }

        # Corrected date pattern to capture full date with year and time
        date_pattern = r"Tanggal\s+(\d{2})\s([A-Za-z]+)\s(\d{4})\s\|\s(\d{2}:\d{2}:\d{2})"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract the day, month, year, and time
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)
            time = date_match.group(4)
            # Translate the month to English
            month_english = month_translation.get(month_indonesian, month_indonesian)
            # Combine into a formatted date string
            date_str = f"{day} {month_english} {year}, {time}"
            try:
                # Convert to datetime object and format as required
                trx.date = datetime.strptime(date_str, "%d %b %Y, %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
        else:
            print("Date not found in the email content.")

        # Extract merchant
        merchant_pattern = r"Provider\s+([A-Za-z\s]+)\s+Jenis Produk"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract fees
        fees_pattern = r"Biaya Admin\s+Rp([\d,.]+)"
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", "").replace(",", ""))

        # Extract amount
        amount_pattern = r"Nominal\s+Rp([\d,.]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract payment method
        trx.payment_method = "BRImo"

        # Extract description
        description_pattern = r"Jenis Produk\s+([A-Za-z\s\d]+)"
        description_match = re.search(description_pattern, email)
        if description_match:
            trx.description = description_match.group(1).strip()

    def _extract_transfer(self, email: str, trx: TransactionData):
        """
        Extract data for a transfer transaction.
        """
        # Extract trx_id
        ref_pattern = r"Nomor Referensi\s+(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = str(ref_match.group(1))

        # Extract date
        # Mapping for Indonesian months to English months
        month_translation = {
            "Januari": "Jan", "Februari": "Feb", "Maret": "Mar", "April": "Apr", "Mei": "May", "Juni": "Jun",
            "Juli": "Jul", "Agustus": "Aug", "September": "Sep", "Oktober": "Oct", "November": "Nov", "Desember": "Dec"
        }

        date_pattern = r"Tanggal\s+(\d{2})\s([A-Za-z]+)\s(\d{4})\s+,\s+(\d{2}:\d{2}:\d{2})\sWIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract the day, month, year, and time
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)
            time = date_match.group(4)
            # Translate the month to English
            month_english = month_translation.get(month_indonesian, month_indonesian)
            # Combine into a formatted date string
            date_str = f"{day} {month_english} {year}, {time}"
            try:
                # Convert to datetime object and format as required
                trx.date = datetime.strptime(date_str, "%d %b %Y, %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error parsing date: {e}")
        else:
            print("Date not found in the email content.")

        # Extract merchant
        merchant_pattern = r"Bank Tujuan\s+([A-Za-z\s]+)\s+Nomor Tujuan"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Extract fees
        fees_pattern = r"Biaya Admin\s+Rp([0-9\.,]+)"
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", "").replace(",", ""))

        # Extract amount
        amount_pattern = r"Nominal\s+Rp([0-9\.,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract payment method
        trx.payment_method = "BRImo"

        # Extract description
        description_pattern = r"Jenis Transaksi\s+([A-Za-z\- ]+)\s+Bank Tujuan"
        description_match = re.search(description_pattern, email)
        if description_match:
            trx.description = description_match.group(1)