# -*- coding: utf-8 -*-
"""İş 4 raporu: 22 eşitlik × 111 tarih, makale Bölüm 3.1 analizlerinin karşılaştırması (.md / .xlsx / .docx)."""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti")
ozet, saglama = pd.read_pickle(os.path.join(KOK, "cache", "ozet.pkl"))
sira = ozet["Formül"].tolist()

T_say = ozet[["Formül", "Eşitlik", "Hedef Q aralığı (AU)", "1 gün", "10 gün", "100 gün", "Toplam (111)",
              "Benzersiz cisim", "Wow! günü cisim(ler)i", "En sık 3 cisim"]]
T_say = T_say.assign(**{"Wow! günü cisim(ler)i": T_say["Wow! günü cisim(ler)i"].map(
    lambda x: x if len(x) < 160 else "; ".join(x.split("; ")[:4]) + f" … (toplam {len(x.split('; '))})")})
T_ist = ozet[["Formül", "P-değeri (n₁/N)", "P / α(0,001) oranı", "Z (10 gün)", "Z (100 gün)",
              "Fisher χ² (10 gün)", "Fisher χ² (100 gün)", "SNR (10 gün)", "SNR (100 gün)"]]
T_fis = ozet[["Formül", "Fisher sonuç (10 gün)", "Fisher sonuç (100 gün)"]]
T_zam = ozet[["Formül", "Medyan 1990 öncesi", "Medyan 1990 sonrası", "N öncesi / sonrası", "DBSCAN küme sayısı",
              "DBSCAN küme boyutları", "DBSCAN gürültü", "2σ aykırı sayısı", "Spearman ρ", "Spearman p", "Kübik R²",
              "Artık lag-1 otokorelasyon"]].copy()
T_zam.insert(3, "Medyan farkı (sonrası − öncesi)", ozet["Medyan 1990 sonrası"] - ozet["Medyan 1990 öncesi"])


# ------------------------------------------------------------------ % sapma karşılaştırması
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
M = pd.read_pickle(os.path.join(KOK, "cache", "eslesmeler.pkl"))
WOWG = pd.Timestamp("1977-08-15")
sap = []
for k in sira:
    d = M[M.formul == k]
    best = d.groupby("day").sapma.min()
    wb = best.get(WOWG, np.nan)
    sap.append({"Formül": k, "Tespit": len(d),
                "Wow! günü en iyi sapma (%)": wb,
                "Wow! günü ort. sapma (%)": d[d.window == 1].sapma.mean(),
                "10 gün ort. (%)": d[d.window == 10].sapma.mean(), "100 gün ort. (%)": d[d.window == 100].sapma.mean(),
                "111 gün ort. (%)": d.sapma.mean(), "Medyan (%)": d.sapma.median(), "En küçük (%)": d.sapma.min(),
                "< %0,1 olan pay (%)": (d.sapma < 0.1).mean() * 100,
                "Günlerin en iyi sapma medyanı (%)": best.median(),
                "Wow! günü sırası: daha iyi gün payı (%)": (best < wb).mean() * 100 if np.isfinite(wb) else np.nan,
                "Eşleşmeli gün": len(best)})
T_sap = pd.DataFrame(sap)
pk = os.path.join(KOK, "cache", "tr_paneller"); os.makedirs(pk, exist_ok=True)   # Türkçe çalışma panelleri (teslim edilmez)
fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
for ax, k in zip(axs, sira):
    d = M[M.formul == k]
    ax.hist(d.sapma, bins=20, range=(0, 1), density=True, color="tab:blue", alpha=0.6)
    ax.axhline(1.0, color="k", ls="--", lw=1, label="Düzgün dağılım")
    wb = T_sap.set_index("Formül").loc[k, "Wow! günü en iyi sapma (%)"]
    if np.isfinite(wb):
        ax.axvline(wb, color="r", lw=2, label=f"Wow! günü %{wb:.3f}")
    ax.set_title(f"{k} (n={len(d)}, ort. %{d.sapma.mean():.3f})"); ax.set_xlabel("Sapma (%)"); ax.legend(fontsize=6)
for ax in axs[len(sira):]:
    ax.axis("off")
