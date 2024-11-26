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



#from livin import MandiriExtractor
#
#data_transfer = """
#Data_Transfer
#Penerima : FLIPTECH LENTERA INS
#Bank Mandiri - 157000534545393
#Tanggal : 13 Nov 2024
#Jam : 15:53:45 WIB
#Jumlah Transfer : Rp200.406,00
#No. Referensi : 2411131121092046786
#Keterangan : -
#Rekening Sumber : DADADA TELY
#*****5683
#"""
#
#data_topup = """
#Data_TopUp
#Penyedia Jasa : 3 Prepaid
#****0248
#Tanggal : 13 Nov 2024
#Jam : 15:53:45 WIB
#Nominal Top-up : Rp 40.000,00
#Biaya Transaksi : Rp 0,00
#Total Transaksi : Rp 40.000,00
#No. Referensi : 702410291310161710
#Rekening Sumber : ARISTO TELY
#*****5683
#"""
#
#data_payment = """
#Data_Payment
#Penerima : KOPI 7 KAMBANG IWAK -HO
#PALEMBANG - ID
#Tanggal : 13 Nov 2024
#Jam : 18:35:00 WIB
#Nominal Transaksi : Rp 124.300,00
#No. Referensi : 2410291122532788441
#No. Referensi QRIS : 410698015472
#Merchant PAN : 9360001430019008082
#Customer PAN : 9360000812187256836
#Pengakuisisi : Bank BCA
#Terminal ID : A2917806
#Sumber Dana : ARISTO TELY
#*****5683
#"""
#
#print("Hasil Transfer:")
#print(str(MandiriExtractor().extract(data_transfer)[0]))
#
#print("\nHasil Top-Up:")
#print(str(MandiriExtractor().extract(data_topup)[0]))
#
#print("\nHasil Payment:")
#print(str(MandiriExtractor().extract(data_payment)[0]))

from bri import BRIExtractor

data_transfer = """
Halo, ROHIMA
Berikut ini adalah informasi transaksi yang telah Anda lakukan di Aplikasi BRImo.
Tanggal                  : 22 November 2024 , 20:06:34 WIB
Nomor Referensi          : 764780384974
Sumber Dana              : ROHIMA 6476 **** **** 534
Jenis Transaksi          : Transfer BI-FAST
Bank Tujuan              : BANK BCA
Nomor Tujuan             : 6120 4876 88
Nama Tujuan              : FERNANDO ALBERTUS
Catatan                  : -
Nominal                  : Rp35.000
Biaya Admin              : Rp2.500
"""

data_topup = """
Halo, ROHIMA
Berikut ini adalah informasi transaksi yang telah Anda lakukan di Aplikasi BRImo.
16 November 2024, 21:00:55 WIB
No. Ref : 762178203330
ShopeePay
p0000XXXXC
082123520349
Jenis Transaksi
ShopeePay
Catatan
-
Nominal
Rp80.000
Biaya Admin
Rp0
"""

print("\nHasil Transfer:")
transfer_title = "Pemindahan Dana"
for trx in BRIExtractor().extract(data_transfer, transfer_title):
    print(trx)

print("\nHasil Top-Up:")
topup_title = "Top Up"
for trx in BRIExtractor().extract(data_topup, topup_title):
    print(trx)


from ocbc import OCBCExtractor

# Example email content from one of the screenshots as text
data_top_up = """
Dear Mr/Mrs/Ms FX SURYA DARMAWAN,
Thank you for using Online Banking OCBC.
We are pleased to inform you that the following request for bill payment has been successful.

FROM:
FX SURYA DARMAWAN
IDR MB202411251007305558

TO:
SHOPEEPAY
082110005254

PAYMENT AMOUNT:
IDR 101,000

PAYMENT DATE:
25 Nov 2024 10:07:30 WIB

Reference Number: MB202411251007305558
"""

data_transfer = """
Bapak/Ibu yang terhormat,
Terima kasih atas kepercayaan Bapak/Ibu kepada OCBC sebagai rekan perbankan selama ini.

Dengan ini kami sampaikan bahwa rekening Bapak/Ibu telah menerima Transfer Dana Masuk BI-Fast dengan rincian sebagai berikut:

Bank Pengirim       : BANK CENTRAL ASIA
Nama Pengirim       : FX SURYA DARMAWAN
No Rekening Pengirim: 1921109305
Nominal             : Rp 400.000,00

Bank Penerima       : OCBC
Nama Penerima       : FX SURYA DARMAWAN
No Rekening Penerima: 693815277043
Tanggal Transaksi   : 04 November 2024
Waktu Transaksi     : 16:22:24
"""

# Print the extracted transactions
print("\nTop-Up Transaction Details:")
for trx in OCBCExtractor().extract(data_top_up):
    print(trx)

print("\nTransfer Transaction Details:")
for trx in OCBCExtractor().extract(data_transfer):
    print(trx)


from ovo import OVOExtractor

data = """
Nama Acquirer    : BCA
Nama Toko        : TRUSTEA
Lokasi           : SURABAYA, 60293 ID
No. Referensi    : p01-240917-fd2f8c4f-f6aa-491b-9149-31beeb122126
No. Resi (Kode Transaksi) : 072bbc31f9ba
Kode Approval    : 634065
Metode Pembayaran: OVO Cash
Pembayaran       - Rp6.000
"""

print("\nPayment Transaction Details:")
for trx in OVOExtractor().extract(data):
    print(trx)