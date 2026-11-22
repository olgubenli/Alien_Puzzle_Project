# -*- coding: utf-8 -*-
"""İş 5 raporu: Hipotez 2 (Bölüm 3.2) analizlerinin 21 eşitlik için karşılaştırması (.md / .xlsx / .docx)."""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti")
oz, tops = pd.read_pickle(os.path.join(KOK, "cache", "ozet.pkl"))
oz["Beklenen 8. sapma ≈ 12/N (%)"] = 12 / oz["Eşleşme (±%1,5)"]
oz["Gözlenen 8. sapma (%)"] = oz["Top 8 sapma aralığı (%)"].map(lambda x: float(str(x).split("–")[-1]) if isinstance(x, str) else np.nan)
BOS = "İlk 31'deki en büyük boşluk"
RTJ = "Ek: rastgele 8'li ≥ A (|Tj−3|<0,15) olasılığı"
ref = oz.set_index("Formül").loc["Ref"]
alt = oz[oz["Formül"] != "Ref"]
ozgun = alt[alt["Not"].fillna("") == ""]  # birebir aynı sonuç veren mutlak biçimler hariç


def k(x):
    return int(np.sum(x))


R = o.Rapor("İş 5 — Makale Bölüm 3.2 (Hipotez 2) Analizlerinin 21 Eşitlik İçin Tekrarı")
R.h("Ne yapıldı")
R.p("Makalenin 3.2 bölümünde (Supplementary 3.5 ve 4.2) yazarın formülü için yapılan tüm analizler, İş 2 tablosundaki "
    "eşitliklerin hepsi için aynen tekrarlandı. E = Dünya (1,01279 AU, 15.08.1977). Q, U ve J = adı o harfle başlayan cisimler "
    "(Q: 56, U: 196, J: 1.057; Wow! günü Excel'leri). Her eşitlik için 11.601.632 kombinasyonun tamamı denendi. "
    "Sapma = |sol − sağ| / |sağ| × 100 (makaledeki tanım), eşleşme ölçütü ±%1,5. En küçük 8 sapma = Top 8.")
R.p("Tekrarlanan analizler: Tablo 1 (Top 8); Fig. S11 (Top 8 + %50 / %25 / %20 / %5 grupları); Fig. 4 / S12 (KDE yoğunluğu ve ilk 48 "
    "eşleşmede 'elbow'); Method A (P = 8/N, Z p₀ = 0,5); Method B (N/8 grup, P = 1/(N/8), Z); Fig. S13 (log-log histogram); "
    "Fig. S14 (Top 8 dikey profilleri); Fig. S15 (Grup A = Top 8 cisimleri + Dünya, Grup B = diğer eşleşmelerin cisimleri; a, e, i, Tj, AU). "
    "Yörünge elemanları yazarın genisletilmis_asteroid_db2.json dosyasından (eksikler Faz 2 SBDB önbelleğinden) alındı.")
R.p("Ek kontroller (makalede yok, karşılaştırma için): sapmaların ±%1,5 içinde düzgün dağılıp dağılmadığı (KS testi), "
    "düzgün dağılımda 8. sapmanın altında beklenen eşleşme sayısı ve P(≥ 8 | şans), elbow boşluğunun yerel ortalama aralık "
    "cinsinden büyüklüğü (Faz 2 yöntemi) ve Top 8 cisimlerinin rastgele seçilen 8'li gruplarla (2.000 tekrar) karşılaştırılması.")
R.p("Not: Bazı mutlak biçimler bu veride normal biçimle birebir aynı sonucu verir (tüm terimler pozitif olduğu için); "
    "tablolarda 'Not' sütununda belirtildi. Ref için mutlak biçim yoktur (formül zaten mutlak değerlidir ve H2'de kök çözülmez).")

