from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime

class EGExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the EG transaction receipt format.
        """
        return email_from == "help@acct.epicgames.com" and "Your Epic Games Receipt" in title
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()
        # Example format:
        #Thank You.

        #Hi Darius!
        #Thanks for your purchase from Epic Games Commerce GmbH.
        #
        #INVOICE ID:
        #F3281830883
        #
        #YOUR ORDER INFORMATION:
        #
        #Order ID: Bill To:
        #F2401041706008733 dariusmputra@gmail.com
        #Order Date: Source:
        #January 4, 2024 Epic Games Store
        #
        #HERE'S WHAT YOU ORDERED:
        #
        #Description: Publisher: Price:
        #Marvel's Guardians of the Galaxy Eidos Interactive Corporation Rp879000.00 IDR
        #Discounts:
        #Sale Discount \- Rp879000.00 IDR
        #TOTAL: Rp0.00 IDR
        #Please keep a copy of this receipt for your records.
        #View your purchase history
        #View your Epic Rewards balance
        #Games and apps purchased on the Epic Games Store are eligible for a refund
        #within 14 days of purchase (or 14 days after release for pre-purchases) if
        #they have less than 2 hours of runtime, unless otherwise stated on their Epic
        #Games Store product page. Offers that include virtual currency or other
        #consumables are marked “non-refundable” and are not eligible for refund. Most
        #in-app purchases are non-refundable. See our refund policy for more
        #information.
        #
        #Epic Games Commerce GmbH
        #D4 Platz 10 6039 Root, Switzerland
        #Tax Identification Number (TIN) : 33.001.353.3-053.000
        #
        #
        #Need Help? help.epicgames.com
        #
        #
        #(C) 2024, Epic Games, Inc. All rights reserved. Epic, Epic Games, the Epic
        #Games logo, Unreal, Unreal Engine, the Unreal Engine logo, Epic Games Store,
        #and the Epic Games Store logo are trademarks or registered trademarks of Epic
        #Games, Inc. in the USA and elsewhere. All other trademarks are the property of
        #their respective owners.
        #
        #
        #Terms of Service |  Privacy Policy

        from decimal import Decimal
import re
import datetime
from .base_extractor import BaseExtractor, EmailContent, TransactionData

class EGExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        """
        Check if the email matches the EG transaction receipt format.
        """
        return email_from == "help@acct.epicgames.com" and "Your Epic Games Receipt" in title
    
    def extract(self, content: EmailContent) -> list[TransactionData]:
        """
        Extract the transaction data from the email.
        """
        email = content.get_plaintext()

        # Clean up email content (replace multiple spaces and newlines with a single space)
        email = re.sub(r"\s+", " ", email)

        # Debugging: Print cleaned-up email content to verify
        print("Cleaned email content:")
        print(email)
        print("\n" + "-"*50 + "\n")

        trx = TransactionData()
        trx.is_incoming = False
        trx.payment_method = "Epic Games"
        trx.extra_data = {}

        # Extract total amount and currency (e.g., Rp0.00 IDR)
        total_match = re.search(r"TOTAL:\s*([\d,\.]+)\s*(\w{3})", email)
        if total_match:
            trx.amount = Decimal(total_match.group(1).replace(",", ""))
            trx.currency = total_match.group(2)
        else:
            trx.currency = "IDR"  # Default value if not found
            trx.amount = Decimal(0)

        # Extract transaction ID (Invoice ID)
        trx_id_match = re.search(r"INVOICE ID:\s*(\S+)", email)
        if trx_id_match:
            trx.trx_id = trx_id_match.group(1)
        else:
            trx.trx_id = "Unknown Invoice ID"
        
        # Extract description (Game title) between "Description:" and "Publisher:"
        # Product\s*-\s*(.*?)\s*Company
        description_match = re.search(r"Description:\s*-\s*(.*?)\s*Publisher:", email, re.DOTALL)
        if description_match:
            trx.description = description_match.group(1).strip()
        else:
            trx.description = "No description available"
        
        # Extract merchant (Publisher) between "Publisher:" and "Price:"
        merchant_match = re.search(r"Publisher:\s*-\s*(.*?)\s*Price:", email, re.DOTALL)
        if merchant_match:
            trx.merchant = merchant_match.group(1).strip()
        else:
            trx.merchant = "Unknown Publisher"

        # Extract order date (in the format Month Day, Year)
        date_match = re.search(r"Order Date:\s*([A-Za-z]+ \d{1,2}, \d{4})", email)
        if date_match:
            try:
                trx.date = datetime.datetime.strptime(date_match.group(1).strip(), "%B %d, %Y")
            except ValueError as ve:
                raise ValueError(f"Date format mismatch: {ve}")
        else:
            trx.date = None  # Optional: Or set a default date

        # Optional: Extract fees (assuming no fees in the sample email)
        trx.fees = Decimal(0)

        # Debugging: Print extracted fields to verify they were captured correctly
        print("Extracted Transaction Data:")
        print(f"Transaction ID: {trx.trx_id}")
        print(f"Description: {trx.description}")
        print(f"Merchant: {trx.merchant}")
        print(f"Date: {trx.date}")
        print(f"Amount: {trx.amount}")
        print(f"Currency: {trx.currency}")
        print(f"Fees: {trx.fees}")

        return [trx] 