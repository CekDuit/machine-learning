from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

translations = { 'Senin': 'Monday', 'Selasa': 'Tuesday', 'Rabu': 'Wednesday', 'Kamis': 'Thursday', 'Jumat': 'Friday', 'Sabtu': 'Saturday', 'Minggu': 'Sunday', 'Januari': 'January', 'Februari': 'February', 'Maret': 'March', 'April': 'April', 'Mei': 'May', 'Juni': 'June', 'Juli': 'July', 'Agustus': 'August', 'September': 'September', 'Oktober': 'October', 'November': 'November', 'Desember': 'December' }

class TokopediaExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        return "Checkout Pesanan" in title and email_from == "noreply@tokopedia.com"

    def extract(self, content: EmailContent) -> list[TransactionData]:
        df = content.get_dfs(thousands=".", decimal=",")
        pt = content.get_plaintext()

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = str(df[3].iloc[1,1])

        trx.merchant = re.search(r"Toko: (.+)", pt).group(1).strip()
        
        # For currency, split before space
        currency, amount = str(df[3].iloc[0, 1]).split(" ")
        trx.currency = "IDR" if currency == "Rp" else currency
        trx.amount = Decimal(amount.replace(".", "").replace(",", ""))

        trx.trx_id = re.search(r"No\. Invoice: (INV/[A-Z0-9/]+)\s+", pt).group(1)
        trx.description = ""

        date_string = str(df[3].iloc[2, 1])
        for ind, eng in translations.items():
            date_string = date_string.replace(ind, eng)
            
        # re.search(r"(\d{2} \w+ \d{2} \d{2}:\d{2})", pt).group(0)
        
        
        trx.date = datetime.datetime.strptime(date_string, "%A, %d %B %Y, %H:%M WIB")
        
        return [trx]