R.h("1. Sağlama — yazarın formülü makaledeki sayıları veriyor mu?")
sag = pd.DataFrame([
    ["Kombinasyon", "56 × 196 × 1.057", f"{int(ref['Kombinasyon']):,}"],
    ["Eşleşme (±%1,5)", "20.590", f"{int(ref['Eşleşme (±%1,5)']):,}"],
    ["Top 8 üyeleri", "Tablo 1'deki 8 üçlü", "Aynı 8 üçlü (sıra farklı)"],
    ["Top 8 sapma aralığı", "%0,000159 – %0,000778", "%" + str(ref["Top 8 sapma aralığı (%)"])],
    ["S11 kesimleri", "0,756 / 1,126 / 1,426", ref["S11 kesimler (%)"]],
    ["S11 grup sayıları", "10.291 / 5.146 / 4.116 / 1.029", ref["S11 grup sayıları"]],
    ["Method A: P / (α/P)", "0,0003885 / 2,57", f"{ref['Method A P = 8/N']:.7f} / {ref['Method A: α(0,001)/P']:.2f}"],
    ["Method A: Z", "(Supplementary'de bozuk basılmış)", f"{ref['Method A Z (p₀=0,5)']:.2f}"],
    ["Method B: grup / Z", "2.573,5 / −50,69", f"{ref['Method B grup sayısı N/8']:.1f} / {ref['Method B Z (p₀=0,5)']:.2f}"],
    ["Grup A cisim sayısı", "24 (Supplementary), 23 (makale 3.3)", f"{int(ref['Grup A cisim (Dünya dahil)'])} (Dünya dahil) → 23 + Dünya"],
], columns=["Ölçüt", "Makale", "Yeni hesap"])
R.t("Sağlama", sag)
R.p("Top 8'in üyeleri birebir aynı; sıralama ve son basamaklardaki küçük farklar Excel'deki 6 ondalık yuvarlamadan gelir "
    "(Faz 2'de de görülmüştü). Grup A'nın 24 cismi, Top 8'deki 23 cisim + Dünya'dır; Supplementary'deki '24' ile makaledeki "
    "'23' arasındaki fark buradan gelir ve Fig. S15'teki 1,0 AU tepesi Dünya'nın kendisidir.")

R.h("Kısa sonuç")
R.p(f"Yazarın formülünde 'anomali' olarak yorumlanan bulguların hepsi alternatif eşitliklerde de çıkıyor. {len(ozgun)} farklı "
    f"alternatif eşitliğin {k(ozgun['Method A P = 8/N'] < 0.001)}'inde Method A/B 'rastgelelik reddedildi' sonucunu veriyor; "
    f"{k(ozgun['Gözlenen 8. sapma (%)'] < ref['Gözlenen 8. sapma (%)'])}'inde Top 8 yazarınkinden daha 'hassas'; "
    f"{k(ozgun[BOS] > ref[BOS])}'inde elbow boşluğu yazarınkinden büyük. "
    "Top 8'in sapması tamamen eşleşme sayısıyla belirleniyor (8. sapma ≈ 12/N) ve sapmalar her formülde ±%1,5 içinde düzgün dağılıyor. "
    "Hiçbir formülde Top 8 cisimleri 'e ≈ 0–0,02' veya belirgin Tj ≈ 3 kimliği göstermiyor.")

R.h("2. Eşleşmeler ve Top 8 (Tablo 1)")
R.t("Eşleşme ve Top 8", oz[["Formül", "Eşitlik", "Eşleşme (±%1,5)", "Top 8 sapma aralığı (%)", "Gözlenen 8. sapma (%)",
                            "Beklenen 8. sapma ≈ 12/N (%)", "Top 8 payı (%)", "Not"]])
R.p("Düzgün dağılımda N eşleşmenin 8. en küçük sapması yaklaşık 8 × 1,5 / N = 12/N'dir. Gözlenen değerler her formülde bu "
    f"beklentiyle aynı büyüklükte: yazarın formülünde 12/20.590 = %{12/20590:.6f}, gözlenen %{ref['Gözlenen 8. sapma (%)']:.6f}; "
    "F1'de 12/1.287.577 = %0,0000093, gözlenen %0,000011. Top 8'in 'hiper-hassasiyeti' eşleşme sayısının doğrudan sonucudur. "
    "F1'de en küçük sapma tam 0'dır: Excel'deki 6 ondalık yuvarlama nedeniyle bazı kombinasyonlarda iki taraf birebir eşit çıkar.")
