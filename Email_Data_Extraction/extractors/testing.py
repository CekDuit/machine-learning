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

#from extractors.bri import BRIExtractor
#
#data_transfer = """
#Halo, ROHIMA
#Berikut ini adalah informasi transaksi yang telah Anda lakukan #di Aplikasi BRImo.
#Tanggal                  : 22 November 2024 , 20:06:34 WIB
#Nomor Referensi          : 764780384974
#Sumber Dana              : ROHIMA 6476 **** **** 534
#Jenis Transaksi          : Transfer BI-FAST
#Bank Tujuan              : BANK BCA
#Nomor Tujuan             : 6120 4876 88
#Nama Tujuan              : FERNANDO ALBERTUS
#Catatan                  : -
#Nominal                  : Rp35.000
#Biaya Admin              : Rp2.500
#"""
#
#data_topup = """
#Halo, ROHIMA
#Berikut ini adalah informasi transaksi yang telah Anda lakukan #di Aplikasi BRImo.
#16 November 2024, 21:00:55 WIB
#No. Ref : 762178203330
#ShopeePay
#p0000XXXXC
#082123520349
#Jenis Transaksi
#ShopeePay
#Catatan
#-
#Nominal
#Rp80.000
#Biaya Admin
#Rp0
#"""
#
#print("\nHasil Transfer:")
#transfer_title = "Pemindahan Dana"
#for trx in BRIExtractor()._extract_title(data_transfer, #transfer_title):
#    print(trx)
#
#print("\nHasil Top-Up:")
#topup_title = "Top Up"
#for trx in BRIExtractor()._extract_title(data_topup, topup_title)#:
#    print(trx)
#
#
#from extractors.ocbc import OCBCExtractor
#
## Example email content from one of the screenshots as text
#data_top_up = """
#Dear Mr/Mrs/Ms FX SURYA DARMAWAN,
#Thank you for using Online Banking OCBC.
#We are pleased to inform you that the following request for bill #payment has been successful.
#
#FROM:
#FX SURYA DARMAWAN
#IDR MB202411251007305558
#
#TO:
#SHOPEEPAY
#082110005254
#
#PAYMENT AMOUNT:
#IDR 101,000
#
#PAYMENT DATE:
#25 Nov 2024 10:07:30 WIB
#
#Reference Number: MB202411251007305558
#"""
#
#data_transfer = """
#Bapak/Ibu yang terhormat,
#Terima kasih atas kepercayaan Bapak/Ibu kepada OCBC sebagai #rekan perbankan selama ini.
#
#Dengan ini kami sampaikan bahwa rekening Bapak/Ibu telah #menerima Transfer Dana Masuk BI-Fast dengan rincian sebagai #berikut:
#
#Bank Pengirim       : BANK CENTRAL ASIA
#Nama Pengirim       : FX SURYA DARMAWAN
#No Rekening Pengirim: 1921109305
#Nominal             : Rp 400.000,00
#
#Bank Penerima       : OCBC
#Nama Penerima       : FX SURYA DARMAWAN
#No Rekening Penerima: 693815277043
#Tanggal Transaksi   : 04 November 2024
#Waktu Transaksi     : 16:22:24
#"""
#
## Print the extracted transactions
#print("\nTop-Up Transaction Details:")
#topup_title = "Top Up"
#for trx in OCBCExtractor()._extract_title(data_top_up, #topup_title):
#    print(trx)
#
#print("\nTransfer Transaction Details:")
#transfer_title = "Transfer"
#for trx in OCBCExtractor()._extract_title(data_transfer, #transfer_title):
#    print(trx)
#
#
#from extractors.ovo import OVOExtractor
#
#data = """
#Nama Acquirer    : BCA
#Nama Toko        : TRUSTEA
#Lokasi           : SURABAYA, 60293 ID
#No. Referensi    : #p01-240917-fd2f8c4f-f6aa-491b-9149-31beeb122126
#No. Resi (Kode Transaksi) : 072bbc31f9ba
#Kode Approval    : 634065
#Metode Pembayaran: OVO Cash
#Pembayaran       - Rp6.000
#"""
#
#print("\nPayment Transaction Details:")
#for trx in OVOExtractor().extract(data):
#    print(trx)

# from extractors.eg import EGExtractor

# data_payment = """
# Thank You.
# Hi Darius!
# Thank you for your purchase!

# INVOICE ID:     F3714270093
# YOUR ORDER INFORMATION:
# Order ID:       F2409060937042320           
# Bill To:        dariusmputra@gmail.com
# Order Date:     September 6, 2024
# Source: Epic Games Store
# HERE'S WHAT YOU ORDERED:
# Description:    Sniper Ghost Warrior Contracts
# Publisher:      CI Games
# Price:	        Rp224980.00 IDR
# Discounts:	
# Sale Discount	- Rp224980.00 IDR
# TOTAL:	Rp0.00 IDR
# """