fig.suptitle("111 gündeki tüm eşleşmelerin % sapma dağılımı (kesikli çizgi: ±%1 içinde düzgün dağılım beklentisi; kırmızı: Wow! günü)", fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(pk, "panel_sapma_dagilimi.png"), dpi=90); plt.close(fig)
fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
for ax, k in zip(axs, sira):
    best = M[M.formul == k].groupby("day").sapma.min()
    ax.scatter(best.index, best.values, s=10, c="tab:blue")
    if WOWG in best.index:
        ax.scatter([WOWG], [best[WOWG]], s=80, c="r", marker="*", zorder=5, label="Wow! günü")
        ax.legend(fontsize=6)
    ax.set_ylim(0, 1); ax.set_title(k); ax.set_ylabel("Günün en iyi sapması (%)")
for ax in axs[len(sira):]:
    ax.axis("off")
fig.suptitle("Her günün en iyi (en küçük) % sapması — Wow! günü kırmızı yıldız", fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(pk, "panel_gunluk_en_iyi_sapma.png"), dpi=90); plt.close(fig)

ref = ozet.set_index("Formül").loc["Ref-makale"]
diger = ozet[~ozet["Formül"].str.startswith("Ref")]


def kac(kosul):
    return int(kosul.sum())


R = o.Rapor("İş 4 — Makale Bölüm 3.1 Analizlerinin 22 Eşitlik İçin Tekrarı (111 Tarih)")
R.h("Ne yapıldı")
R.p("Makalenin 3.1 (Hypothesis 1 Results) bölümünde yazarın formülü için yapılan tüm hesaplar ve grafikler, "
    "İş 2'deki eşitliklerin hepsi için aynen tekrarlandı. Tarihler: Wow! günü (1977-08-15), 10 kontrol tarihi "
    "(uzaylı bulmaca/N.farklı tarih …) ve 100 kontrol tarihi (100 farklı tarih/…/AstroData*) — toplam 111. "
    "Her tarihte E, U, J o günün gerçek mesafesi; Q bilinmeyen; denklem çözülüp ±%1 içindeki cisimler eşleşme sayıldı. "
    "Ref-makale yalnız pozitif kökü (makaledeki gibi), diğer tüm satırlar köklerin mutlak değerlerini kullanır; "
    "bir eşitliğin birden çok kökü varsa eşleşmeler birleştirildi (orijinal sondogru.py mantığı).")
R.p("Parametreler yazarın orijinal kodundan (yenigrafik49.py) ve Supplementary Denklem 1–8'den alındı: P = n₁/N "
    "(N = 26.576); Z = (p̂ − 0,5)/√(0,25/n); Fisher λ = Wow! günü eşleşme sayısı, p_i = P(X ≥ k_i | λ), df = 2k; "
    "SNR = Wow! günü cisim(ler)inin tekrarları / diğerleri; KDE 1990 öncesi/sonrası; DBSCAN (StandardScaler, eps 0,3, "
    "min_samples 5); 30 noktalık merkezli hareketli ortalama, 2σ aykırılar, Spearman ρ; 3. derece polinom R².")
R.p("Veri notu: 100 tarihlik Excel'lerin bazı satırlarında mesafe boş (9 tarihte Dünya, Jüpiter veya Uranüs dahil). "
    "Makaledeki analiz bigdata.db'den yapıldığı için boş değerler bigdata.db'den tamamlandı; iki kaynakta da bulunan "
    "değerler birebir aynıdır (fark 0). Tarihler dosyalardaki gibidir (1984-03-01 ve 2012-07-08; Supplementary "
    "listesinde 1984-03-11 ve 2012-07-18 yazıyor). F3 ve F3-mutlak'ta (~64.000 tespit) DBSCAN, bellek nedeniyle "
    "15.000 noktalık sabit tohumlu örnekle yapıldı.")

R.h("1. Sağlama — yazarın formülü (Ref-makale) makaledeki sayıları veriyor mu?")
R.t("Sağlama", saglama)
R.p("Farkların nedeni: (1) Makaledeki 'C/2ZREİ O1 (PANSTARRS)' bozulmuş bir isimdir; mesafe (12,94947 AU) ve tarih "
    "aynı olan C/2024 O1 (PANSTARRS) ile aynı cisimdir. (2) 2012-07-08 tarihinde Excel'de Jüpiter mesafesi boş; makaledeki "
    "analizde bu gün için eşleşme yok. Değer bigdata.db'den tamamlanınca o gün 2 kuyruklu yıldız eşleşiyor "
    "(C/2007 W1 Boattini, C/2008 C1 Chen-Gao). 100 günlük toplam bu yüzden 165 yerine 167, Fisher χ² 270,06 yerine 272,72. "
    "Bu iki istisna dışında makaledeki 189 tespitin tamamı birebir yeniden üretildi; yöntem doğrulandı.")