for kod, top in tops.items():
    if top is not None and kod in ozgun["Formül"].tolist() + ["Ref"]:
        R.t(f"Top 8 — {kod}", top, sadece_excel=True)
R.p("Her formülün Top 8 tablosu Excel'de ayrı sayfadadır ('Top 8 — …').")

R.h("3. Sapma grupları (Fig. S11) ve dağılım")
R.t("S11 grupları", oz[["Formül", "S11 kesimler (%)", "S11 kesimler, düzgün dağılım beklentisi (%)", "S11 grup sayıları",
                         "Ortalama sapma (%)", "Düzgün dağılım beklentisi (%)", "KS testi p (düzgün 0–1,5)"]])
R.p("Yazarın %50 / %25 / %20 / %5 grupları, ±%1,5 içinde düzgün dağılımın yüzdelik dilimleridir (0,750 / 1,125 / 1,425). "
    "Eşleşmesi çok olan formüllerin hepsinde kesim noktaları bu değerlerle birebir örtüşüyor ve ortalama sapma ≈ %0,75. "
    "Sapmalar rastgele dağılıyor; dağılımın bir 'alt bölgesi' yok. Az eşleşmeli F2 (14) ve F7 (40) dışında KS testi düzgün dağılımı reddetmiyor.")

R.h("4. Elbow analizi (Fig. 4 / S12)")
R.t("Elbow", oz[["Formül", "8.–9. arası boşluk (ort. aralık cinsinden)", "İlk 31'deki en büyük boşluk",
                  "En büyük boşluğun yeri (… sıradan sonra)", "Ek: ≤ 8. sapma, beklenen sayı", "Ek: P(≥8 | şans)"]])
R.p(f"Yazarın formülünde ilk 31 sıradaki en büyük boşluk gerçekten 8. eşleşmeden sonra ({ref[BOS]:.1f} ortalama aralık). "
    "Ancak bu, 'elbow'un her formülde 8'de olduğu anlamına gelmiyor: alternatiflerde en büyük boşluk 1., 3., 6., 9., 10., 24. … "
    "sıralardan sonra çıkıyor ve birçoğunda büyüklüğü yazarınkine yakın veya daha büyük (F1 8,4; F8 6,5; F4 6,2; F5 6,0). "
    "Top 8 sayısı boşluk görüldükten sonra seçildiği için bu boşluk önceden belirlenmiş bir ölçüt değildir. Ayrıca şans altında 8. sapmanın "
    f"altında beklenen eşleşme sayısı yazarın formülünde {ref['Ek: ≤ 8. sapma, beklenen sayı']:.1f}, P(≥ 8) = {ref['Ek: P(≥8 | şans)']:.2f}: "
    "Top 8 beklenenden sıkı değil.")

R.h("4.1 8. eşleşmeden sonraki boşluk: yazarın formülü ve diğerleri", 3)
G89 = "8.–9. arası boşluk (ort. aralık cinsinden)"
b8 = oz[["Formül", "Eşleşme (±%1,5)", G89, BOS, "En büyük boşluğun yeri (… sıradan sonra)", "Not"]].copy()
b8["Şans olasılığı: 8 önceden seçilseydi"] = np.exp(-b8[G89])
b8["Şans olasılığı: sıra sonradan seçildi (ilk 31)"] = 1 - (1 - np.exp(-b8[G89])) ** 31
R.t("8. eşleşmeden sonraki boşluk", b8)
R.p("Boşluklar, sıfıra yakın bölgedeki ortalama aralık cinsinden verilmiştir. Rastgele (düzgün) dağılımda önceden seçilmiş tek bir "
    "sıradaki boşluk üstel dağılır: g büyüklüğünde veya daha büyük bir boşluğun olasılığı e^(−g)'dir. Sıra, boşluk görüldükten sonra ilk 31 "
    "sıra içinden seçilirse olasılık yaklaşık 1 − (1 − e^(−g))^31 olur.")
