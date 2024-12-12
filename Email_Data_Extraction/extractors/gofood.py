from decimal import Decimal
from .base_extractor import BaseExtractor, EmailContent, TransactionData
import re
import datetime


class GoFoodExtractor(BaseExtractor):
    def match(self, title: str, email_from: str) -> bool:
        valid_titles = ["your food order with gojek", "pesanan makananmu bersama gojek"]
        valid_emails = [
            "no-reply@invoicing.gojek.com"
            # "m320b4ky1551@bangkit.academy"
        ]
        is_title_valid = any(
            valid_title in title.lower() for valid_title in valid_titles
        )
        is_email_valid = any(
            valid_email in email_from.lower() for valid_email in valid_emails
        )

        return is_title_valid and is_email_valid

        # return "your food order" in title.lower() and "no-reply@invoicing.gojek.com" in email_from.lower()

    def extract(self, content: EmailContent) -> list[TransactionData]:
        email = content.get_plaintext()
        # Example format:
        # gofood
        # Wednesday, 2 August 2023
        # Order ID: F-2178695239
        # Hi KIKO,
        # Thanks for ordering GoFood
        # Total paid: Rp57.000
        # Order details:
        # 3 Mie Gacoan IV 0 @Rp14.000 Rp42.000
        # 1 Udang Rambutan @Rp13.000 Rp13.000
        # Total Price: Rp55.000
        # Delivery fee: Rp13.000
        # Other fee(s): Rp3.000
        # Discounts: -Rp14.000
        # Total payment: Rp57.000
        # Paid with GoPay: Rp50.000
        # Paid with Cash: Rp7.000
        # Delivery details:
        # Zainur Rahman
        # Delivered on 2 August 2023 at 13:47
        # Distance: 3.9 km
        # Delivery time: 45 mins

        # Create transaction object
        trx = TransactionData()
        trx.is_incoming = False
        pattern = r"(?:from|dari)\s*\n(.*?)(?=,|\n)"
        match = re.search(pattern, email)
        if match:
            trx.merchant = match.group(1)
        else:
            trx.merchant = None
        trx.currency = "IDR"

        total_payment_match = re.search(
            r"Total (payment|pembayaran)\s*Rp([\d.]+)", email
        )
        trx.amount = Decimal(total_payment_match.group(2).replace(".", ""))

        payment_match = re.findall(
            r"(?:Paid with|Bayar pakai)\s+([A-Za-z\s]+)(?=\s+Rp|$)", email
        )

        payment_methods = []
        payment_methods.extend(payment_match)
        trx.payment_method = " + ".join(payment_methods)

        trx.description = ""

        # bulan_map = {
        #     "Januari": "January", "Februari": "February", "Maret": "March",
        #     "April": "April", "Mei": "May", "Juni": "June",
        #     "Juli": "July", "Agustus": "August", "September": "September",
        #     "Oktober": "October", "November": "November", "Desember": "December"
        # }

        # date_match = re.search(r"(?:Delivered on|Diantarkan)\s+(\d+ \w+ \d{4}) at (\d{2}:\d{2})", email)
        # if date_match:
        #     date_str = date_match.group(1)
        #     time_str = date_match.group(2)
        #     for indo, eng in bulan_map.items():
        #         date_str = date_str.replace(indo, eng)
        #     trx.date = datetime.datetime.strptime(f"{date_str} {time_str}", "%d %B %Y %H:%M")

        hari_map = {
            "Senin": "Monday",
            "Selasa": "Tuesday",
            "Rabu": "Wednesday",
            "Kamis": "Thursday",
            "Jumat": "Friday",
            "Sabtu": "Saturday",
            "Minggu": "Sunday",
        }

        bulan_map = {
            "Januari": "January",
            "Februari": "February",
            "Maret": "March",
            "April": "April",
            "Mei": "May",
            "Juni": "June",
            "Juli": "July",
            "Agustus": "August",
            "September": "September",
            "Oktober": "October",
            "November": "November",
            "Desember": "December",
        }

        # Merge English and Indonesian day names
        hari_map.update(
            {
                "Monday": "Monday",
                "Tuesday": "Tuesday",
                "Wednesday": "Wednesday",
                "Thursday": "Thursday",
                "Friday": "Friday",
                "Saturday": "Saturday",
                "Sunday": "Sunday",
            }
        )

        # Try different date parsing patterns
        date_match_2022 = re.search(
            r"(?:on\s+)?((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)),?\s+(\d+)\s+(\w+)\s+(\d{4})",
            email,
        )
        date_match_2023_2024 = re.search(
            r"(?:Delivered on|Diantarkan)\s+(\d+ \w+ \d{4}) at (\d{2}:\d{2})", email
        )

        # Initialize date and time variables
        date_str = None
        time_str = "00:00"  # Default time if not found

        if date_match_2022:
            # Parse date from the first pattern (2022 style)
            hari = date_match_2022.group(1)
            tanggal = date_match_2022.group(2)
            bulan = date_match_2022.group(3)
            tahun = date_match_2022.group(4)

            hari_eng = hari_map.get(hari, hari)
            bulan_eng = bulan_map.get(bulan, bulan)

            date_str = f"{tanggal} {bulan_eng} {tahun}"

        elif date_match_2023_2024:
            # Parse date from the second pattern (2023-2024 style)
            date_str = date_match_2023_2024.group(1).strip()
            time_str = date_match_2023_2024.group(2)

            # Replace Indonesian month names with English
            for indo, eng in bulan_map.items():
                date_str = date_str.replace(indo, eng)

        else:
            print("Tanggal tidak ditemukan dalam email")
            trx.date = None
            return [trx]

        try:
            # Try parsing without day name first
            try:
                trx.date = datetime.datetime.strptime(
                    f"{date_str} {time_str}", "%d %B %Y %H:%M"
                )
            except ValueError:
                # If that fails, try with day name
                trx.date = datetime.datetime.strptime(
                    f"{date_str} {time_str}", "%A, %d %B %Y %H:%M"
                )
        except ValueError as e:
            print(f"Error parsing date: {e}")
            trx.date = None

        match = re.search(r"(?:Order ID|ID pesanan):\s*(\S+)", email)
        trx.trx_id = match.group(1)

        return [trx]
