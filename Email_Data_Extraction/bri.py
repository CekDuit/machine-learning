from decimal import Decimal
from base_extractor import BaseExtractor, TransactionData
import re
import datetime

class BRIExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the BRI transaction receipt format.
        """
        return email_from == "noreply@bri.co.id" and "Berhasil" in title

    def extract(self, email: str, title: str) -> list[TransactionData]:
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
        date_match = re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2}:\d{2} WIB)", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %B %Y, %H:%M:%S WIB")
        else:
            raise ValueError("Date not found in email")

        ref_match = re.search(r"No\. Ref\s*:\s*(.+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")

        # Extract sender name (for top-ups, the sender name might not be explicitly present)
        trx.sender_name = "Unknown Sender"

        # Extract recipient name
        recipient_match = re.search(r"ShopeePay|DANA|OVO|Gopay|Nama Tujuan", email)
        trx.recipient_name = recipient_match.group(0).strip() if recipient_match else "Unknown Recipient"

        # Extract payment details
        nominal_match = re.search(r"Nominal\s*Rp([\d\.]+)", email)
        if nominal_match:
            trx.amount = Decimal(nominal_match.group(1).replace(".", ""))
        else:
            raise ValueError("Nominal not found in email")

        fees_match = re.search(r"Biaya Admin\s*Rp([\d\.]+)", email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", ""))
        else:
            trx.fees = Decimal("0")

        trx.description = f"Top Up {trx.recipient_name}"
        return [trx]


    def _extract_transfer(self, email: str, title: str) -> list[TransactionData]:
        """
        Extract details for the Transfer format.
        """
        trx = TransactionData()
        trx.currency = "IDR"

        # Extract general fields
        date_match = re.search(r"Tanggal\s*:\s*(.+)", email)
        if date_match:
            trx.date = datetime.datetime.strptime(date_match.group(1), "%d %B %Y , %H:%M:%S WIB")
        else:
            raise ValueError("Transaction date not found in email")

        ref_match = re.search(r"Nomor Referensi\s*:\s*(.+)", email)
        if ref_match:
            trx.trx_id = ref_match.group(1)
        else:
            raise ValueError("Transaction reference number not found in email")

        # Extract sender name
        sender_match = re.search(r"Sumber Dana\s*:\s*(.+)", email)
        trx.sender_name = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Extract recipient name
        recipient_match = re.search(r"Nama Tujuan\s*:\s*(.+)", email)
        trx.recipient_name = recipient_match.group(1).strip() if recipient_match else "Unknown Recipient"

        # Extract payment details
        amount_match = re.search(r"Nominal\s*:\s*Rp([\d\.]+)", email)
        if amount_match:
            trx.amount = Decimal(amount_match.group(1).replace(".", ""))
        else:
            raise ValueError("Nominal not found in email")

        fees_match = re.search(r"Biaya Admin\s*:\s*Rp([\d\.]+)", email)
        if fees_match:
            trx.fees = Decimal(fees_match.group(1).replace(".", ""))
        else:
            raise ValueError("Fees not found in email")

        trx.description = "Transfer to " + trx.recipient_name

        return [trx]