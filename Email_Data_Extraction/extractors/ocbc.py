import re
from decimal import Decimal
from typing import Optional
from datetime import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class OCBCExtractor(BaseExtractor):

    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OCBC payment receipt format.
        """
        return (title.endswith("Transfer Dana Masuk") or title.startswith("Successful Payment ") or title.startswith("Successful QR Payment ") or title.startswith("Pembayaran QR Berhasil ") or title.startswith("Successful Funds Transfer ")) and (email_from == "onlinetransaction@ocbc.id" or email_from == "notifikasi@ocbc.id" or email_from == "notifikasi@ocbcnisp.com") 

    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract transactions from the OCBC email content.
        """
        email = content.get_plaintext()

        # Normalize whitespace
        email = re.sub(r"\s+", " ", email)

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "OCBC"

        if self._is_extract_transfer(email):
            self._extract_transfer(email, trx)
        elif self._is_extract_qr_payment(email):
            self._extract_qr_payment(email, trx)
        elif self._is_extract_funds_transfer(email):
            self._extract_funds_transfer(email, trx)
        elif self._is_extract_top_up(email):
            self._extract_top_up(email, trx)

        return [trx]
    
    def _is_extract_transfer(self, email: str) -> bool:
        """
        Check if the email is a transfer receipt.
        """
        if "TRANSFER DANA" in email:
            return True
        return False
    
    def _is_extract_qr_payment(self, email: str) -> bool:
        """
        Check if the email is a QR payment receipt.
        """
        if "QR Payment" in email or "Pembayaran QR" in email:
            return True
        return False
    
    def _is_extract_funds_transfer(self, email: str) -> bool:
        """
        Check if the email is a funds transfer receipt.
        """
        if "Successful Funds Transfer" in email:
            return True
        return False
    
    def _is_extract_top_up(self, email: str) -> Optional[bool]:
        """
        Check if the email is in the 'Successful Bill Payment' format for top-up.
        """
        if "Successful Payment" in email or "Top Up" in email in email:
            return True
        return False
    
    def _extract_transfer(self, email: str, trx: TransactionData) -> None:
        """
        Extract the transfer details from the OCBC email.
        """
        # Extract Transaction ID
        trx.trx_id = "-"

        # Extract Nominal (Amount)
        nominal_pattern = r"Nominal\s*:\s*Rp\s*([\d\.]+),(\d{2})\s*"
        nominal_match = re.search(nominal_pattern, email)
        if nominal_match:
            # Remove thousands separator (.) and ignore the decimal part
            nominal_value = nominal_match.group(1).replace(".", "")  # Remove periods
            trx.currency = "IDR"  # Set currency
            trx.amount = Decimal(nominal_value)  # Convert to Decimal
            trx.fees = 0  # No fees for transfers

        # Extract Description
        description_pattern = r"menerima\s*(.*?)\s*(?=\n|dengan)"
        description_match = re.search(description_pattern, email)
        if description_match:
            trx.description = description_match.group(1)

        # Extract Merchant
        merchant_pattern = r"Bank Penerima\s*:\s*(.*?)\s*(?=\n|Nama Penerima)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Mapping for Indonesian month to numeric representation
        month_translation = {
            "Januari": "01", "Februari": "02", "Maret": "03", "April": "04", "Mei": "05", 
            "Juni": "06", "Juli": "07", "Agustus": "08", "September": "09", "Oktober": "10", 
            "November": "11", "Desember": "12"
        }

        # Extract Transaction Date
        date_pattern = r"Tanggal Transaksi\s*:\s*(\d{2})\s([A-Za-z]+)\s(\d{4})"
        date_match = re.search(date_pattern, email)
        if date_match:
            day = date_match.group(1)
            month_indonesian = date_match.group(2)
            year = date_match.group(3)

            # Translate month from Indonesian to numeric format
            month_numeric = month_translation.get(month_indonesian, "00")  # Default to "00" if not found

            # Combine into the final date string
            date_str = f"{year}-{month_numeric}-{day}"

        # Extract Transaction Time
        time_pattern = r"Waktu Transaksi\s*:\s*(\d{2}):(\d{2}):(\d{2})"
        time_match = re.search(time_pattern, email)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2)
            second = time_match.group(3)

            # Combine into the final time string
            time_str = f"{hour}:{minute}:{second}"
        
        # Combine date and time to form final datetime string
        if date_match and time_match:
            # Convert to a datetime object
            final_datetime_str = f"{date_str} {time_str}"
            trx.date = datetime.strptime(final_datetime_str, "%Y-%m-%d %H:%M:%S")

        # Extract Payment Method
        payment_method_pattern = r"Bank Pengirim\s*:\s*(.*?)\s*(?=\n|Nama Pengirim)"
        payment_method_match = re.search(payment_method_pattern, email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1)
            

    def _extract_qr_payment(self, email: str, trx: TransactionData) -> None:
        """
        Extract details from the QR payment email format.
        """
        if "QR Payment" in email:
            # Extract trx_id
            ref_match = r"Reff\s+No\.\s+(\S+)"
            ref_match = re.search(ref_match, email)
            if ref_match:
                trx.trx_id = ref_match.group(1)

            # Extract date & time
            date_pattern = r"Payment\s+Date:\s+(\d{2}/\d{2}/\d{4})"
            date_match = re.search(date_pattern, email)
            if date_match:
                trx.date = datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")

            # Extract merchant name
            merchant_pattern = r"Merchant\sPAN\s[\d]+\s+([^\n]+?)(?=\s+\w+|$)"
            merchant_match = re.search(merchant_pattern, email)
            if merchant_match:
                trx.merchant = merchant_match.group(1)

            # Extract fees
            fees_pattern = r"Tip\sIDR\s([\d,]+(?:\.\d{2})?)"
            fees_match = re.search(fees_pattern, email)
            if fees_match:
                fees_str = fees_match.group(1).replace(",", "")
                trx.fees = Decimal(fees_str.replace(".00", ""))

            # Extract amount
            amount_pattern = r"Amount Pay\sIDR\s([\d,]+(?:\.\d{2})?)"
            amount_match = re.search(amount_pattern, email)
            if amount_match:
                amount_str = amount_match.group(1).replace(",", "")
                trx.amount = Decimal(amount_str.replace(".00", ""))
                trx.currency = "IDR"

            # Extract description
            description_pattern = r"(QR\s+Payment\s+Merchant\s+PAN\s+\d{16})"
            description_match = re.search(description_pattern, email)
            if description_match:
                trx.description = description_match.group(1)
        
        elif "Pembayaran QR" in email:
            # Extract trx_id
            ref_match = r"No\.\s+Reff\s+(\S+)"
            ref_match = re.search(ref_match, email)
            if ref_match:
                trx.trx_id = ref_match.group(1)

            # Extract date
            date_pattern = r"TANGGAL\s+PEMBAYARAN:\s+(\d{2}/\d{2}/\d{4})"
            date_match = re.search(date_pattern, email)
            if date_match:
                trx.date = datetime.strptime(date_match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")
            
            # Extract merchant
            merchant_pattern = r"PAN\sMerchant\s[\d]+\s+([^\n]+?)(?=\s+\w+|$)"
            merchant_match = re.search(merchant_pattern, email)
            if merchant_match:
                trx.merchant = merchant_match.group(1)

            # Extract fees
            fees_pattern = r"Tip\sIDR\s([\d,]+(?:\.\d{2})?)"
            fees_match = re.search(fees_pattern, email)
            if fees_match:
                fees_str = fees_match.group(1).replace(",", "")
                trx.fees = Decimal(fees_str.replace(".00", ""))

            # Extract amount
            amount_pattern = r"Nominal Bayar\sIDR\s([\d,]+(?:\.\d{2})?)"
            amount_match = re.search(amount_pattern, email)
            if amount_match:
                amount_str = amount_match.group(1).replace(",", "")
                trx.amount = Decimal(amount_str.replace(".00", ""))
                trx.currency = "IDR"

            # Extract description
            description_pattern = r"(Pembayaran\s+QR\s+PAN\s+Merchant\s+\d{16})"
            description_match = re.search(description_pattern, email)
            if description_match:
                trx.description = description_match.group(1)


    def _extract_funds_transfer(self, email: str, trx: TransactionData) -> None:
        """
        Extract details from the funds transfer email format.
        """
        # Extract trx_id
        ref_match = r"Reference Number:\s*(\S+)"
        ref_match = re.search(ref_match, email)
        if ref_match:
            trx.trx_id = ref_match.group(1)

        date_pattern = r"TRANSFER DATE:\s*(\d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2} WIB)"
        # Extract date
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %b %Y %H:%M:%S WIB").strftime("%Y-%m-%d %H:%M:%S")

        # Extract merchant
        merchant_pattern = r"TO\s+[A-Za-z\s]+\s+([A-Za-z\s]+\s+[A-Za-z\s]+)"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()

        # Extract fees  
        fees_pattern = r"Fees\s+IDR\s([\d,\.]+)"  # No explicit fee in this example, defaults to 0
        fees_match = re.search(fees_pattern, email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(",", ""))

        # Extract the amount
        amount_pattern = r"####\s+IDR\s+([\d,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(",", ""))
            trx.currency = "IDR"
            trx.fees = 0  # No fees for funds transfer

        # Extract payment method
        payment_method_pattern = r"FROM\s+[A-Za-z\s]+\s+([A-Za-z]+)\s+IDR"
        payment_method_match = re.search(payment_method_pattern, email)
        if payment_method_match:
            trx.payment_method = payment_method_match.group(1)

        # Extract description
        trx.description = "-"


    def _extract_top_up(self, email: str, trx: TransactionData) -> None:
        """
        Extract details from the top-up email format.
        """
        # Extract trx_id
        ref_match = r"Reference\s+Number:\s+(\S+)"
        ref_match = re.search(ref_match, email)
        if ref_match:
            trx.trx_id = ref_match.group(1)

        # Extract the amount (remove 'IDR', commas, and parse the number)
        amount_pattern = r"IDR\s*([\d,]+)"
        amount_match = re.search(amount_pattern, email)
        if amount_match:
            # Remove commas and convert to Decimal
            amount_str = amount_match.group(1).replace(",", "")
            # Set currency
            trx.currency = "IDR"
            trx.amount = Decimal(amount_str)
            trx.fees = 0  # No fees for top-up

        # Set description
        trx.description = "-"

        # Set merchant name
        merchant_pattern = r"TO\s*(.*?)\s*\d{10,}"
        merchant_match = re.search(merchant_pattern, email)
        if merchant_match:
            trx.merchant = merchant_match.group(1)

        # Extract transaction date
        date_pattern = r"PAYMENT DATE:\s*(\d{2} \w+ \d{4} \d{2}:\d{2}:\d{2})"
        date_match = re.search(date_pattern, email)
        if date_match:
            trx.date = datetime.strptime(date_match.group(1), "%d %b %Y %H:%M:%S")        

    def _extract_value(self, pattern: str, email: str) -> Optional[str]:
        """
        Helper function to extract the first match of a given regex pattern from the email content.
        """
        match = re.search(pattern, email)
        return match.group(1) if match else None