R.p("Ek tespit: Makalede 100 günlük Fisher testi için α = 0,001, df = 200 kritik değeri 278,5 yazılmış; doğru değer "
    "267,54'tür (10 gün için 45,31 doğru). Doğru kritik değerle yazarın formülü 100 günde α = 0,001'de de 'H0 red' çıkar. "
    "Bu tabloda doğru kritik değerler kullanıldı.")

R.h("Kısa sonuç")
R.p(f"Yazarın formülünde 'özel' yorumlanan sonuçların hepsi diğer formüllerde de çıkıyor: "
    f"Fisher testinde 'H0 red' (α=0,01, 100 gün) {kac(diger['Fisher sonuç (100 gün)'].str.contains('α=0.01: H0 red', na=False))}/{len(diger)} formülde; "
    f"Wow! gününde tek eşleşme {kac(diger['1 gün'] == 1)}/{len(diger)} formülde; Z skorları hepsinde ≈ −515 ve ≈ −1630; "
    f"SNR ≈ 0 hepsinde; kübik R² yazarınkinden (0,746) yüksek olan {kac(diger['Kübik R²'] > ref['Kübik R²'])} formül; "
    f"Spearman ρ yazarınkinden (0,48) yüksek olan {kac(diger['Spearman ρ'] > ref['Spearman ρ'])} formül; ≥2 DBSCAN kümesi "
    f"{kac(diger['DBSCAN küme sayısı'] >= 2)} formülde. Bu yapılar formüle değil, her formülün içindeki gezegen mesafelerinin "
    "zamanla değişmesine (Q(t)) bağlıdır.")

R.h("2. Eşleşme sayıları (makale: 1 / 23 / 165, 149 benzersiz cisim)")
R.t("Eşleşme sayıları", T_say)
R.p(f"Wow! gününde tam 1 eşleşme veren eşitlik sayısı: {kac(diger['1 gün'] == 1)} / {len(diger)} "
    f"(yazarın formülü dışında). Wow! gününde hiç eşleşme vermeyen: {kac(diger['1 gün'] == 0)}.")

R.h("3. İstatistik testleri (Supplementary Denklem 1–8)")
R.t("İstatistik testleri", T_ist)
R.t("Fisher kararları", T_fis)
R.p(f"Makaledeki ölçütlerle 'rastgelelik reddedildi' sonucunu veren eşitlik sayıları (yazarın formülü dışında, {len(diger)} eşitlik): "
    f"P-değeri < 0,001: {kac(diger['P-değeri (n₁/N)'].between(1e-12, 0.001))}; "
    f"|Z(10 gün)| > 3,29: {kac(diger['Z (10 gün)'].abs() > 3.29)}; "
    f"|Z(100 gün)| > 3,29: {kac(diger['Z (100 gün)'].abs() > 3.29)}; "
    f"Fisher (100 gün) α = 0,01'de H0 red: {kac(diger['Fisher sonuç (100 gün)'].str.contains('α=0.01: H0 red', na=False))}.")

R.h("4. Zaman yapısı: KDE, DBSCAN, hareketli ortalama, regresyon")
R.t("Zaman yapısı", T_zam)
R.p(f"Yazarın formülü: medyan farkı {ref['Medyan 1990 sonrası'] - ref['Medyan 1990 öncesi']:+.2f} AU, "
    f"Spearman ρ = {ref['Spearman ρ']:.2f}, R² = {ref['Kübik R²']:.3f}, DBSCAN {ref['DBSCAN küme sayısı']} küme. "
    f"Diğer eşitliklerde: |ρ| > 0,3 olan {kac(diger['Spearman ρ'].abs() > 0.3)}; R² > 0,5 olan {kac(diger['Kübik R²'] > 0.5)}; "
    f"≥ 2 DBSCAN kümesi olan {kac(diger['DBSCAN küme sayısı'] >= 2)}.")
