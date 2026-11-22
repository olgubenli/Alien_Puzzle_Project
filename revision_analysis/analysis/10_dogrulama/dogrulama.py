# -*- coding: utf-8 -*-
"""Makaledeki (BENLI_2026_01_06) bütün sayısal ifadelerin yazarın kendi kaynaklarından yeniden hesaplanması.

Kaynaklar (salt okunur):
  H1: Alien_Puzzle_Project/src/yenigrafik49.py içindeki 189 tespit (makalenin kullandığı veri)
      + bağımsız kontrol: Wow!/10/100 gün Excel'lerinden yeniden tarama (04_111gun önbelleği)
  H2: Alien_Puzzle_Project/data/eslesme_sonuclari 20590.txt (yazarın sıralı eşleşme listesi)
      + bağımsız kontrol: Excel'lerden yeniden tarama (05_h2 önbelleği)
  H3: Alien_Puzzle_Project/data/uzayli_bulmacasi_matrixson.db (yazarın maliyet matrisi, k=7)
      + yazarın yörünge elemanları, 06_h3 önbelleği (stres testi, Horizons 15.08.1977 konumları)
Çıktı: cikti/dogrulama_sonuc.json + ekrana özet."""
import json, os, re, sqlite3, sys
from io import StringIO
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

KOK = os.path.dirname(os.path.abspath(__file__))
ANALIZ = os.path.dirname(KOK)
MASA = os.path.dirname(os.path.dirname(ANALIZ))
APP = os.path.join(MASA, "Alien_Puzzle_Project")
CIKTI = os.path.join(KOK, "cikti"); os.makedirs(CIKTI, exist_ok=True)
R = {}


def kaydet(anahtar, deger):
    R[anahtar] = deger
    print(f"{anahtar}: {deger}")


# =============================================================== H1
src = open(os.path.join(APP, "src", "yenigrafik49.py"), encoding="utf-8").read()
parca = []
for ad in ("csv_1d_matches", "csv_10d_matches", "csv_100d_matches"):
    txt = re.search(ad + r' = """(.*?)"""', src, re.S).group(1)
    for a, b in (("2İNDİ-12-13", "2008-12-13"), ("2Oc06-09-24", "2006-09-24"), ("2GEÇ-12-13", "2008-12-13"), ("2GEÇ-09-24", "2006-09-24")):
        txt = txt.replace(a, b)
    parca.append(pd.read_csv(StringIO(txt)))
d = pd.concat(parca).dropna(subset=["window"]).copy()
d["day"] = pd.to_datetime(d["day"], errors="coerce")
d["window"] = d["window"].astype(str).str.extract(r"(\d+)")[0].astype(int)
d = d.sort_values("day", kind="mergesort").reset_index(drop=True)
print("Yazar verisi sütunlar:", d.columns.tolist())

N = 26576
n1, n10, n100 = (int((d.window == w).sum()) for w in (1, 10, 100))
kaydet("H1.sayilar_1_10_100", [n1, n10, n100])
kaydet("H1.toplam_benzersiz", [len(d), int(d.object_id.nunique())])
kaydet("H1.wow_cismi", d[d.window == 1].object_id.tolist())
d10 = d[d.window == 10]; d100 = d[d.window == 100]
kaydet("H1.10gun_AU_aralik", [round(d10.au.min(), 3), round(d10.au.max(), 3)])
kaydet("H1.10gun_2000_sonrasi_oran", round(float((d10.day >= "2000-01-01").mean()), 3))
kaydet("H1.10gun_tekrar_eden", d10.object_id.value_counts()[lambda s: s > 1].to_dict())
# 100 gün: AU rejimleri (en büyük boşluk)
a = np.sort(d100.au.values); g = np.diff(a); k = int(g.argmax())
kaydet("H1.100gun_AU_aralik", [round(a.min(), 3), round(a.max(), 3)])
kaydet("H1.100gun_en_buyuk_bosluk", [round(a[k], 3), round(a[k + 1], 3)])
bos = sorted(((g[i], a[i], a[i + 1]) for i in range(len(g))), reverse=True)[:3]
kaydet("H1.100gun_ilk3_bosluk", [[round(x, 3) for x in t] for t in bos])
# 100 gün tekrar dağılımı
rep100 = d100.object_id.value_counts()
kaydet("H1.100gun_benzersiz", int(len(rep100)))
kaydet("H1.100gun_tek_cift_yuzde", [round(100 * (rep100 == 1).mean(), 1), round(100 * (rep100 == 2).mean(), 1)])
kaydet("H1.100gun_tek_cift_yuzde_tespit_bazli", [round(100 * rep100[rep100 == 1].sum() / rep100.sum(), 1), round(100 * rep100[rep100 == 2].sum() / rep100.sum(), 1)])
kaydet("H1.100gun_ilk3", rep100.head(4).to_dict())
# 111 gün
rep = d.object_id.value_counts()
kaydet("H1.111_ilk5", rep.head(5).to_dict())
kaydet("H1.111_SN_orani_yuzde", {k_: round(100 * v / (len(d) - v), 2) for k_, v in rep.head(5).items()})
kaydet("H1.111_pay_yuzde(v/189)", {k_: round(100 * v / len(d), 2) for k_, v in rep.head(3).items()})
kaydet("H1.S7_tekrar_dagilimi", rep.value_counts().sort_index(ascending=False).to_dict())
pre88, post88 = d[d.day < "1988-01-01"].au, d[d.day >= "1988-01-01"].au
kaydet("H1.1988_once_sonra_ort_medyan", [round(pre88.mean(), 2), round(pre88.median(), 2), round(post88.mean(), 2), round(post88.median(), 2)])
# P, Z
kaydet("H1.P", n1 / N); kaydet("H1.alfa_bolu_P", round(0.001 / (n1 / N), 2))
kaydet("H1.P_Excel_havuzu_26164", [1 / 26164, round(0.001 * 26164, 2)])
for w, nn in ((10, n10), (100, n100)):
    n = w * N; ph = nn / n
    kaydet(f"H1.Z_{w}", round((ph - 0.5) / np.sqrt(0.25 / n), 2)); kaydet(f"H1.phat_{w}", ph)
