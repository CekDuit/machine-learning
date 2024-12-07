import re
from datetime import datetime
from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class BRIExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the BRI format.
        """
        return email_from == "BankBRI@bri.co.id" and ("Top Up" in title or "Pembelian" in title or "Pembayaran" in title or "Pemindahan" in title)
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the BRI email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "BRI"

        # Check for specific types of transactions
        if self._is_ewallet_top_up(email):  # Check if it's an e-wallet top-up
            self._extract_ewallet_top_up(email, trx)
        elif self._is_briva_payment(email):  # Check if it's a BRIVA payment
            self._extract_payment(email, trx)
        elif self._is_bpjs_payment(email):
            self._extract_bpjs_payment(email, trx)
        elif self._is_qris_payment(email):
            self._extract_qris_payment(email, trx)
        elif self._is_electricity_payment(email):
            self._extract_electricity_payment(email, trx)
        elif self._is_transfer(email):
            self._extract_transfer(email, trx)
        else:
            trx.description = "Unknown transaction type"

        return [trx]
    
    def _is_ewallet_top_up(self, email: str) -> bool:
        """
        Check if the email is for an e-wallet top-up transaction (e.g., ShopeePay, GoPay, DANA).
        """
        return "ShopeePay" in email or "OVO" in email or "GoPay" in email or "DANA" in email  # Look for 'ShopeePay', 'OVO', 'GoPay', 'DANA' keyword in the transaction type

    def _is_briva_payment(self, email: str) -> bool:
        """
        Check if the email is for a BRIVA payment.
        """
        return "Pembayaran BRIVA" in email  # Check for 'Pembayaran BRIVA' in the transaction type
    
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
        return "QRIS" in email  # Check for 'QRIS' keyword in the email
    
    def _is_electricity_payment(self, email: str) -> bool:
        """
        Check if the email is for an electricity payment transaction.
        """
        return "PLN" in email

    def _is_transfer(self, email: str) -> bool:
        """
        Check if the email is for a bank transfer.
        """
        return "Pemindahan" in email  # Example pattern, adjust accordingly
    
    
    def _is_payment(self, email: str) -> bool:
        """
        Check if the email is for a payment transaction.
        """
        return "Pembayaran" in email or "Pembelian" in email  # Example pattern, adjust accordingly

    def _extract_ewallet_top_up(self, email: str, trx: TransactionData):
        """
        Extract data for an e-wallet top-up transaction (e.g., ShopeePay, GoPay, OVO, DANA).
        """
        # Regex to match the date-time format
        date_pattern = r"(\d{2}) (\w+) (\d{4}), (\d{2}):(\d{2}):(\d{2}) WIB"
        date_match = re.search(date_pattern, email)

        if date_match:
            # Extract date components
            day = date_match.group(1)
            month_abbr = date_match.group(2)
            year = date_match.group(3)
            hour = date_match.group(4)
            minute = date_match.group(5)
            second = date_match.group(6)

            # If the month is in full (e.g., "September") without abbreviation
            month_translation = {
                "Januari": "January", "Februari": "February", "Maret": "March", "April": "April", 
                "Mei": "May", "Juni": "June", "Juli": "July", "Agustus": "August", "September": "September", 
                "Oktober": "October", "November": "November", "Desember": "December"
            }

            # Replace the Indonesian month abbreviation with English
            english_month = month_translation.get(month_abbr, month_abbr)

            # Build the full date string for parsing
            full_date_str = f"{day} {english_month} {year} {hour}:{minute}:{second}"

            # Now, parse it using datetime
            try:
                parsed_date = datetime.strptime(full_date_str, "%d %B %Y %H:%M:%S")
                trx.date = parsed_date
            except ValueError as e:
                print(f"Error parsing date: {e}")

        # Regex to extract the transaction reference number
        trx_id_pattern = r"No. Ref (\d+)"
        trx_id_match = re.search(trx_id_pattern, email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # Regex to extract the merchant name
        merchant_pattern = r"Jenis Transaksi (\w+)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Regex to extract the amount
        amount_pattern = r"Nominal Rp([\d,.]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace('.', '').replace(',', '.'))

        # Regex to extract the fee
        fee_pattern = r"Biaya Admin Rp([\d,.]+)"
        fee_match = re.search(fee_pattern, email)
        if fee_match:
            trx.fees = Decimal(fee_match.group(1).replace('.', '').replace(',', '.'))

        arr_merchant = ["ShopeePay", "OVO", "GoPay", "DANA"]
        for merchant in arr_merchant:
            if merchant in email:
                trx.merchant = merchant
                break

        # Extract the description (Catatan)
        description_pattern = r"Catatan\s*-*\s*(.*?)(?=\*{2,}|\Z)"
        description_match = re.search(description_pattern, email, re.DOTALL)
        if description_match:
            trx.description = description_match.group(1).strip()
        else:
            trx.description = "No notes provided"

    def _extract_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a BRIVA payment transaction with flexible source account match.
        """
        # Regex to match the date-time format
        date_pattern = r"(\d{2}) (\w+) (\d{4}), (\d{2}):(\d{2}):(\d{2}) WIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract date components
            day = date_match.group(1)
            month_abbr = date_match.group(2)
            year = date_match.group(3)
            hour = date_match.group(4)
            minute = date_match.group(5)
            second = date_match.group(6)
            # Print extracted components
            print(f"Day: {day}, Month: {month_abbr}, Year: {year}, Time: {hour}:{minute}:{second}")
            # If the month is in full (e.g., "September") without abbreviation
            month_translation = {
                "Januari": "January", "Februari": "February", "Maret": "March", "April": "April", 
                "Mei": "May", "Juni": "June", "Juli": "July", "Agustus": "August", "September": "September", 
                "Oktober": "October", "November": "November", "Desember": "December"
            }
            # Replace the Indonesian month abbreviation with English
            english_month = month_translation.get(month_abbr, month_abbr)
            # Build the full date string for parsing
            full_date_str = f"{day} {english_month} {year} {hour}:{minute}:{second}"
            # Now, parse it using datetime
            try:
                parsed_date = datetime.strptime(full_date_str, "%d %B %Y %H:%M:%S")
                trx.date = parsed_date
            except ValueError as e:
                print(f"Error parsing date: {e}")

        # Extract Reference Number
        ref_match = re.search(r"No. Ref (\S+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)

        # Extract Nominal Amount
        nominal_match = re.search(r"Nominal\s*Rp([\d,\.]+)", email)
        if nominal_match:
            trx.amount = Decimal(nominal_match.group(1).replace(".", "").replace(",", ""))

        # Extract Admin Fee (if available)
        admin_fee_match = re.search(r"Biaya Admin\s*Rp([\d,\.]+)", email)
        if admin_fee_match:
            trx.fees = Decimal(admin_fee_match.group(1).replace(".", "").replace(",", ""))

        # Extract Total Amount
        total_match = re.search(r"Total\s*Rp([\d,\.]+)", email)
        if total_match:
            trx.amount = Decimal(total_match.group(1).replace(".", "").replace(",", ""))

        # Extract Destination Information (e.g., "TOKOPEDIA", "80777082125220349")
        destination_match = re.search(r"Tujuan\s*[A-Za-z\s]*([\w\s]+)\s*(\d+)", email)
        if destination_match:
            trx.merchant = destination_match.group(1).strip()

        # Assign Currency (IDR for this example)
        trx.currency = "IDR"  # Default to IDR
        trx.description = "BRIVA Payment"

    def _extract_bpjs_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a BPJS payment transaction.
        """
        # Extract Transaction Date and handle 'WIB' timezone
        date_match = re.search(r"Tanggal\s*(\d{2} \w{3} \d{4}) \| (\d{2}:\d{2}:\d{2}) WIB", email)
        if date_match:
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            # Translate the Indonesian month abbreviation to English
            month_translation = {
                "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "Mei": "May",
                "Jun": "June", "Jul": "July", "Agu": "August", "Sep": "September", "Okt": "October",
                "Nov": "November", "Des": "December"
            }
            for ind_month, eng_month in month_translation.items():
                date_str = date_str.replace(ind_month, eng_month)

            # Parse the date
            trx.date = datetime.datetime.strptime(date_str, "%d %B %Y %H:%M:%S")

        # Extract Reference Number (Nomor Referensi)
        ref_match = re.search(r"Nomor Referensi\s*(\S+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)

        # Extract Customer Name (Nama Pelanggan)
        customer_name_match = re.search(r"Nama Pelanggan\s*([\w\s]+)", email)
        if customer_name_match:
            trx.merchant = customer_name_match.group(1).strip()

        # Extract Notes (Keterangan)
        notes_match = re.search(r"Keterangan\s*([\w\s]+)", email)
        if notes_match:
            trx.description = notes_match.group(1).strip()

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
        # 1. Extract Transaction Date (Tanggal)
        date_pattern = r"Tanggal (\d{2} \w{3} \d{4}) \| (\d{2}:\d{2}:\d{2}) WIB"
        date_match = re.search(date_pattern, email)
        if date_match:
            # Extract the date and time components
            date_str = f"{date_match.group(1)} {date_match.group(2)}"
            # Translate Indonesian month abbreviation to English
            month_translation = {
                "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "Mei": "May",
                "Jun": "June", "Jul": "July", "Agu": "August", "Sep": "September", "Okt": "October",
                "Nov": "November", "Des": "December"
            }
            for ind_month, eng_month in month_translation.items():
                date_str = date_str.replace(ind_month, eng_month)

            # Convert to datetime object
            trx.date = datetime.strptime(date_str, "%d %B %Y %H:%M:%S")

        # 2. Extract Transaction Reference Number (Nomor Referensi)
        trx_id_pattern = r"Nomor Referensi (\d+)"
        trx_id_match = re.search(trx_id_pattern, email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)

        # 3. Extract Merchant Name (Nama Merchant)
        merchant_pattern = r"Nama Merchant ([\w\s]+)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # 4. Extract Transaction Amount (Nominal)
        amount_pattern = r"Nominal Rp([\d\.]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace('.', '').replace(',', '.'))

        # 5. Extract Transaction Fee (Biaya Admin)
        fee_pattern = r"Biaya Admin Rp([\d\.]+)"
        fee_match = re.search(fee_pattern, email)
        if fee_match:
            trx.fees = Decimal(fee_match.group(1).replace('.', '').replace(',', '.'))

        trx.description = "Transaksi dengan QRIS BRI"

        trx.payment_method = "QRIS BRI"

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
            trx.date = datetime.strptime(full_date, "%d %B %Y %H:%M")

        # Extract reference number
        ref_pattern = r"Nomor Referensi(\d+)"
        ref_match = re.search(ref_pattern, email)
        if ref_match:
            trx.trx_id = ref_match.group(1)

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

    def _extract_transfer(self, email: str, trx: TransactionData):
        """
        Extract data for a transfer transaction.
        """
        pass  # Add logic for transfer-specific fields