# # Print the extracted transactions
# print("\nEpic Games Transaction Details:")
# title = "Your Epic Games Receipt"
# for trx in EGExtractor()._extract_title(data_payment, title):
#     print(trx)


# from extractors.unipin import UniPinExtractor

# data = """
# Terima Kasih Atas Pembelian Anda! :)
# Nomor Transaksi	S1923922317
# Tipe Voucher	33 Garena Shells
# Nominal Transaksi	IDR 10.000 (with VAT)
# Voucher	Serial : 142252201
# PIN : 4476300011238140
# """

# # Print the extracted transactions
# print("\nUniPin Transaction Details:")
# title = "UniPin::Voucher Receipt"
# for trx in UniPinExtractor()._extract_title(data, title):
#     print(trx)


# from extractors.mobapay import MobaPayExtractor

# data = """
# Payment Successful
# Order No.:	1621806413359710208
# Username:	One Autumn Leaf
# Game ID:	101839969(2225)
# Email:	dariusmputra@gmail.com
# Payment Time:	2023-02-04 09:42:51 (UTC)
# Amount:	1
# Item Name:	40 Diamond + 4 Bonus
# Currency:	IDR
# Region:	ID
# Price:	12.000..00 IDR
# Payment Methods:	Unipin ShopeePay Wallet
# Subtotal:	12.000..00 IDR
# """

# print("\nMobaPay Transaction Details:")
# title = "Payment Successful"
# for trx in MobaPayExtractor()._extract_title(data, title):
#     print(trx)


# from extractors.xsolla import XsollaExtractor

# data = """
# Purchase Confirmation
# Product - Epic Games Commerce GmbH
# Company	Xsolla (USA), Inc.
# 15260 Ventura Boulevard, Suite 2230, Sherman Oaks, California, 91403
# TIN 33.001.301.2-053.000
# Transaction number	1545704795
# Transaction date	11/26/2024
# Purchase description	Watch Dogs: Legion Deluxe Edition
# Order Id	A2411260937452527
# Country	Indonesia
# Subtotal	Rp103 254.00
# TotalRp103 254.00
# Including 11% VAT : Rp10 233.00
# Thank you for using Xsolla!
# """

# print("\nXsolla Transaction Details:")
# title = "Your receipt"
# for trx in XsollaExtractor()._extract_title(data, title):
#     print(trx)


# from google_play import GooglePlayExtractor

# # Contoh email
# data = """
# Order number: GPA.3335-0097-8360-50910
# Order date: 2 Dec 2024 18:20:35 GMT+7
# Your account: fxsurya27@gmail.com
# Item            Price
# True Premium (xxxxx) Rp 39.000,00/month
# Auto-renewing subscription
# Tax: Rp 2.090,00
# Total: Rp 41.090,00/month
# Payment method: ShopeePay: **** 6235
# """

# print(str(GooglePlayExtractor().extract(data)[0]))


# from paypal import PaypalExtractor

# # Contoh email
# data = """
# Data_Transfer
# Anda mengirim $2,00 USD ke asukti
# CATATAN ANDA UNTUK asukti asukti
# “Transfer Jajan”
# Perincian Transaksi
# ID transaksi: 49S77625NF073893R
# Tanggal transaksi: 1 Mei 2023
# Pembayaran terkirim: $2,00 USD
# Biaya: $0,00 USD
# Dibayar dengan: Saldo PayPal (USD)
# Anda membayar: $2,00 USD
# """

# print(str(PaypalExtractor().extract(data)[0]))


# from paypal import PaypalExtractor

# # Contoh email
# data = """
# Data_Terima
# Run Jie Soo telah mengirim $2,50 USD kepada Anda
# Perincian Transaksi
# ID transaksi: 1JE26965PL263253S
# Tanggal transaksi: 12 Mei 2023
# Jumlah yang diterima: $2,50 USD
# Biaya: $0,41 USD
# Total: $2,09 USD
# """

# print(str(PaypalExtractor().extract(data)[0]))


# from steam import SteamExtractor

# # Contoh email
# data = """
# You've earned Steam Points
# Fallout 4: Game of the Year Edition
# Subtotal (excl. VAT): Rp 119,820
# VAT at 11%: Rp 13,180
# Total: Rp 133,000
# NBA 2K24 Kobe Bryant Edition
# Subtotal (excl. VAT): Rp 94,991
# VAT at 11%: Rp 10,449
# Total: Rp 105,440
# Account name: darkiki27
# Invoice: 3869230398088464184
# Date issued: 17 Apr, 2024 @ 8:58pm WIB
# Billing address: ...
# Total: Rp 238,440
# Payment method: Visa
# """

# print(str(SteamExtractor().extract(data)[0]))