# Fisher (λ = Wow! günü eşleşme sayısı = 1)
for w, gun_say in ((10, 10), (100, 100)):
    say = d[d.window == w].groupby("day").size()
    p = stats.poisson.sf(say.values - 1, n1)
    chi = float((-2 * np.log(p)).sum()); df_ = 2 * gun_say
    kr = {str(al): round(float(stats.chi2.ppf(1 - al, df_)), 2) for al in (0.05, 0.01, 0.001)}
    kaydet(f"H1.Fisher_{w}", {"gun_eslesmeli": int(len(say)), "chi2": round(chi, 4), "df": df_, "kritik": kr,
                              "p_degeri": float(stats.chi2.sf(chi, df_)),
                              "sonuc": {al: ("red" if chi > c else "red değil") for al, c in kr.items()},
                              "gun_dagilimi": say.value_counts().sort_index().to_dict()})
# SNR (Thereus pencerelerde)
for w in (10, 100):
    mw = d[d.window == w]; h = int((mw.object_id.str.contains("Thereus")).sum())
    kaydet(f"H1.SNR_{w}", h / (len(mw) - h))
# KDE medyanlar
pre, post = d[d.day < "1990-01-01"].au, d[d.day >= "1990-01-01"].au
kaydet("H1.medyan_1990_once_sonra", [round(pre.median(), 2), round(post.median(), 2), round(post.median() - pre.median(), 2), len(pre), len(post)])
# DBSCAN (yazarın parametreleri)
X = StandardScaler().fit_transform(np.c_[d.day.map(pd.Timestamp.toordinal), d.au])
lab = DBSCAN(eps=0.3, min_samples=5).fit_predict(X); d["kume"] = lab
kum = []
for c in sorted(set(lab)):
    s = d[d.kume == c]
    kum.append({"kume": int(c), "n": len(s), "AU": [round(s.au.min(), 2), round(s.au.max(), 2)], "yil": [int(s.day.dt.year.min()), int(s.day.dt.year.max())]})
