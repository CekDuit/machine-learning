from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class OcbcExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the OCBC payment receipt format.
        """
        return title in ["Successful Bill Payment", "TRANSFER DANA MASUK BI-FAST"] and email_from in ["callcenter@ocbcnisp.com", "noreply@ocbcnisp.com"]

    def extract(self, title: str, email_from: str, email: str) -> list[TransactionData]:
        """
        Extract payment details from the OCBC email content.
        """
        transactions = []
        
        # Extract from Format 1
        trx = self._extract_top_up(email)
        if trx:
            transactions.append(trx)

        # Extract from New Format (From Image)
        trx = self._extract_transfer(email)
        if trx:
            transactions.append(trx)

        return transactions

    def _extract_top_up(self, email: str) -> TransactionData | None:
        """
        Extract details from the existing format.
        """
        from_match = re.search(r"FROM\s*:\s*([\w\s]+)\nIDR\s([\d\-]+)", email)
        to_match = re.search(r"TO\s*:\s*(.+)\n([\d\s]+)", email)
        amount_match = re.search(r"PAYMENT AMOUNT\s*IDR\s([\d,]+)", email)
        date_match = re.search(r"PAYMENT DATE\s*:\s*(\d{2}/\w+/\d{4})", email)
        ref_match = re.search(r"Reference Number:\s*(\d+)", email)
        
        if from_match and to_match and amount_match and date_match and ref_match:
            trx = TransactionData()
            sender_name = from_match.group(1).strip()
            sender_account = from_match.group(2).strip()
            recipient_name = to_match.group(1).strip()
            recipient_account = to_match.group(2).strip()
            trx.merchant = recipient_name
            trx.currency = "IDR"
            trx.amount = Decimal(amount_match.group(1).replace(",", ""))
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d/%b/%Y")
            trx.trx_id = ref_match.group(1)
            trx.description = "Payment via OCBC NISP"
            return trx
        return None

    def _extract_transfer(self, email: str) -> TransactionData | None:
        """
        Extract details from the new format (based on the image provided).
        """
        bank_sender_match = re.search(r"Bank Pengirim\s*:\s*([\w\s]+)", email)
        sender_name_match = re.search(r"Nama Pengirim\s*:\s*([\w\s]+)", email)
        sender_account_match = re.search(r"No Rekening Pengirim\s*:\s*([\d\-]+)", email)
        amount_match_new = re.search(r"Nominal\s*:\s*Rp\s([\d,.]+)", email)
        recipient_bank_match = re.search(r"Bank Penerima\s*:\s*([\w\s]+)", email)
        recipient_name_match = re.search(r"Nama Penerima\s*:\s*([\w\s]+)", email)
        recipient_account_match = re.search(r"No Rekening Penerima\s*:\s*([\d\-]+)", email)
        transaction_date_match = re.search(r"Tanggal Transaksi\s*:\s*(\d{2}\s\w+\s\d{4})", email)
        transaction_time_match = re.search(r"Waktu Transaksi\s*:\s*(\d{2}:\d{2}:\d{2})", email)
        
        if (
            bank_sender_match and sender_name_match and sender_account_match and amount_match_new and
            recipient_bank_match and recipient_name_match and recipient_account_match and 
            transaction_date_match and transaction_time_match
        ):
            trx = TransactionData()
            sender_name = sender_name_match.group(1).strip()
            sender_account = sender_account_match.group(1).strip()
            trx.currency = "IDR"
            trx.amount = Decimal(amount_match_new.group(1).replace(".", "").replace(",", ""))
            recipient_name = recipient_name_match.group(1).strip()
            recipient_account = recipient_account_match.group(1).strip()
            trx.merchant = recipient_account
            trx.date = datetime.datetime.strptime(transaction_date_match.group(1).strip(), "%d %B %Y")
            trx.description = f"Transfer from {bank_sender_match.group(1).strip()} to {recipient_bank_match.group(1).strip()}"
            trx.trx_id = f"{trx.date.strftime('%Y%m%d')}-{transaction_time_match.group(1).strip()}"  # Generate unique ID
            return trx
        return None