import datetime
from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re


class GrabExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Test if the email matches the extractor
        """
        if title == "Your Grab E-Receipt":
            return True
        return False

    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract transactions from the email content
        Currently, only GrabCar is supported.
        """
        dfs = content.get_dfs(thousands=".", decimal=",")
        str1 = dfs[0].iloc[0][0]
        if "GrabCar" not in str1:
            raise ValueError("Grab parser currently only supports GrabCar.")

        trx = TransactionData()
        trx.is_incoming = False
        trx.amount = Decimal(str(dfs[8].iloc[0][1]))
        trx.merchant = "Grab"
        trx.payment_method = dfs[10].iloc[0][1]
        trx.currency = "IDR"
        trx.description = "GrabCar Trip"

        trip_info = dfs[1].iloc[0][0]
        # Example: GrabCar  Hope you enjoyed your ride!  Picked up on 20 November 2024  Booking ID: A-7A7B7C7D7E
        trip_date, booking_id = re.search(r"on (\d{1,2}\s\w+\s\d{4})\s+Booking ID:\s+([A-Z0-9-]+)", trip_info).groups()  # type: ignore
        trx.date = datetime.datetime.strptime(trip_date, "%d %B %Y")
        trx.trx_id = booking_id

        return [trx]