R.p("Gri çizgiler (panellerde): her tarihte formülün hedef mesafesi Q(t). Eşleşmeler bu çizgiyi izler; "
    "zaman eğrileri, kümeler ve trendler formülün içindeki gezegen mesafelerinden (Uranüs, Jüpiter, Dünya) gelir.")

R.h("5. % sapma karşılaştırması")
R.p("Sapma = |cisim mesafesi − hedef Q| / Q × 100 (makaledeki tanım; eşleşme ölçütü ±%1). Tabloda her formül için "
    "Wow! günündeki sapma, 10 / 100 / 111 günlük ortalamalar, her günün en iyi (en küçük) sapması ve Wow! gününün "
    "bu günler arasındaki yeri verilmiştir. 'Daha iyi gün payı': eşleşme olan günlerin yüzde kaçında en iyi sapma "
    "Wow! gününden küçük.")
R.t("Sapma karşılaştırması", T_sap)
R.img(os.path.join(CIKTI, "karsilastirma_EN", "Panel_Deviation_Distribution.png"), "Tüm eşleşmelerin % sapma dağılımı — 22 eşitlik", genislik_cm=17)
R.img(os.path.join(CIKTI, "karsilastirma_EN", "Panel_Daily_Best_Deviation.png"), "Her günün en iyi % sapması; Wow! günü kırmızı yıldız", genislik_cm=17)
rs = T_sap.set_index("Formül")
alt = T_sap[~T_sap["Formül"].str.startswith("Ref")]
R.p(f"1) Sapmalar her formülde ±%1 içinde düzgün dağılıyor: 111 günlük ortalama sapma {T_sap['111 gün ort. (%)'].min():.2f}–"
    f"{T_sap['111 gün ort. (%)'].max():.2f}% arasında (düzgün dağılımda beklenen %0,50), eşleşmelerin %{T_sap['< %0,1 olan pay (%)'].min():.0f}–"
    f"{T_sap['< %0,1 olan pay (%)'].max():.0f}'i %0,1'in altında (beklenen %10). Yani bir eşleşmenin sapmasının küçük ya da büyük olması "
    "formül hakkında bilgi taşımıyor; pencereye rastgele düşen bir cismin beklenen davranışı.")
R.p(f"2) Yazarın formülünde Wow! günü eşleşmesi (Thereus) %{rs.loc['Ref-makale','Wow! günü en iyi sapma (%)']:.3f} sapmayla pencerenin "
    f"kenarına yakın. Eşleşme olan günlerin %{rs.loc['Ref-makale','Wow! günü sırası: daha iyi gün payı (%)']:.0f}'inde en iyi sapma "
    f"bundan küçük (günlerin en iyi sapma medyanı %{rs.loc['Ref-makale','Günlerin en iyi sapma medyanı (%)']:.2f}). Wow! günü sapma "
    "açısından sıradan, hatta ortalamanın altında bir gün.")
R.p(f"3) Wow! gününde tek eşleşme veren diğer formüllerin sapmaları: F7 %{rs.loc['F7','Wow! günü en iyi sapma (%)']:.3f}, "
    f"F10 %{rs.loc['F10','Wow! günü en iyi sapma (%)']:.3f}, F6 %{rs.loc['F6','Wow! günü en iyi sapma (%)']:.3f}, "
    f"F8 %{rs.loc['F8','Wow! günü en iyi sapma (%)']:.3f}, F5 %{rs.loc['F5','Wow! günü en iyi sapma (%)']:.3f}. "
    f"Bunların {int((alt['Wow! günü en iyi sapma (%)'] < rs.loc['Ref-makale','Wow! günü en iyi sapma (%)']).sum())}/{len(alt)}'i "
    "Wow! gününde yazarın formülünden daha küçük sapma veriyor. Bu değerler İş 2'deki tek gün sonuçlarıyla birebir aynı.")

R.h("5.1 Sapmalar her formülde rastgele dağılıyor", 3)
R.p("Bir pencereye cisimler rastgele düşerse sapma 0 ile %1 arasında düzgün dağılır: ortalama %0,50, eşleşmelerin %10'u %0,1'in altında. "
    f"22 formülde ortalama sapma %{T_sap['111 gün ort. (%)'].min():.2f} – %{T_sap['111 gün ort. (%)'].max():.2f}, %0,1 altındaki pay "
    f"%{T_sap['< %0,1 olan pay (%)'].min():.0f} – %{T_sap['< %0,1 olan pay (%)'].max():.0f}. Yazarın formülü dahil hiçbir formülün "
    "eşleşmeleri hedefe beklenenden daha yakın değil; sapmanın küçük ya da büyük olması formül hakkında bilgi taşımıyor.")
