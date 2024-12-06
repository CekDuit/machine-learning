from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class GoTagihanExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return email_from == "receipts@gotagihan.gojek.com"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        c = content.get_dfs(thousands=".", decimal=",")
        pt = content.get_plaintext()

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "GoPay"

        trx.merchant = str(c[1].loc[0][1])
        merged_amount = str(c[1].loc[0][2])
        
        # For currency, split before first number
        first_num_idx = re.search(r"\d", merged_amount).start()
        trx.currency = merged_amount[:first_num_idx]
        trx.amount = Decimal(merged_amount[first_num_idx:].replace(".", "").replace(",", ""))

        trx.trx_id = re.search(r"(?:Payment ID|ID Pembayaran) - (.+\-GOBILLS)", pt).group(1)
        trx.description = ""
        try:
            trx.date = datetime.datetime.strptime(
                str(c[0].loc[0][1]),
                "%d %b %Y, %H:%M",
            )
        except ValueError:
            date_str = re.search(r"(\d{2} \w+ \d{4}, \d{2}:\d{2})", pt).group(0)
            trx.date = datetime.datetime.strptime(date_str, "%d %b %Y, %H:%M")
        
        return [trx]