R.p(f"Yazarın formülü: 8–9 arası boşluk {ref[G89]:.1f} ortalama aralık ve ilk 31 sıradaki en büyük boşluk tam buradadır. Eğer 'Top 8' "
    f"veriye bakmadan önce belirlenmiş olsaydı bu boşluğun şansla çıkma olasılığı ≈ %{np.exp(-ref[G89])*100:.2f} olurdu. Ancak 8 sayısı "
    f"boşluk görüldükten sonra seçildiği için doğru olasılık ≈ %{(1-(1-np.exp(-ref[G89]))**31)*100:.1f}'dir (Faz 2: %2,0). Bu, yazarın formülünün "
    "3.2 bölümündeki tek dikkat çekici ölçütüdür; alışılmadık ama nadir değildir.")
R.p("Diğer formüllerde 8. eşleşmeden sonraki boşluk: F1 7,7 (yazarınkinden büyük), F7 3,1, F3 1,8, F4 1,2; geri kalanların hepsinde "
    "< 1 (yani boşluk yok; 9. eşleşme 8.'ye yapışık). Ancak F1'in boşluğu yuvarlama kaynaklıdır: Excel'deki mesafeler 6 ondalıklı olduğu "
    "için F1'in sapmaları ~%0,00001'lik basamaklarla kesikli çıkar (1 sapma = 0, 7 sapma ≈ %0,00001, sonrakiler ≈ %0,00002); 8. ile 9. "
    "arasındaki boşluk bu basamak atlamasıdır. F7'de 8. sıradan sonraki boşluk (3,1) da formülün en büyük boşluğudur, ama yalnız 40 eşleşme olduğu için zayıftır.")
R.p("Diğer formüllerde en büyük boşluk 8'den farklı sıralarda çıkar (1., 3., 6., 9., 10., 24., 25., 28., 29.) ve bazıları büyüktür "
    "(F8 6,5 – 28. sıradan sonra; F4 6,2 – 10.; F5 6,0 – 9.). Her formülde bir yerde büyük bir boşluk vardır; yeri rastgeledir. Yazarın "
    "formülünde bu boşluğun 8'de çıkması ve 8'in buna göre seçilmesi, istatistikte 'sonradan seçim' (look-elsewhere) etkisinin tipik örneğidir.")
R.p("Faz 2 ek bilgisi: yuvarlama küçük rastgele gürültüyle giderildiğinde yazarın boşluğu 7,3'ten 6,3'e iner; doğru sinyal saatinde "
    "(16 Ağustos 02:16 UT) 3,6'ya düşer ve Top 8'in üyeleri tamamen değişir. Boşluk, hesaplama saatine ve veri hassasiyetine bağlıdır.")

R.h("5. Method A ve Method B")
R.t("Method A/B", oz[["Formül", "Eşleşme (±%1,5)", "Method A P = 8/N", "Method A: α(0,001)/P", "Method A Z (p₀=0,5)",
                       "Method B grup sayısı N/8", "Method B P = 1/(N/8)", "Method B Z (p₀=0,5)", "Method A/B: H0 red (α=0,001)?"]])
R.p("Method A'nın P'si 8/N, Method B'ninki 1/(N/8)'dir; ikisi matematiksel olarak aynı sayıdır ve yalnız eşleşme sayısına bağlıdır. "
    "N > 8.000 olan her formül 'rastgelelik reddedildi' sonucunu alır; Z değerleri de yalnız N'den hesaplanır (p₀ = 0,5). Bu testler "
    "formüllerin ne bulduğunu değil, kaç eşleşme ürettiğini ölçer.")

R.h("6. Grup A – Grup B yörünge karşılaştırması (Fig. S15)")
R.t("Grup A–B", oz[["Formül", "Grup A cisim (Dünya dahil)", "Grup B cisim", "A medyan e", "B medyan e", "A ortalama e",
                     "A: e < 0,02 payı", "A medyan i (°)", "B medyan i (°)", "A: |Tj−3|<0,15 sayısı", "A medyan Tj",
                     "Ek: rastgele 8'li ≥ A (|Tj−3|<0,15) olasılığı", "Ek: rastgele 8'li ort. e ≤ A olasılığı"]])