R.h("5.2 Wow! günü sapma açısından sıradan, hatta kötü bir gün", 3)
tek = T_sap[T_sap["Formül"].isin(["Ref-makale", "F7", "F10-mutlak", "F6", "F10", "F8", "F5"])][
    ["Formül", "Wow! günü en iyi sapma (%)", "Wow! günü sırası: daha iyi gün payı (%)", "Eşleşmeli gün"]]
tek = tek.assign(**{"Wow! günü cismi": tek["Formül"].map({"Ref-makale": "32532 Thereus", "F7": "C/1877 G2 (Swift)",
    "F10-mutlak": "C/1968 N1 (Honda), C/1973 A1 (Heck-Sause)", "F6": "Pioneer 10", "F10": "C/1973 A1 (Heck-Sause)",
    "F8": "C/1863 T1 (Baeker)", "F5": "C/1968 N1 (Honda)"})}).sort_values("Wow! günü en iyi sapma (%)", ascending=False)
R.t("Wow! günü sapması (tek veya az eşleşmeli formüller)", tek)
R.p(f"Yazarın formülünde eşleşme olan {int(rs.loc['Ref-makale','Eşleşmeli gün'])} günün "
    f"%{rs.loc['Ref-makale','Wow! günü sırası: daha iyi gün payı (%)']:.0f}'inde günün en iyi sapması Thereus'unkinden (%0,829) küçük; "
    f"günlerin en iyi sapma medyanı %{rs.loc['Ref-makale','Günlerin en iyi sapma medyanı (%)']:.2f}. Panelde Wow! günü (kırmızı yıldız) "
    "pencerenin üst kenarına yakın duruyor. Wow! gününde tek eşleşme veren 5 alternatif formülün (F5, F6, F7, F8, F10) hepsi "
    "yazarın formülünden daha küçük sapma veriyor. Bu değerler İş 2'deki tek gün sonuçlarıyla birebir aynı; iki hesap birbirini doğruluyor.")
R.h("5.3 En küçük sapma, eşleşme sayısına bağlı", 3)
R.p("F3'te her gün yaklaşık 660 eşleşme olduğu için günün en iyi sapması her gün %0,001 civarında (panelde sıfır çizgisine yapışık). "
    "F7, F8 ve Ref-makale gibi günde 1–3 eşleşme veren formüllerde en iyi sapma 0 ile %1 arasında rastgele dağılıyor. Pencereye ne kadar "
    "çok cisim düşerse en küçük sapma o kadar küçülür. Bu, makalenin 3.2 bölümü (Hipotez 2) için de önemlidir: oradaki 'hiper-hassas "
    "Top 8' (%0,000159 – %0,000778) 11,6 milyon kombinasyon içinden seçilmiştir ve bu kadar kombinasyonda bu düzeyde küçük sapmalar "
    "zaten beklenir (Faz 2: beklenen 10,8, gözlenen 8).")
R.h("5.4 Pencereler arasında fark yok", 3)
R.p(f"10 günlük ortalamalar %{T_sap['10 gün ort. (%)'].min():.2f} – %{T_sap['10 gün ort. (%)'].max():.2f}, 100 günlük ortalamalar "
    f"%{T_sap['100 gün ort. (%)'].min():.2f} – %{T_sap['100 gün ort. (%)'].max():.2f}; pencereden pencereye sistematik bir fark yok. "
    "Wow! gününün ortalaması çoğu formülde tek bir eşleşmeye dayandığı için rastgele bir değerdir.")
R.h("5.5 Özet", 3)
R.p("Sapmalar formüller arasında ayrım yapmıyor ve Wow! gününü özel kılmıyor. Yazarın formülünün Wow! günü sapması (%0,83), tek "
    "eşleşme veren alternatif formüllerin hepsinden kötü ve günler arasında da alt sıralarda. Makalede Thereus'un sapması bir "
    "kesinlik göstergesi gibi sunulmamalı; yalnız '±%1 penceresine düşen tek cisim' olarak yazılabilir.")

