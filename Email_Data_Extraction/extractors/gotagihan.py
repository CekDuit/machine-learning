from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class GoTagihanExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return title == "GoTagihan Receipts" or ("GoPay" in "title" and ("Payment Receipt" in title or "Bukti Pembayaran" in title)) and email_from == "receipts@gotagihan.gojek.com"

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

        trx.trx_id = re.search(r"Payment ID - (.+\-GOBILLS)", pt).group(0)
        trx.description = ""
        trx.date = datetime.datetime.strptime(
            str(c[0].loc[0][1]),
            "%d %b %Y, %H:%M",
        )
        
        return [trx]
