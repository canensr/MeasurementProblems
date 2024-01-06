#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olanbombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testiyapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.


#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç

#####################################################
# Proje Görevleri
#####################################################

#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz.
# Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.


import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, ttest_ind


pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


df_control = pd.read_excel("ab_testing.xlsx",sheet_name="Control Group")
df_control.head()


df_test = pd.read_excel("ab_testing.xlsx",sheet_name="Test Group")
df_test.head()


# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df_control)
check_df(df_test)



# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df_control["Group"] = "Control"
df_test["Group"] = "Test"

df = pd.concat([df_control,df_test],axis=0,ignore_index=True)
df.head()
df.tail()
# Out[27]:
#      Impression      Click  Purchase    Earning    Group
# 0   82529.45927 6090.07732 665.21125 2311.27714  Control
# 1   98050.45193 3382.86179 315.08489 1742.80686  Control
# 2   82696.02355 4167.96575 458.08374 1797.82745  Control
# 3  109914.40040 4910.88224 487.09077 1696.22918  Control
# 4  108457.76263 5987.65581 441.03405 1543.72018  Control
# ..          ...        ...       ...        ...      ...
# 75  79234.91193 6002.21358 382.04712 2277.86398     Test
# 76 130702.23941 3626.32007 449.82459 2530.84133     Test
# 77 116481.87337 4702.78247 472.45373 2597.91763     Test
# 78  79033.83492 4495.42818 425.35910 2595.85788     Test
# 79 102257.45409 4800.06832 521.31073 2967.51839     Test

df.info()
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 80 entries, 0 to 79
# Data columns (total 5 columns):
#  #   Column      Non-Null Count  Dtype
# ---  ------      --------------  -----
#  0   Impression  80 non-null     float64
#  1   Click       80 non-null     float64
#  2   Purchase    80 non-null     float64
#  3   Earning     80 non-null     float64
#  4   Group       80 non-null     object
# dtypes: float64(4), object(1)
# memory usage: 3.2+ KB




###############################################################################################
#                       # Görev 2:  A/B Testinin Hipotezinin Tanımlanması                       #
###############################################################################################
# Adım 1: Hipotezi tanımlayınız.

# H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
# H1 : M1!= M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark vardır.)


# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz

df.groupby("Group").agg({"Purchase":"mean"})
# Out[29]:
#          Purchase
# Group
# Control 550.89406
# Test    582.10610

#############################################################################################
#                       # GÖREV 3: Hipotez Testinin Gerçekleştirilmesi                          #
#############################################################################################

# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz
# Normallik Varsayımı :
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1: Normal dağılım varsayımı sağlanmamaktadır
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ
# Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu ?
# Elde edilen p-valuedeğerlerini yorumlayınız.

test_stat, pvalue = shapiro(df.loc[df["Group"] == "Control", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# Test Stat = 0.9773, p-value = 0.5891

test_stat, pvalue = shapiro(df.loc[df["Group"] == "Test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# Test Stat = 0.9589, p-value = 0.1541

# Sonuc
# H0 reddedilemez control grubunun değerleri normal dağılım varsayımını sağlamaktadır.
# Normallik varsayımı sağlanmasaydı varyans homojenliğine bakmadan non parametrik testine geçecektik


# Varyans Homojenliği :
# Varyans, verilerin aritmatik ortalamadan sapmalarinin karelerinin toplamidir yani standart sapmanin karekok alinmamis halidir
# H0: Varyanslar homojendir.
# H1: Varyanslar homojen Değildir.
# p < 0.05 H0 RED
# p > 0.05 H0 REDDEDİLEMEZ
# Kontrol ve test grubu için varyans homojenliğinin sağlanıp sağlanmadığını Purchase değişkeni üzerinden test ediniz.
# Test sonucuna göre normallik varsayımı sağlanıyor mu? Elde edilen p-valuedeğerlerini yorumlayınız.

test_stat, pvalue = levene(df.loc[df["Group"] == "Control", "Purchase"],
                           df.loc[df["Group"] == "Test", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# Test Stat = 2.6393, p-value = 0.1083

# Sonuc
# H0 reddedilemez control ve test grubunun değerleri varyans homojenliği varsayımını sağlamaktadır.
# Varyanslar homojendir.


# Adım 2 : Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz.
# Varsayımlar sağlandığı için bağımsız iki örneklem t testi (parametrik test) yapılmaktadır.
# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist.ol.an.fark.yoktur.)
# H1: M1 != M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında ist.ol.an.fark vardır)
# p < 0.05 H0 RED, p > 0.05 H0 REDDEDILEMEZ

test_stat, pvalue = ttest_ind(df.loc[df["Group"] == "Control", "Purchase"],
                              df.loc[df["Group"] == "Test", "Purchase"],
                              equal_var=True)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))
# Test Stat = -0.9416, p-value = 0.3493

# Sonuç
# H0 hipotezi reddedilemez çünkü p value > 0.05.

#############################################################################################
#                       GÖREV 4 : SONUÇLARIN ANALİZİ                         #
#############################################################################################
# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.
# İlk önce iki gruba da normallik testi uygulanmıştır.
# İki grubun normal dağılıma uyduğu gözlendiği için homojenlik varsayımı incelendi.
# Varyanslar homojen de çıktığı için <Bağımsız İki örneklem T Testi< uygulanmıştır.
# Uygulama sonucunda p değerinin 0.05 den büyük olduğu görülmüş ve HO hipotezi reddedilmiştir.


# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.
# Satın alma anlamında anlamlı bir fark olmadığından müşteri iki yöntemden birini seçebilir fakat diğer istatistiksel
# farklılıklarda önem arz edecektir.Tıklanma etkileşim kazanç ve dönüşüm oranlarındaki farklılıklar değerlendirilip
# hangi yöntemin daha kazançlı olduğu tespit edilebilir. Özellikle Fecabooka tıklanma başına para ödendiği için
# hangi yöntemde tıklanma oranının daha düşük olduğu tespit edilip oranına bakılabilir. iki grup gözlenmeye devam edilir.



