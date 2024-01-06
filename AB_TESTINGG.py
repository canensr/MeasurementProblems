#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
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

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.




#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# !pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.
df_k = pd.read_excel("Measurement_problems/datasets/ab_testing.xlsx",sheet_name="Control Group")
df_t = pd.read_excel("Measurement_problems/datasets/ab_testing.xlsx",sheet_name="Test Group")

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.
df_k.sort_values("Purchase",ascending=False).head(10)
df_t.sort_values("Purchase",ascending=False).head(10)
df_k.describe().T
df_t.describe().T
# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.
df_k["Group"] = "Kontrol"
df_t["Group"] = "Test"
df = pd.concat([df_k,df_t])
df.head(10)
df.info


#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.
# Yeni teklif verme türü "avarage bidding" işe yaradı mı?

# H0 : M1 = M2  İki grup arasında istatistiksel olarak anlamlı farklılık yoktur / # Average bidding ve Maksimum Bidding purchase ortalamaları Arasında İst. Olarak An. Fark yoktur
# H1 : M1 != M2 ....vardır.

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz
df_k.describe().T
df_t.describe().T
df.groupby("Group").agg({"Purchase":"mean"})
#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################


# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz

# Normallik varsayımı
# H0: Normal dağılım varsayımı sağlanmaktadır.
# H1:..sağlanmamaktadır
test_stat, pvalue = shapiro([df_k["Purchase"]])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue)) # p>0.05 h0 reddedilemez, normal dağılıyor

test_stat, pvalue = shapiro([df_t["Purchase"]])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue)) # p>0.05 h0 reddedilemez, normal dağılıyor

# Varyans homojenliği
# H0: Varyanslar Homojendir
# H1: Varyanslar Homojen Değildir
purchase_k = np.array(df_k["Purchase"]) #iki boyutlu olmaması gerekiyor o yüzden numpyarraye çeviriyoruz
purchase_t = np.array(df_t["Purchase"])

test_stat, pvalue = levene(purchase_k,purchase_t)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))  # p>0.05 h0 reddedilemez. varyanslar homojen.


# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz
# Her iki varsayım da sağlanıyor. Yani bağımsız iki örneklem t testi yapacağız. (parametrik test)
test_stat, pvalue = ttest_ind(df_k["Purchase"],
                              df_t["Purchase"],
                              equal_var=True)

print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue)) # p>0.05 h0 reddedilemez.

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

## p-value değeri 0.3493 geldi. Yani H0 hipotezini reddedemiyoruz.
# Yani her iki yöntem arasında anlamlı bir fark var diyemeyiz. H0: M1 = M2 reddedilemez.

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

#Varsayımlar sağlandığı için bağımsız iki örneklem t testi yaptık.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

#Elde ettiğimiz sonuca göre average bidding ile maximum bidding arasında purchase ortalamaları açısından anlamlı bir fark olmadığını gördük.
# Müşteriden veri sayısını arttırmasını isteyebiliriz. 3 ay daha veri toplamasını ve tekrar hipotez testi yapılmasını isteyebiliriz.
# Mevcut sonuçlara göre yeni teklif türü olan average biddingi satın almamasını tavsiye ederiz.