R.p(f"Makalede Grup A için 'e ≈ 0,0–0,02, i < 20°, Tj ≈ 3,0' denmişti. Yazarın formülünde Grup A'nın medyan e değeri "
    f"{ref['A medyan e']:.3f} (Grup B {ref['B medyan e']:.3f}); e < 0,02 olan cisim payı %{ref['A: e < 0,02 payı']*100:.0f}; |Tj − 3| < 0,15 olan "
    f"cisim {int(ref['A: |Tj−3|<0,15 sayısı'])}. Rastgele seçilen 8'li grupların %{ref[RTJ]*100:.0f}'i en az bu kadar "
    "Tj ≈ 3 cismi içeriyor. Hiçbir alternatif formülde de Grup A 'e ≈ 0–0,02' göstermiyor; Tj ≈ 3 sayıları 0–4 arasında değişiyor. "
    "Ana kuşak ve Truva cisimlerinden oluşan Q, U, J havuzunda i < 20° ve Tj ≈ 3 zaten yaygındır.")

R.h("7. Karşılaştırma panelleri")
for ad, bas in (("figS11_gruplar", "Fig. S11 — Sapma grupları"), ("fig4_S12_kde", "Fig. 4 / S12 üst — Sapma yoğunluğu (KDE)"),
                ("fig4_S12_elbow_ilk48", "Fig. 4 / S12 alt — İlk 48 eşleşme (kırmızı: Top 8)"), ("figS13_loglog", "Fig. S13 — Log-log histogram"),
                ("figS14_profiller", "Fig. S14 — Top 8 dikey profilleri"), ("figS15_grupAB", "Fig. S15 — Grup A – Grup B")):
    R.h(bas, 3)
    EN = {"figS11_gruplar": "FigS11_Deviation_Groups_Pie", "fig4_S12_kde": "Fig4_S12_KDE_Elbow", "fig4_S12_elbow_ilk48": "Fig4_S12_KDE_Elbow",
          "figS13_loglog": "FigS13_LogLog_Histogram", "figS14_profiller": "FigS14_Heliocentric_Distance_Top8", "figS15_grupAB": "FigS15_GroupA_vs_GroupB_Violin"}
    R.img(os.path.join(CIKTI, "karsilastirma_EN", f"Panel_{EN[ad]}.png"), bas + " — 21 eşitlik", genislik_cm=17)

R.h("8. Yorum: farklı formüllerle ne bulduk?")
R.h("8.1 Eşleşme sayısı formüle göre çok değişiyor", 3)
R.p("Aynı Q, U, J havuzu ve aynı ±%1,5 ölçütüyle eşleşme sayısı 14 (F2) ile 1.287.577 (F1) arasında değişiyor; yazarın formülü "
    "20.590. Sayıyı belirleyen, formülün iki tarafının değer aralıklarının ne kadar örtüştüğüdür. F1'de iki taraf da ~10–15 aralığında "
    "olduğu için milyonlarca kombinasyon eşleşiyor; F2'de toplam 5'e ancak uç kombinasyonlarla ulaşılıyor.")
R.h("8.2 'Hiper-hassas Top 8' her formülde var", 3)
R.p("Makalede Top 8'in %0,000159–%0,000778 sapmaları 'hiper-hassas alt küme' olarak sunulmuştu. Alternatif formüllerde Top 8 "
    "sapmaları eşleşme sayısıyla ters orantılı: F1'de %0,00001, F4'te %0,0001–0,0002, F10'da %0,0001–0,001. Gözlenen 8. sapma her "
    "formülde şans beklentisi 12/N ile aynı büyüklükte. Yani 'hassasiyet' formülün doğruluğunu değil, kaç kombinasyon denendiğini gösterir.")
R.h("8.3 Gruplar ve KDE: sapmalar rastgele", 3)
R.p("Fig. S11'deki dört grup, düzgün dağılımın yüzdelik dilimleridir ve her formülde aynı kesim noktalarında çıkar. KDE grafiklerinde "
    "yoğunluk her formülde ≈ 1/1,5'te düzdür; sıfır ve %1,5'teki düşüş KDE yönteminin sınır etkisidir. Makaledeki 'sıfıra yakın yoğunluk "
    "düşük, mükemmel uyum nadir' yorumu bu sınır etkisinden gelir.")