kaydet("H1.DBSCAN", kum)
# 30 noktalık hareketli ortalama, 2σ aykırı, Spearman
rm = d.au.rolling(30, min_periods=1, center=True).mean(); res = d.au - rm
kaydet("H1.2sigma_aykiri", int((res.abs() > 2 * res.std()).sum()))
rho, pv = stats.spearmanr(d.day.map(pd.Timestamp.toordinal), d.au)
kaydet("H1.spearman", [round(rho, 3), pv])
d["rm"] = rm
kaydet("H1.rm_1960_1980_ort", round(d[(d.day < "1981-01-01")].rm.mean(), 2))
kaydet("H1.rm_2005_2010_ort", round(d[(d.day >= "2005-01-01") & (d.day < "2011-01-01")].rm.mean(), 2))
kaydet("H1.rm_maks_ve_yil", [round(rm.max(), 2), int(d.loc[rm.idxmax(), "day"].year)])
# Kübik regresyon
Xo = d.day.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
mod = make_pipeline(PolynomialFeatures(3, include_bias=False), LinearRegression()).fit(Xo, d.au.values)
pr = mod.predict(Xo); kaydet("H1.kubik_R2", round(r2_score(d.au, pr), 3))
e = d.au.values - pr
kaydet("H1.artik_lag1", round(float(np.corrcoef(e[:-1], e[1:])[0, 1]), 3))
# artıkların periyodu (Lomb–Scargle, yıl)
from scipy.signal import lombscargle
t = (d.day - d.day.min()).dt.days.values / 365.25
per = np.linspace(4, 40, 2000); w_ = 2 * np.pi / per
pw = lombscargle(t, e - e.mean(), w_)
kaydet("H1.artik_baskin_periyot_yil", round(float(per[pw.argmax()]), 1))

# Bağımsız kontrol: Excel taraması (04_111gun önbelleği)
try:
    oz4, sag4 = pd.read_pickle(os.path.join(ANALIZ, "04_111gun", "cache", "ozet.pkl"))
    kaydet("H1.excel_kontrol", sag4.astype(str).values.tolist())
except Exception as ex:
    kaydet("H1.excel_kontrol", f"okunamadı: {ex}")

# =============================================================== H2
es = json.load(open(os.path.join(APP, "data", "eslesme_sonuclari 20590.txt"), encoding="utf-8"))
liste = [list(v.values())[0] for v in es.values()]
NH = len(liste); kaydet("H2.N", NH)
kaydet("H2.top8_yazar_dosyasi", [" - ".join(x.split(" (")[0] for x in m[1:]) for m in liste[:8]])
kaydet("H2.top8_payi_yuzde", round(800 / NH, 4))
pA = 8 / NH; nB = NH / 8
kaydet("H2.MethodA", {"P": pA, "alfa/P": round(0.001 / pA, 3), "Z": round((pA - 0.5) / np.sqrt(0.25 / NH), 2)})
kaydet("H2.MethodB", {"grup_sayisi": nB, "P": 1 / nB, "Z(N/8)": round((1 / nB - 0.5) / np.sqrt(0.25 / nB), 3),
                      "Z(2573.5)": round((1 / 2573.5 - 0.5) / np.sqrt(0.25 / 2573.5), 3)})
# Excel'den yeniden tarama (Top 8, S11, Grup A)
oz5, tops5 = pd.read_pickle(os.path.join(ANALIZ, "05_h2", "cache", "ozet.pkl"))
ref = oz5[oz5["Formül"] == "Ref"].iloc[0]
for kk in ("Eşleşme (±%1,5)", "Top 8 sapma aralığı (%)", "S11 kesimler (%)", "S11 grup sayıları", "En büyük boşluğun yeri (… sıradan sonra)",
           "Grup A cisim (Dünya dahil)", "A medyan e", "A ortalama e", "A: e < 0,02 payı", "A medyan i (°)", "A medyan Tj"):
    kaydet(f"H2.excel.{kk}", str(ref[kk]))
t8 = tops5["Ref"]
kaydet("H2.excel_top8", [f"{r_.Q.split(' (')[0]}-{r_.U.split(' (')[0]}-{r_.J.split(' (')[0]}: {r_['Sapma (%)']:.6f}" for _, r_ in t8.iterrows()])
kaydet("H2.excel_top8_AU", [[round(r_["Q AU"], 4), round(r_["U AU"], 4), round(r_["J AU"], 4)] for _, r_ in t8.iterrows()])
# Tablo 1'deki 4 basamaklı AU'larla sapma (|6|E−Q| − 5|U−J|| / 5|U−J|)
T1 = [(2.3406, 3.5354, 1.9420), (2.2162, 1.4160, 2.8601), (1.8336, 1.9299, 2.9149), (2.6046, 4.6201, 2.7098),
      (2.2448, 3.2121, 4.6905), (1.8336, 3.0757, 2.0907), (2.6688, 3.7098, 1.7225), (2.4062, 3.5505, 1.8784)]
E_ = 1.01279
kaydet("H2.tablo1_AU_ile_sapma", [round(abs(6 * abs(E_ - q) - 5 * abs(u - j)) / (5 * abs(u - j)) * 100, 5) for q, u, j in T1])