R.h("6. Karşılaştırma panelleri (22 eşitlik yan yana)")
GR = [("fig1_violin", "Fig. 1 — Pencerelere göre AU dağılımı"), ("figS2_strip", "Fig. S2 — Pencerelere göre AU (jitter)"),
      ("figS3_varlik_10g", "Fig. S3 — 10 gün (+1977) varlık matrisi"), ("figS4_matris_111g", "Fig. S4 — 111 gün varlık matrisi"),
      ("figS5_pasta", "Fig. S5 — Cisim tekrar payları"), ("fig2_kde_1990", "Fig. 2 — 1990 öncesi/sonrası KDE"),
      ("fig3_dbscan", "Fig. 3 — DBSCAN"), ("figS8_hareketli_ort", "Fig. S8 — Hareketli ortalama ve aykırılar"),
      ("figS9_regresyon", "Fig. S9 — Kübik regresyon"), ("figS10_artiklar", "Fig. S10 — Regresyon artıkları")]
EN = {"fig1_violin": "FigS1_Fig1_AU_Distribution_by_Window", "figS2_strip": "FigS2_AU_Scatter_by_Window", "figS3_varlik_10g": "FigS3_Presence_Matrix_10d_1d_Inset",
      "figS4_matris_111g": "FigS4_Presence_Matrix_Master_111d", "figS5_pasta": "FigS5_Repetition_Frequency_Pies", "fig2_kde_1990": "FigS6_Fig2_AU_Density_by_Epoch_1990",
      "fig3_dbscan": "FigS7_Fig3_DBSCAN_Clusters", "figS8_hareketli_ort": "FigS8_AU_vs_Time_Rolling_Mean_Outliers", "figS9_regresyon": "FigS9_Polynomial_Regression_Deg3",
      "figS10_artiklar": "FigS10_Regression_Residuals"}   # İngilizce paneller (panel_EN.py)
for dosya, bas in GR:
    R.h(bas, 3)
    R.img(os.path.join(CIKTI, "karsilastirma_EN", f"Panel_{EN[dosya]}.png"), bas + " — 22 eşitlik", genislik_cm=17)

R.h("7. Yorum: farklı formüllerle ne bulduk?")
R.p("Bu bölüm makalenin 3.1 bölümündeki yorumların sırasını izler ve her birini 20 alternatif eşitliğin sonuçlarıyla karşılaştırır.")
R.h("7.1 Eşleşme sayıları ve Wow! gününün tekilliği", 3)
R.p("Makalede Wow! gününde yalnız Thereus'un bulunması, formülün o güne özgü tek bir hedef gösterdiği şeklinde yorumlanmıştı. "
    "Alternatif 20 eşitliğin 8'i Wow! gününde aynı şekilde tek eşleşme veriyor: F5 → C/1968 N1 (Honda), F6 → Pioneer 10, "
    "F7 → C/1877 G2 (Swift), F8 → C/1863 T1 (Baeker), F10 → C/1973 A1 (Heck-Sause) ve bunların mutlak biçimlerinden bazıları. "
    "Tek eşleşme çıkıp çıkmaması hedef mesafenin katalogda seyrek bir bölgeye düşüp düşmediğine bağlıdır: F3'ün hedefi 3,1 AU "
    "(asteroit kuşağı) olduğu için Wow! gününde 661 eşleşme var; F7 ve F8'in hedefi 125–150 AU, burada yalnız birkaç uzun dönemli "
    "kuyruklu yıldız var; F2'nin hedefi 5,3–7,5 AU ve eşleşmelerin çoğu Jüpiter Truvaları (Agenor, Deikoon, Phaenops…). "
    "Her formül, hedefinin bulunduğu bölgedeki cisim ailesini bulur.")
R.h("7.2 AU dağılımı ve iki popülasyon (Fig. 1, Fig. S2)", 3)
R.p("Makalede 10 ve 100 günlük pencerelerde görülen iki AU rejimi 'iki ayrı popülasyon' olarak yorumlanmıştı. Alternatif "
    "formüllerde de pencereler arasında benzer kaymalar ve çok tepeli dağılımlar görülüyor. Panellerdeki gri çizgiler (hedef "
    "mesafe Q(t)) bunun nedenini gösterir: her tarihte formül farklı bir mesafeyi hedefler ve eşleşmeler bu hedefin etrafında "
    "toplanır. Kontrol tarihleri farklı yıllara dağıldığı için her formülde 'rejimler' oluşur. Mutlak biçimlerde iki kök iki ayrı "
    "bant üretir (Ref-mutlak: ~10 ve ~12 AU; F1-mutlak: ~22 ve ~36 AU); bu bantlar denklemin cebirsel yapısından gelir.")