R.h("8.4 Elbow ve log-log 'uçurum'", 3)
R.p("Log-log histogramda her formülde aynı görüntü çıkar: logaritmik kutular sola doğru daraldığı için sayılar azalır ve en küçük "
    "birkaç değer 'kopuk' görünür (panellerdeki kesikli çizgi düzgün dağılım beklentisidir ve histogramla örtüşür). Elbow boşluğu "
    "yazarın formülünde 8. sıradan sonra; alternatiflerde başka sıralarda ve benzer büyüklükte. Boşluğun yeri ve büyüklüğü rastgele "
    "sıra istatistiklerinin doğal değişkenliğidir; Faz 2'de yuvarlama giderilince ve sinyal saatine geçilince yazarın boşluğunun da kaybolduğu görülmüştü.")
R.h("8.5 Method A ve B", 3)
R.p("İki yöntem aynı sayıyı (8/N) iki farklı yoldan yazar ve yalnız N'ye bağlıdır. Eşleşmesi 8.000'den fazla olan her formül "
    "'H0 red' sonucunu alır (alternatiflerden F1, F4, F4-mutlak, F9, F10, F10-mutlak). Z değerleri (−11 ile −1.135 arası) da yalnız N'yi yansıtır.")
R.h("8.6 Grup A–B: 'dinamik kimlik' yok", 3)
R.p("Hiçbir formülün Top 8 cisimleri 'neredeyse dairesel yörünge (e ≈ 0–0,02)' göstermiyor; yazarın formülünde de Grup A'nın ortalama e "
    "değeri 0,17. Tj ≈ 3 cisim sayısı rastgele 8'li gruplardan farklı değil. Grup A'nın dar dağılımı yalnız küçük örnek (23 cisim) "
    "olmasından, 1,0 AU tepesi ise Dünya'nın gruba katılmasından gelir. Ukalegon ve Jean-Claude'un Top 8'de çıkması da Faz 2'deki "
    "'kavşak cisim' etkisiyle açıklanır.")
R.h("8.7 Genel sonuç", 3)
R.p("1) Yöntem doğrulandı: yazarın formülüyle 20.590 eşleşme, aynı Top 8, aynı S11 grupları, Method A/B değerleri ve Grup A'nın 24 cismi yeniden üretildi.\n"
    "2) 3.2 bölümündeki altı analizin hepsi aynı gerçeği gösterir: sapmalar ±%1,5 içinde düzgün dağılır ve Top 8 bu dağılımın en "
    "küçük 8 değeridir. Bu her formülde böyledir.\n"
    "3) Top 8'in hassasiyeti, Method A/B sonucu ve Z değerleri yalnız eşleşme sayısına bağlıdır; formülün 'doğruluğu' hakkında bilgi vermez.\n"
    "4) Top 8 cisimlerinin yörünge kimliği hiçbir formülde rastgele seçimden farklı değildir.")
R.p("Makale için anlamı: 3.2 bölümü 'Top 8, ön kayıtlı bir seçim kuralıyla (en küçük 8 sapma) belirlenmiş aday listesidir; "
    "istatistiksel bir anomali değildir' şeklinde yeniden çerçevelenebilir. Hedef listesi (Ukalegon, Jean-Claude) düşük maliyetli "
    "gözlem önerisi olarak korunabilir, ancak 'hiper-hassas', 'istatistiksel uçurum', 'fiziksel rezonans' ifadeleri kaldırılmalıdır.")

R.h("9. Formül başına dosyalar")
R.p("Her eşitliğin tam boy grafikleri (Fig. S11, Fig. 4/S12 KDE ve elbow, Fig. S13, S14, S15) ve veri dosyası (özet, Top 8, ilk 1.000 "
    "eşleşme, Grup A ve Grup B) cikti/formuller/<Formül>/ klasöründedir.")
R.kaydet("05_H2_karsilastirma", klasor=CIKTI)