# Grup A yörünge elemanları (06_h3 önbelleği, yazarın eleman dosyası)
oz3, SON, EK = pd.read_pickle(os.path.join(ANALIZ, "06_h3", "cache", "h3_sonuc.pkl"))
S11 = SON["Ref"]["S11"]
kaydet("H2.grupA_cisim_sayisi(Dunya_haric)", len(S11))
kaydet("H2.grupA_e", {"ort": round(S11.e.mean(), 3), "medyan": round(S11.e.median(), 3), "min": round(S11.e.min(), 3), "max": round(S11.e.max(), 3),
                      "e<0.02": int((S11.e < 0.02).sum())})
kaydet("H2.grupA_i", {"medyan": round(S11["i (°)"].median(), 2), "i>=20": S11.loc[S11["i (°)"] >= 20, "Cisim"].tolist()})
kaydet("H2.grupA_Tj", {"medyan": round(S11.Tj.median(), 3), "Tj<3": S11.loc[S11.Tj < 3, "Cisim"].tolist(),
                       "|Tj-3|<0.2": int((S11.Tj.sub(3).abs() < 0.2).sum()), "aralik": [float(S11.Tj.min()), float(S11.Tj.max())]})
kaydet("H2.kapilar", S11[S11.Tj < 3][["Cisim", "Tj", "a (AU)", "e", "i (°)", "Sınıf"]].round(4).values.tolist())
kaydet("H2.S14", SON["Ref"]["S14"].values.tolist())

# =============================================================== H3
con = sqlite3.connect(os.path.join(APP, "data", "uzayli_bulmacasi_matrixson.db"))
CM = pd.read_sql("select * from CostMatrix", con)
kaydet("H3.matris_dugum_kenar", [int(CM.From_Asteroid.nunique()), len(CM)])


def c(a_, b_):
    r_ = CM[(CM.From_Asteroid.str.startswith(a_)) & (CM.To_Asteroid.str.startswith(b_))].Cost
    return round(float(r_.iloc[0]), 4) if len(r_) else None


B = {"E": "399", "Qx": "3763 ", "Uw": "15025 ", "Uk": "55701 ", "Th": "32532 ", "JC": "84011 ", "Qt": "755 ", "Ur": "23900 ",
     "Qq": "8755 ", "Jac": "25869 ", "QB": "28275 ", "Uly": "5254 ", "Qc": "4372 ", "Jo": "306001 ", "Jr": "169509 "}
kaydet("H3.ana_rota_adimlar(E-Qx-Uw-Uk)", [c(B["E"], B["Qx"]), c(B["Qx"], B["Uw"]), c(B["Uw"], B["Uk"])])
kaydet("H3.ana_rota_toplam", round(c(B["E"], B["Qx"]) + c(B["Qx"], B["Uw"]) + c(B["Uw"], B["Uk"]), 4))
kaydet("H3.dogrudan_Dunya_Ukalegon", c(B["E"], B["Uk"]))
kaydet("H3.Ukalegon_Thereus", c(B["Uk"], B["Th"]))
kaydet("H3.ara_rota(E-Qt-JC)", [c(B["E"], B["Qt"]), c(B["Qt"], B["JC"]), round(c(B["E"], B["Qt"]) + c(B["Qt"], B["JC"]), 4)])
kaydet("H3.dogrudan_Dunya_JC", c(B["E"], B["JC"]))
kaydet("H3.Urakawa_JC", c(B["Ur"], B["JC"]))
kaydet("H3.dogrudan_Dunya_Thereus", c(B["E"], B["Th"]))
ROTALAR = {1: ["E", "Qq", "Jac", "Th"], 2: ["E", "QB", "Uly", "Th"], 3: ["E", "Qt", "JC", "Th"], 4: ["E", "Qc", "Jo", "Th"],
           5: ["E", "Qx", "Uw", "Uk", "Th"], 6: ["E", "Qt", "Jr", "Th"]}
FT = {}
for no, y in ROTALAR.items():
    ad = [c(B[y[i]], B[y[i + 1]]) for i in range(len(y) - 1)]
    FT[no] = round(sum(x for x in ad if x is not None), 4) if None not in ad else None
    kaydet(f"H3.rota{no}_adimlar", ad)
