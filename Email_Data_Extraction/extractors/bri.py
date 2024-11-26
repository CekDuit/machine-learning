from decimal import Decimal
from .base_extractor import BaseExtractor, TransactionData
import re
import datetime

class BriExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the BRI transaction receipt format.
        """
        return email_from == "noreply@bri.co.id" and "Berhasil" in title

    def extract(self, title: str, email_from: str, email: str) -> list[TransactionData]:
        """
        Extract payment details based on the email title and content.
        """
        if "Top Up" in title:
            return self._extract_top_up(email, title)
        elif "Pembelian" in title or "Pembayaran" in title or "Pemindahan Dana" in title:
            return self._extract_transfer(email, title)
        else:
            raise ValueError("Unknown BRI email format")

    def _extract_top_up(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the Top Up format.
        """
        trx = TransactionData()
        trx.currency = "IDR"

        # Extract general fields
        trx.date = datetime.datetime.strptime(
            re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2}:\d{2} WIB)", email).group(1),
            "%d %B %Y, %H:%M:%S WIB",
        )
        trx.trx_id = re.search(r"No\. Ref\s*:\s*(.+)", email).group(1)

        # Extract sender name
        sender_match = re.search(r"Sumber Dana\s*:\s*(.+)", email)
        sender_name = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Extract recipient name
        recipient_match = re.search(r"(ShopeePay|DANA|OVO|Nama Tujuan)\s*:\s*(.+)", email)
        recipient_name = recipient_match.group(2).strip() if recipient_match else "Unknown Recipient"

        # Extract payment details
        trx.amount = Decimal(
            re.search(r"Nominal\s*Rp([\d\.]+)", email).group(1).replace(".", "")
        )
        trx.fees = Decimal(
            re.search(r"Biaya Admin\s*Rp([\d\.]+)", email).group(1).replace(".", "")
        )
        trx.description = f"Top Up {recipient_name}"
        trx.merchant = recipient_name
        return [trx]

    def _extract_transfer(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the Transfer format.
        """
        trx = TransactionData()
        trx.currency = "IDR"

        # Extract general fields
        trx.date = datetime.datetime.strptime(
            re.search(r"Tanggal\s*:\s*(.+)", email).group(1), "%d %B %Y , %H:%M:%S WIB"
        )
        trx.trx_id = re.search(r"Nomor Referensi\s*:\s*(.+)", email).group(1)

        # Extract sender name
        sender_match = re.search(r"Sumber Dana\s*:\s*(.+)", email)
        sender_name = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Extract recipient name
        recipient_match = re.search(r"Nama Tujuan\s*:\s*(.+)", email)
        recipient_name = recipient_match.group(1).strip() if recipient_match else "Unknown Recipient"

        # Extract payment details
        trx.amount = Decimal(
            re.search(r"Nominal\s*Rp([\d\.]+)", email).group(1).replace(".", "")
        )
        trx.fees = Decimal(
            re.search(r"Biaya Admin\s*Rp([\d\.]+)", email).group(1).replace(".", "")
        )
        trx.description = "Transfer to " + recipient_name
        trx.merchant = recipient_name
        return [trx]