R.h("7.3 Tekrar eden cisimler (Fig. S5)", 3)
R.p("Makalede Chariklo'nun 13 tekrarla öne çıkması, formülün kaotik yörünge rejimlerine duyarlılığı olarak yorumlanmıştı. Her "
    "formülün kendi 'Chariklo'su' var: F1'de Petraios (18), F3'te Mazzini (45), F4'te Chiminigagua (20) ve cüce gezegen Gonggong (11), "
    "F5'te Aphidas (14), F9'da Arawn (17), F10'da Elatus (8). Yörüngesi formülün hedef aralığında uzun süre kalan cisimler sık "
    "tekrar eder. Thereus da alternatif formüllerde tekrar ediyor: ~11 AU civarında kök üreten Ref-mutlak ve F6-mutlak'ta 7'şer kez. "
    "Yazarın formülünde Thereus'un başka günlerde çıkmaması özel değildir; hedef ~12,3 AU'dan uzaklaşınca Thereus pencere dışında kalır.")
R.h("7.4 İstatistik testleri", 3)
R.p("P-değeri (n₁/N): Wow! gününde 1 eşleşme veren her formül aynı P = 0,0000376 değerini alır; bu sayı formülün ne bulduğunu "
    "değil yalnız eşleşmenin tek olduğunu söyler. Z-testleri: tüm formüllerde Z ≈ −515 (10 gün) ve ≈ −1630 (100 gün), 64 bin "
    "eşleşmeli F3'te bile −493 / −1559; bu değerler p₀ = 0,5 varsayımından ve havuz büyüklüğünden gelir, formülleri ayırt etmez. "
    "Fisher testi: 100 günde α = 0,01 düzeyinde 'H0 red' 20 formülün 13'ünde çıkıyor; bu test kontrol günlerinin Wow! gününden daha "
    "fazla eşleşme verip vermediğini ölçer, yani 'red', Wow! gününün ortalama bir günden daha az eşleşme verdiğini gösterir. "
    "SNR: neredeyse tüm formüllerde 0–0,09; makalede 'formül belirli bir uzay bölgesini hedefliyor' kanıtı sayılan sonuç 22 formülün hepsinde vardır.")
R.h("7.5 1990 öncesi / sonrası yoğunluk (Fig. 2)", 3)
R.p("Makalede medyanın 12,22'den 13,22 AU'ya çıkması 'JFC rejiminden Centaur kuşağına fiziksel geçiş' olarak yorumlanmıştı. "
    "Alternatif formüllerde de 1990'da benzer kaymalar var: F1 21,8 → 23,2 AU; F2 5,6 → 7,1 AU; F4 73,5 → 81,5 AU; F6 14,0 → 15,1 AU. "
    "Hedefleri çok farklı bölgelerde olan formüllerin hepsi 1990 sonrası daha uzağa kayıyor. Ortak neden, hepsinin içinde bulunan "
    "Uranüs'ün 1966'da Güneş'e en yakın, 2009'da en uzak noktasında olmasıdır. 'Göç' fiziksel bir olay değil, Uranüs'ün yörüngesinin formüle yansımasıdır.")
R.h("7.6 DBSCAN kümeleri (Fig. 3)", 3)
R.p("Makalede iki küme ve 13 gürültü noktası 'fiziksel bir rezonans yasasına güçlü uyum' olarak yorumlanmıştı. Alternatif "
    "formüllerin 17'sinde en az iki küme var (F10'da 13, F7'de 7). DBSCAN her formülde hedef eğrisini zaman dilimlerine ayırır; "
    "küme sayısı eğrinin şekline ve veri yoğunluğuna bağlıdır.")
R.h("7.7 Hareketli ortalama ve Spearman (Fig. S8)", 3)
R.p("Makalede ρ = 0,48 'zamana bağlı, rastgele olmayan artış' olarak yorumlanmıştı. Alternatif formüllerin 9'unda ρ daha yüksek "
    "(F3 0,81; F2 0,73; F2-mutlak 0,61); F9'da ρ = −0,52, yani eğilim ters yönde. Trendin yönü ve gücü formüldeki gezegen "
    "terimlerinin işaretine göre belirlenir.")