kaydet("H3.FT", FT)
# Euclidean mesafeler (Horizons 15.08.1977, 06_h3 önbelleği)
HOR = json.load(open(os.path.join(ANALIZ, "06_h3", "cache", "horizons.json"), encoding="utf-8"))
AD = {"E": "399", "Qx": "3763 Qianxuesen (1980 TA6)", "Uw": "15025 Uwontario (1998 TX28)", "Uk": "55701 Ukalegon (1193 T-3)",
      "Th": "32532 Thereus (2001 PT13)", "JC": "84011 Jean-Claude (2002 OB25)", "Qt": "755 Quintilla (A908 GC)", "Qq": "8755 Querquedula (4586 P-L)",
      "Jac": "25869 Jacoby (2000 JP70)", "QB": "28275 Quoc-Bao (1999 CM23)", "Uly": "5254 Ulysses (1986 VG1)", "Qc": "4372 Quincy (1984 TB)",
      "Jo": "306001 Joanllaneras (2009 TD42)", "Jr": "169509 Jeffreyrobbins (2002 CV269)"}
P = {k_: np.array(HOR[v]["xyz"]) for k_, v in AD.items() if v in HOR and "xyz" in HOR[v]}
kaydet("H3.eksik_konum", [k_ for k_ in AD if k_ not in P])


def dist(a_, b_):
    return float(np.linalg.norm(P[a_] - P[b_]))


kaydet("H3.oklid_Dunya_Ukalegon", round(dist("E", "Uk"), 3))
leg = [round(dist("E", "Qx"), 3), round(dist("Qx", "Uw"), 3), round(dist("Uw", "Uk"), 3)]
kaydet("H3.ana_rota_oklid_adimlar", leg); kaydet("H3.ana_rota_oklid_toplam", round(sum(leg), 3))
kaydet("H3.uzama_kati", round(sum(leg) / dist("E", "Uk"), 2))
MT = {}
for no, y in ROTALAR.items():
    MT[no] = round(sum(dist(y[i], y[i + 1]) for i in range(len(y) - 1)), 2)
kaydet("H3.MT", MT)
MAK_FT = {1: 220.88, 2: 298.12, 3: 221.214, 4: 220.95, 5: 233.12, 6: 221.31}
MAK_MT = {1: 22.23, 2: 21.81, 3: 22.67, 4: 21.27, 5: 26.29, 6: 18.00}
kaydet("H3.EFF_makale_FT/MT", {k_: round(MAK_FT[k_] / MAK_MT[k_], 2) for k_ in MAK_FT})
kaydet("H3.EFF_yeni", {k_: round(FT[k_] / MT[k_], 2) for k_ in FT if FT[k_]})
kaydet("H3.yuzde28_46", [round(100 * (1 - (233.12 / 26.29) / (221.31 / 18.00)), 1), round(100 * (26.29 / 18.00 - 1), 1)])
# Stres testi (06_h3, yazarın ağ kuralıyla yeniden kurulmuş)
st = SON["Ref"]["stres"]
kaydet("H3.stres", st.round(4).astype(str).values.tolist())
jc = st[st["Kapı"].str.contains("Jean")].set_index("k"); uk = st[st["Kapı"].str.contains("Ukalegon")].set_index("k")
kaz = {"JC_Top5_k1_k4": round(100 * (1 - jc.loc[4, "Top 5"] / jc.loc[1, "Top 5"]), 1),
       "JC_Top4_k1_k4": round(100 * (1 - jc.loc[4, "Top 4"] / jc.loc[1, "Top 4"]), 1),
       "JC_Top1-5_ort_k1_k4": round(100 * (1 - jc.loc[4, ["Top 1", "Top 2", "Top 3", "Top 4", "Top 5"]].sum() / jc.loc[1, ["Top 1", "Top 2", "Top 3", "Top 4", "Top 5"]].sum()), 1),
       "UK_Top5_k1_k4": round(100 * (1 - uk.loc[4, "Top 5"] / uk.loc[1, "Top 5"]), 2),
       "k4_k7_degisim": round(100 * float(abs(jc.loc[7, "Top 5"] - jc.loc[4, "Top 5"]) / jc.loc[4, "Top 5"]), 4)}
kaydet("H3.optimizasyon_kazanci", kaz)
kaydet("H3.ilk_sira_yazar_dosyasi", {"Ukalegon": 4, "Jean-Claude": 5, "Uwontario": 6, "Jacoby": 13, "Quoc-Bao": 20, "Qianxuesen": 21,
                                      "Quintilla": 26, "Joanllaneras": 26, "Ulysses": 31, "Quincy": 33, "Querquedula": 40, "Jeffreyrobbins": 438,
                                      "Uwontario_ikinci": 34, "Quintilla_ikinci": 31})

json.dump(R, open(os.path.join(CIKTI, "dogrulama_sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\nKaydedildi:", os.path.join(CIKTI, "dogrulama_sonuc.json"))
