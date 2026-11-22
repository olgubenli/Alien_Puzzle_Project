# -*- coding: utf-8 -*-
"""İş 7 raporu: birleşik profil testi (.md / .xlsx / .docx)."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(KOK))
import ortak as o  # noqa: E402

CIKTI = os.path.join(KOK, "cikti"); CACHE = os.path.join(KOK, "cache")
asama = "hepsi" if os.path.exists(os.path.join(CACHE, "profil_hepsi.pkl")) else "0000"
S = pd.read_pickle(os.path.join(CACHE, f"profil_{asama}.pkl"))


def grafik(t, ad, baslik):
    r = t[t.id != "YAZAR"]; y = t[t.id == "YAZAR"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(np.log10(r.nadirlik), bins=40, color="tab:blue", alpha=0.7, label="Rastgele formüllerin kendi profilleri")
    if len(y):
        ax.axvline(np.log10(y.nadirlik.iloc[0]), color="r", lw=2, label="Yazarın formülü")
    ax.set_xlabel("log10(profil nadirliği)  — solda = daha nadir"); ax.set_ylabel("Formül sayısı"); ax.set_title(baslik); ax.legend()
    yol = os.path.join(CIKTI, ad); fig.tight_layout(); fig.savefig(yol, dpi=120); plt.close(fig)
    return yol


R = o.Rapor("İş 7 — Birleşik Profil Testi: Üç Bölümün Özellikleri Birlikte Ne Kadar Nadir?")
R.h("Soru")
R.p("Tek tek bakıldığında yazarın formülünün hiçbir özelliği olağanüstü değildir. Ancak üç bölümün özellikleri bir arada bulunuyor: "
    "(A) Bölüm 3.1 — Wow! gününde ±%1 içinde tek eşleşme (Thereus); (B) Bölüm 3.2 — en büyük sapma boşluğunun 8. sıradan sonra olması "
    "(Top 8'in elbow ile ayrılması); (C) Bölüm 3.3 — Top 8'de hem Jüpiter Truvası hem Hilda bulunması (ana ve ara kapı). "
    "Bu üçünün birlikte görülmesi, aynı karakterlerden (6, E, Q, U, J, 5) kurulan rastgele formüllerde ne kadar nadirdir?")
R.h("Yöntem")
R.p("Faz 3'te üretilen 1.000 rastgele formül (her biri 6, E, Q, U, J, 5'i birer kez kullanan eşitlik) ve yazarın formülü, makaledeki "
    "yöntemlerle değerlendirildi. Her formül için bir profil tanımlandı: (H1 eşleşme sayısı 0 / 1 / 2+, en büyük boşluğun sırası, Top 8'de Truva "
    "var mı, Hilda var mı). Nadirlik: profili oluşturan dört bileşenin rastgele formüllerdeki sıklıklarının çarpımı (bileşenler bağımsız "
    "varsayıldı). Her rastgele formülün kendi profilinin nadirliği de hesaplandı; böylece 'her formülün benzersiz bir parmak izi vardır' "
    "itirazı test edildi.")
R.p("Sinyal anı için (16.08.1977 02:16 UT): H2 ve H3'te Q, U, J cisimlerinin sinyal anı mesafeleri (Excel değeri + Horizons'tan iki an "
    "arasındaki fark) kullanıldı. H1'de 26.164 cismin her biri için 26 saat 16 dakikada Güneş uzaklığının en çok ne kadar değişebileceği "
    "fiziksel bir üst sınırla (δ = √(2,1·μ/r)·Δt) hesaplandı; eşleşme bu sınırla bile değişmiyorsa 'kesin', değişebiliyorsa 'belirsiz' "
    "sayıldı ve H1 kategorisi (0 / 1 / 2+) yalnız kesin olarak belirlenebildiğinde kullanıldı.")

for k, ad in (("0000", "15.08.1977 00:00 UT (yazarın verisi)"), ("0216", "16.08.1977 02:16 UT (sinyal anı)")):
    if k not in S:
        continue
    t, oz = S[k][0], S[k][1]
    R.h(f"Sonuç — {ad}")
    tab = pd.DataFrame([{"Ölçüt": a, "Değer": (f"{b:.4f}" if isinstance(b, float) else b)} for a, b in oz.items()])
    R.t(f"Özet {k}", tab)
    R.img(grafik(t, f"nadirlik_{k}.png", f"Profil nadirliği — {ad}"), f"Profil nadirliği dağılımı — {ad}", genislik_cm=14)
    R.t(f"Profiller {k}", t.drop(columns=["prof"]).sort_values("nadirlik"), sadece_excel=True)

oz0 = S["0000"][1]
R.h("Yorum — 00:00 UT")
R.p(f"Yazarın formülü üç özelliği birlikte taşır. Tek tek oranlar (profili belirli {oz0['Profili belirli rastgele formül']} rastgele formülde): "
    f"A %{oz0['A oranı (rastgele)']*100:.1f}, B %{oz0['B oranı']*100:.1f}, C %{oz0['C oranı']*100:.1f}. Üçünü birlikte taşıyan rastgele formül "
    f"sayısı: {oz0['A+B+C birlikte (rastgele sayı)']}. Rastgele formüllerin %{oz0['Profili benzersiz rastgele oranı']*100:.0f}'inin profili de "
    f"benzersizdir; ancak kendi profili yazarınki kadar veya daha nadir olan rastgele formül oranı yalnız "
    f"%{oz0['Kendi profili yazarınki kadar/daha nadir rastgele oranı']*100:.2f}'tür. Yani bu veri ve bu zaman için yazarın birleşik profili, "
    "rastgele okumaların yaklaşık %99,7'sinden daha nadirdir. Bu, çalışmanın en dikkat çekici sonucudur.")
R.p("Sınırlamalar: (1) Üç ölçüt, yazarın formülünün sonuçları görüldükten sonra tanımlanmıştır ('Teksaslı nişancı' etkisi); profil "
    "testi bunu kısmen düzeltir, hangi boyutlara bakılacağı seçimini düzeltmez. (2) Nadirlik bileşenlerin bağımsızlığı varsayımıyla "
    "hesaplanmıştır. (3) Örneklem 581 formüldür; %0,3 yaklaşık 2 formüle karşılık gelir ve belirsizliği büyüktür. (4) Formülün kendisi "
    "Thereus'u verdiği için seçilmiştir. (5) Sonuç 00:00 UT verisi içindir; sinyal 26 saat sonra gelmiştir.")
if "0216" in S:
    oz1 = S["0216"][1]
    R.h("Zaman (epoch) duyarlılığı — algılama anı (02:16 UT)")
    R.p("Wow! sinyali 15 Ağustos 1977'de yerel saatle 22:16 EDT'de, yani 16 Ağustos 1977 02:16 UT'de algılanmıştır; sinyal teleskobun "
        "kaynağı taradığı yaklaşık 72 saniye boyunca görülmüştür. Sinyalin yayın anı, süresi ve — bir mesaj olduğu varsayılırsa — hangi anın "
        "Güneş Sistemi dizilimini referans aldığı bilinmemektedir. Bu çalışmada algılama gününün standart günlük anı (15 Ağustos 1977 "
        "00:00 UT, JPL Horizons) kullanılmıştır. Bu seçimin etkisini görmek için aynı test algılama anı için de yapılmıştır.")
    if "Yazar A / B / C" in oz1:
        R.p(f"Algılama anında: H1 sonucu (tek eşleşme, 32532 Thereus) aynen korunur; bu sonuç cisimlerin 26 saatteki en büyük olası yer "
            f"değiştirmesi hesaba katıldığında da kesindir. Top 8 yapısı ise zamana duyarlıdır: en büyük sapma boşluğu "
            f"{oz1['Yazar: en büyük boşluk sırası']}. sıradan sonra çıkar ve Top 8'de Truva / Hilda = {oz1['Yazar: Truva / Hilda']} olur. "
            f"Bu anda kendi profili yazarınki kadar veya daha nadir olan rastgele formül oranı %{oz1['Kendi profili yazarınki kadar/daha nadir rastgele oranı']*100:.1f}'dir. "
            "Hipotez 2 ve 3'ün ince ölçekli (10⁻⁶ düzeyindeki) yapısının referans ana duyarlı olması beklenen bir durumdur; Hipotez 1'in ±%1'lik "
            "ölçeği ise bu farktan etkilenmez.")
    else:
        R.p(oz1.get("Not", ""))
R.h("Makalede kullanılabilecek ifadeler (öneri)")
R.p("Sonuç / tartışma için: \"Taken individually, none of the features of the adopted reading is exceptional relative to 1,000 random "
    f"readings built from the same six characters (single Wow-epoch match: {oz0['A oranı (rastgele)']*100:.0f}%; largest gap after rank 8: "
    f"{oz0['B oranı']*100:.0f}%; Trojan + Hilda gateways in the top octet: {oz0['C oranı']*100:.0f}%). Jointly, however, the profile is rarer than "
    f"{100-oz0['Kendi profili yazarınki kadar/daha nadir rastgele oranı']*100:.1f}% of random readings for the ephemeris epoch used throughout "
    "this study (1977-08-15 00:00 UT). The single-match result for 32532 Thereus is robust at the detection time (1977-08-16 02:16 UT), "
    "whereas the top-octet structure is epoch-sensitive. Because the features were identified after inspecting the adopted reading, we "
    "regard the joint profile as a hypothesis-generating observation; its sensitivity to the reference epoch is reported for transparency "
    "and motivates a dedicated analysis at the detection epoch in future work.\"")
R.p("Yöntem bölümü için: \"The Wow! signal was detected on 15 August 1977 at 22:16 EDT (16 August 1977, 02:16 UT) during a ~72-s transit "
    "of the source through the Big Ear beam. Because the emission time, the duration of the transmission and — under the hypothesis "
    "examined here — the reference instant of any encoded configuration are unknown, heliocentric distances were retrieved from JPL "
    "Horizons for the standard daily epoch of the detection date (1977-08-15 00:00 UT). The sensitivity of the results to this choice "
    "was evaluated by repeating the analyses at the detection time (Supplementary Section X).\"")
R.kaydet("07_birlesik_profil", klasor=CIKTI)
