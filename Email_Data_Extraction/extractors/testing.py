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


# from seabank import SeaBankExtractor

# # Contoh email
# data = """
# Waktu Transaksi : 22 Nov 2024 18:48
# Jenis Transaksi : Real Time (BI-FAST)
# Transfer Dari : BOBO DELONA-XXXXXXXXX3859
# Rekening Tujuan : JAGO-XXXXXXXXX2337
# Jumlah : Rp200.000
# No. Referensi : 202411224350224969367
# """

# print(str(SeaBankExtractor().extract(data)[0]))



from livin import MandiriExtractor

data_transfer = """
Data_Transfer
Penerima : FLIPTECH LENTERA INS
Bank Mandiri - 157000534545393
Tanggal : 13 Nov 2024
Jam : 15:53:45 WIB
Jumlah Transfer : Rp200.406,00
No. Referensi : 2411131121092046786
Keterangan : -
Rekening Sumber : DADADA TELY
*****5683
"""

data_topup = """
Data_TopUp
Penyedia Jasa : 3 Prepaid
****0248
Tanggal : 13 Nov 2024
Jam : 15:53:45 WIB
Nominal Top-up : Rp 40.000,00
Biaya Transaksi : Rp 0,00
Total Transaksi : Rp 40.000,00
No. Referensi : 702410291310161710
Rekening Sumber : ARISTO TELY
*****5683
"""

data_payment = """
Data_Payment
Penerima : KOPI 7 KAMBANG IWAK -HO
PALEMBANG - ID
Tanggal : 13 Nov 2024
Jam : 18:35:00 WIB
Nominal Transaksi : Rp 124.300,00
No. Referensi : 2410291122532788441
No. Referensi QRIS : 410698015472
Merchant PAN : 9360001430019008082
Customer PAN : 9360000812187256836
Pengakuisisi : Bank BCA
Terminal ID : A2917806
Sumber Dana : ARISTO TELY
*****5683
"""

print("Hasil Transfer:")
print(str(MandiriExtractor().extract(data_transfer)[0]))

print("\nHasil Top-Up:")
print(str(MandiriExtractor().extract(data_topup)[0]))

print("\nHasil Payment:")
print(str(MandiriExtractor().extract(data_payment)[0]))