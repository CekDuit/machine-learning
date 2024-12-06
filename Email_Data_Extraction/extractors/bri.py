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
        trx.extra_data = {}

        # Check for specific types of transactions
        if self._is_ewallet_top_up(email):  # Check if it's an e-wallet top-up
            self._extract_ewallet_top_up(email, trx)
        elif self._is_briva_payment(email):  # Check if it's a BRIVA payment
            self._extract_payment(email, trx)
        elif self._is_bpjs_payment(email):
            self._extract_bpjs_payment(email, trx)
        elif self._is_qris_payment(email):
            self._extract_qris_payment(email, trx)
        elif self._is_transfer(email):
            self._extract_transfer(email, trx)
        else:
            trx.description = "Unknown transaction type"

        return [trx]
    
    def _is_ewallet_top_up(self, email: str) -> bool:
        """
        Check if the email is for an e-wallet top-up transaction (e.g., ShopeePay).
        """
        return "Jenis Transaksi ShopeePay" in email or "Jenis Transaksi OVO" in email or "Jenis Transaksi GoPay" in email or "Jenis Transaksi DANA" in email  # Look for 'ShopeePay' keyword in the transaction type

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

        # Extract Transaction Type (e.g., "Pembayaran BRIVA")
        trx_type_match = re.search(r"Jenis Transaksi\s*(Pembayaran BRIVA)", email)
        if trx_type_match:
            trx.extra_data["transaction_type"] = trx_type_match.group(1)

        # Extract Nominal Amount
        nominal_match = re.search(r"Nominal\s*Rp([\d,\.]+)", email)
        if nominal_match:
            trx.amount = Decimal(nominal_match.group(1).replace(".", "").replace(",", ""))

        # Extract Admin Fee (if available)
        admin_fee_match = re.search(r"Biaya Admin\s*Rp([\d,\.]+)", email)
        if admin_fee_match:
            trx.extra_data["admin_fee"] = Decimal(admin_fee_match.group(1).replace(".", "").replace(",", ""))

        # Extract Total Amount
        total_match = re.search(r"Total\s*Rp([\d,\.]+)", email)
        if total_match:
            trx.amount = Decimal(total_match.group(1).replace(".", "").replace(",", ""))

        # Extract Destination Information (e.g., "TOKOPEDIA", "80777082125220349")
        destination_match = re.search(r"Tujuan\s*[A-Za-z\s]*([\w\s]+)\s*(\d+)", email)
        if destination_match:
            trx.extra_data["destination_name"] = destination_match.group(1).strip()
            trx.extra_data["destination_id"] = destination_match.group(2)

            # Ensure the merchant is assigned correctly based on the destination name
            trx.merchant = trx.extra_data["destination_name"]

        # Extract Source Account Information under 'Sumber Dana'
        source_account_match = re.search(r"Sumber Dana\s*([A-Za-z\s]+)\s*(BANK\s+[A-Za-z]+)\s*(\d{4}[\*\-]+\d{4})", email)
        if source_account_match:
            trx.extra_data["source_account"] = f"{source_account_match.group(1).strip()} {source_account_match.group(2).strip()} {source_account_match.group(3)}"

        # Assign Currency (IDR for this example)
        trx.currency = "IDR"  # Default to IDR
        trx.description = "BRIVA Payment"

    def _extract_bpjs_payment(self, email: str, trx: TransactionData):
        """
        Extract data for a BPJS Kesehatan payment transaction.
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

        # Extract Source Account (e.g., "ROHIMA BANK BRI 6476 **** **** 534")
        source_account_match = re.search(r"Sumber Dana\s*([0-9]{4}\s\*\*\*\*\s\*\*\*\*\s[0-9]{3})", email)
        if source_account_match:
            trx.extra_data["source_account"] = source_account_match.group(1).strip()

        # Extract Institution (BPJS Kesehatan)
        institution_match = re.search(r"Institusi\s*BPJS\s*Kesehatan", email)
        if institution_match:
            trx.extra_data["institution"] = institution_match.group(0).strip()

        # Extract Payment Number (Nomor Pembayaran)
        payment_number_match = re.search(r"Nomor Pembayaran\s*(\S+)", email)
        if payment_number_match:
            trx.extra_data["payment_number"] = payment_number_match.group(1).strip()

        # Extract Transaction ID (ID Transaksi)
        transaction_id_match = re.search(r"ID Transaksi\s*(\S+)", email)
        if transaction_id_match:
            trx.extra_data["transaction_id"] = transaction_id_match.group(1).strip()

        # Extract Customer Name (Nama Pelanggan)
        customer_name_match = re.search(r"Nama Pelanggan\s*([\w\s]+)", email)
        if customer_name_match:
            trx.extra_data["customer_name"] = customer_name_match.group(1).strip()

        # Extract Location (Lokasi)
        location_match = re.search(r"Lokasi\s*([\w\s\-]+)", email)
        if location_match:
            trx.extra_data["location"] = location_match.group(1).strip()

        # Extract Family Count (Jumlah Keluarga)
        family_count_match = re.search(r"Jumlah Keluarga\s*(\d+)", email)
        if family_count_match:
            trx.extra_data["family_count"] = family_count_match.group(1).strip()

        # Extract Notes (Keterangan)
        notes_match = re.search(r"Keterangan\s*([\w\s]+)", email)
        if notes_match:
            trx.extra_data["notes"] = notes_match.group(1).strip()

        # Extract Nominal Amount (Nominal)
        nominal_match = re.search(r"Nominal\s*Rp([\d,\.]+)", email)
        if nominal_match:
            trx.amount = Decimal(nominal_match.group(1).replace(".", "").replace(",", ""))
            trx.currency = "IDR"

        # Extract Admin Fee (Biaya Admin)
        admin_fee_match = re.search(r"Biaya Admin\s*Rp([\d,\.]+)", email)
        if admin_fee_match:
            trx.extra_data["admin_fee"] = Decimal(admin_fee_match.group(1).replace(".", "").replace(",", ""))

        # Extract Total Amount (Total)
        total_match = re.search(r"Total\s*Rp([\d,\.]+)", email)
        if total_match:
            trx.amount = Decimal(total_match.group(1).replace(".", "").replace(",", ""))

        trx.description = "BPJS Payment"

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

        trx.description = "QRIS Payment Transaction with BRI"

        trx.payment_method = "QRIS BRI"

    def _extract_transfer(self, email: str, trx: TransactionData):
        """
        Extract data for a transfer transaction.
        """
        pass  # Add logic for transfer-specific fields