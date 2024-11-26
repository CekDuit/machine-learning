# from mybca import MyBCAExtrator

# data = """
# Status : Successful
# Transaction Date : 19 Nov 2024 17:52:19
# Transfer Type : Transfer to BCA Account
# Source of Fund : 7625xxxx00
# Source Currency : IDR - Indonesian Rupiah
# Beneficiary Account : 0000000000
# Target Currency : IDR - Indonesian Rupiah
# Beneficiary Name : John Doe
# Target Amount : IDR 1,000,000.00
# Remarks : -
# Reference No. : C000000-50000-400000-0000-BE000000
# """

# print(str(MyBCAExtrator().extract(data)[0]))


# from jago import JagoExtractor

# data = """
# Dari : MA • 1039984217777
# Ke : BUBU Store
# Jumlah : Rp35.000
# Tanggal transaksi : 14 August 2024 23:51 WIB
# """

# print(str(JagoExtractor().extract(data)[0]))


from livin import JagoExtractor

# Contoh email
data = """
Dari : MA • 1039984217777
Ke : BUBU Store
Jumlah : Rp35.000
Tanggal transaksi : 14 August 2024 23:51 WIB
"""

print(str(JagoExtractor().extract(data)[0]))