R.h("7.8 Kübik regresyon ve artıklar (Fig. S9–S10)", 3)
R.p("Makalede R² = 0,746 'öngörülebilir, deterministik rezonans' ve artıklardaki 15–20 yıllık salınım 'ikincil periyodik modülasyon' "
    "olarak yorumlanmıştı. 5 formülde R² daha yüksek (F2 0,85; F6 0,80; F4 0,80; F1 0,79; F3 0,75). Artıklardaki sistematik yapı "
    "neredeyse tüm formüllerde var (lag-1 otokorelasyon yazarınkinde 0,82, alternatiflerde çoğunlukla 0,7–0,97). F10 ve F9'da "
    "salınım çok nettir ve dönemi Jüpiter'in 11,86 yıllık yörüngesidir; yazarın formülündeki 'ikincil modülasyon' da budur. "
    "Deterministik olan bir rezonans değil, gezegenlerin yörüngeleridir.")
R.h("7.9 % sapmalar", 3)
R.p("Tüm formüllerde eşleşmelerin sapmaları ±%1 penceresinde düzgün dağılıyor (ortalama ≈ %0,50, %0,1 altı ≈ %10). Küçük sapma "
    "bir formülün 'doğruluğunu' göstermez. Yazarın formülünde Wow! günü sapması (%0,829) eşleşme olan günlerin büyük çoğunluğundan "
    "kötüdür; Wow! gününde tek eşleşme veren F7 (%0,187), F10 (%0,461), F6 (%0,425), F8 (%0,557) ve F5 (%0,566) daha küçük sapma verir.")
R.h("7.10 Genel sonuç", 3)
R.p("1) Yöntem doğrulandı: yazarın formülüyle makaledeki 189 tespit birebir yeniden üretildi (tek farklar 2012-07-08'deki eksik "
    "Jüpiter verisi ve bozuk bir cisim adı).\n"
    "2) Makaledeki bulguların hiçbiri formüle özgü değil: Wow! gününde tek eşleşme, Fisher'da 'red', Z ≈ −515, SNR ≈ 0, 1990 kayması, "
    "DBSCAN kümeleri, S-eğrisi, yüksek R² ve artık salınımı alternatif formüllerin önemli bir kısmında da çıkıyor.\n"
    "3) Bu yapıların kaynağı, formülün çözümü olan hedef mesafe Q(t)'dir. Q(t) her tarihte Dünya, Uranüs ve Jüpiter'in o günkü "
    "mesafelerinden hesaplanır; Uranüs'ün yörüngesi uzun dönemli trendi (S-eğrisi, 1990 kayması), Jüpiter'in yörüngesi kısa dönemli "
    "salınımı üretir. Hangi cisimlerin bulunacağını ise katalogun o mesafedeki yoğunluğu belirler.\n"
    "4) Yazarın formülünü farklı kılan tek şey hedef bölgesidir (~12,3 AU, katalogda seyrek Centaur bölgesi); bu Wow! gününde tek bir "
    "Centaur'un (Thereus) bulunmasını sağlar. Benzer seyrek bölgeleri hedefleyen F5, F6, F7, F8 ve F10 da tek cisim bulur.")
R.p("Makale için anlamı: 3.1 bölümü 'gözlenen zaman yapısı Q(t)'nin analitik sonucudur; alternatif okuma kuralları da benzer yapılar "
    "üretir' şeklinde yeniden çerçevelenebilir. Bu, Hakem 1'in eleştirisine en güçlü cevaptır: varsayım bırakılmış, test edilmiş ve "
    "sonuç dürüstçe raporlanmıştır.")

R.h("8. Formül başına dosyalar")
R.p("Her eşitliğin tam boy grafikleri (10 adet) ve veri dosyası şu klasörde: cikti/formuller/<Formül>/ "
    "(…_veri.xlsx: özet, tüm tespitler, tekrar sayıları, Fisher tabloları, DBSCAN kümeleri, hedef Q(t)).")
R.t("Dosya listesi", pd.DataFrame({"Formül": sira, "Klasör": [f"cikti/formuller/{k}/" for k in sira]}))
R.kaydet("04_111gun_karsilastirma", klasor=CIKTI)
