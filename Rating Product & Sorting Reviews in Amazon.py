
###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı



###################################################
# GÖREV 1: Average Rating'i Güncel Yorumlara Göre Hesaplayınız ve Var Olan Average Rating ile Kıyaslayınız.
###################################################

# Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır.
# Bu görevde amacımız verilen puanları tarihe göre ağırlıklandırarak değerlendirmek.
# İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.

import pandas as pd
import math
import scipy.stats as st

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
###################################################
# Adım 1: Veri Setini Okutunuz ve Ürünün Ortalama Puanını Hesaplayınız.
###################################################
df_=pd.read_csv("Measurement_problems/datasets/amazon_review.csv")
df=df_.copy()
df.head(10)
df["overall"].mean()
###################################################
# Adım 2: Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
###################################################
df.loc[df["day_diff"]<=30,"overall"].mean() * 28/100 + \
    df.loc[(df["day_diff"]>30) & (df["day_diff"]<=90),"overall"].mean() * 26/100 + \
    df.loc[(df["day_diff"]>90) & (df["day_diff"]<=180),"overall"].mean() * 24/100 + \
    df.loc[df["day_diff"]>180,"overall"].mean() * 22/100

def time_based_weighted_average(dataframe, w1=28,w2=26,w3=24,w4=22):
    return dataframe.loc[dataframe["day_diff"]<=30,"overall"].mean() * w1/100 + \
    dataframe.loc[(dataframe["day_diff"]>30) & (dataframe["day_diff"]<=90),"overall"].mean() * w2/100 + \
    dataframe.loc[(dataframe["day_diff"]>90) & (dataframe["day_diff"]<=180),"overall"].mean() * w3/100 + \
    dataframe.loc[df["day_diff"]>180,"overall"].mean() * w4/100

time_based_weighted_average(df)

# Adım 3: Ağırlıklandırılmış puanlamada her bir zaman diliminin ortalamasını karşılaştırıp yorumlayınız.
df.loc[df["day_diff"]<=30,"overall"].mean() * 28/100
df.loc[(df["day_diff"]>30) & (df["day_diff"]<=90),"overall"].mean() * 26/100
df.loc[(df["day_diff"]>90) & (df["day_diff"]<=180),"overall"].mean() * 24/100
df.loc[df["day_diff"]>180,"overall"].mean() * 22/100
# analiz tarihinden oylamanın yapıldığı tarih aralığı ne kadar artarsa ağırlıklandırılmış puanlamaya göre
# ürünün puanı azalıyor.

###################################################
# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirleyiniz.
###################################################


###################################################
# Adım 1. helpful_no Değişkenini Üretiniz
###################################################

# Not:
# total_vote bir yoruma verilen toplam up-down sayısıdır.
# up, helpful demektir.
# veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.
df.head(30)
df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
###################################################
# Adım 2. score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Ekleyiniz
###################################################
# def score_pos_neg_diff():
def score_up_down_diff(up,down):
    return up - down

df["score_pos_neg_diff"] = df.apply(lambda x : score_up_down_diff(x["helpful_yes"],x["helpful_no"]),axis=1)


def score_average_rating(up,down):
    if up+down == 0:
        return 0
    return up/(up+down)
df["score_average_rating"] = df.apply(lambda x : score_average_rating(x["helpful_yes"],x["helpful_no"]),axis=1)
df.head(10)

def wilson_lower_bound(up, down, confidence=0.95):
    n = up + down
    if n == 0:
        return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df["wilson_lower_bound"] = df.apply(lambda x:wilson_lower_bound(x["helpful_yes"],x["helpful_no"]),axis=1)
df.sort_values("wilson_lower_bound",ascending=False)[:20]

##################################################
# Adım 3. 20 Yorumu Belirleyiniz ve Sonuçları Yorumlayınız.
###################################################
df.sort_values("wilson_lower_bound",ascending=False)[:20]


