# -*- coding: utf-8 -*-
"""İş 6 raporu: Bölüm 3.3 (Hipotez 3) analizlerinin 15 formülün elbow grupları için karşılaştırması."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
import h3  # noqa: E402
import ortak as o  # noqa: E402

CIKTI = h3.CIKTI
ozet, SON, EKSIK = pd.read_pickle(os.path.join(h3.CACHE, "h3_sonuc.pkl"))
h3.eksikleri_tamamla()
FL = ozet["Formül"].tolist()
ref = ozet.set_index("Formül").loc["Ref"]
alt = ozet[ozet["Formül"] != "Ref"]

# ---------------------------------------------------------------- sağlama: makaledeki 6 rota birebir
E, T = h3.EARTH, h3.THEREUS
bul = lambda s: [x for x in h3.EL if x.startswith(s + " ")][0]
MAK = [("Route 1", ["8755", "25869"], 22.23, 220.88, 9.94), ("Route 2", ["28275", "5254"], 21.81, 298.15, 13.67),
       ("Route 3", ["755", "84011"], 22.67, 221.24, 9.76), ("Route 4", ["4372", "306001"], 21.27, 220.95, 10.39),
       ("Route 5", ["3763", "15025", "55701"], 26.29, 233.12, 8.87), ("Route 6", ["755", "169509"], 18.00, 221.31, 12.29)]
sag_rota = []
for ad, ss, mtm, ftm, effm in MAK:
    y = [E] + [bul(x) for x in ss] + [T]; h3.horizons(y)
    ft = sum(h3.maliyet(y[i], y[i + 1]) for i in range(len(y) - 1)); mt = h3.mt(y)
    sag_rota.append({"Rota": ad, "Duraklar": " → ".join(["Dünya"] + [bul(x).split(" (")[0] for x in ss] + ["Thereus"]),
                     "FT makale": ftm, "FT yeni": ft, "MT makale": mtm, "MT yeni": mt, "EFF makale": effm, "EFF yeni": ft / mt})
sag_rota = pd.DataFrame(sag_rota)
st = SON["Ref"]["stres"]
sag = pd.DataFrame([
    ["Ana / ara kapı", "55701 Ukalegon / 84011 Jean-Claude", f"{ref['Ana kapı']} / {ref['Ara kapı']}"],
    ["k=1 Top 5 (Jean-Claude)", "50,5587 / 50,5587 / 50,6257 / 78,3427 / 142,4267",
     " / ".join(f"{v:.4f}" for v in st[(st.k == 1) & st["Kapı"].str.startswith("Ara")].iloc[0, 2:7])],
    ["k=1 Top 5 (Ukalegon)", "220,9343 / 220,9343 / 220,9923 / 221,0013 / 221,5633",
     " / ".join(f"{v:.4f}" for v in st[(st.k == 1) & st["Kapı"].str.startswith("Ana")].iloc[0, 2:7])],
    ["k=7 Top 1 (Ukalegon / Jean-Claude)", "220,9343 / 50,5587",
     " / ".join(f"{v:.4f}" for v in st[st.k == 7]["Top 1"])],
    ["Tablo S14 yeni Tj<3 cisimler", "Jeffreyrobbins, Jacoby, Joanllaneras, Ulysses",
     ", ".join(x.split(" ")[1] for x in SON["Ref"]["S14"]["Cisim"])],
], columns=["Ölçüt", "Makale", "Yeni hesap"])

# ---------------------------------------------------------------- tablolar
T_grup = ozet[["Formül", "Eşitlik", "Elbow grubu (eşleşme)", "Elbow grubu cisim (Dünya dahil)", "Gruptaki Tj<3 sayısı",
               "Ana kapı", "Ana kapı Tj / sınıf", "Ara kapı", "Ara kapı Tj / sınıf", "Yeni Tj<3 (tüm eşleşmeler)",
               "Ek: rastgele grupta ≥1 Tj<3 asteroit olasılığı", "Ek: rastgele grupta ≥ gözlenen sayı olasılığı", "Ek: rastgele grup Tj<3 ortalaması"]]
T_stres = ozet[["Formül"] + [c for c in ozet.columns if "k=1 Top1" in c or "doğrudana eşit" in c]]
rot7 = []
for k in FL:
    for _, rw in SON[k]["rot7"].iterrows():
        rot7.append({"Formül": k, "Kapı": rw["Kapı"], "Rota (k=7)": rw["Rota (k=7)"], "Maliyet": rw["Maliyet"],
                     "Doğrudan Dünya→kapı": rw["Doğrudan Dünya→kapı maliyeti"], "Adımlar": rw["Adım maliyetleri"],
                     "Eğim terimi payı (%)": rw["Eğim terimi payı (%)"], "MT rota (AU)": rw["MT (AU)"],
                     "Doğrudan Öklid (AU)": rw["Doğrudan Öklid Dünya→kapı (AU)"]})
T_rot7 = pd.DataFrame(rot7)
T_th = ozet[["Formül", "Thereus: rota sayısı", "Thereus: en ucuz rota (FT)", "Thereus: en 'verimli' rota (EFF)",
             "Thereus: EFF birincisi grupta mı", "Thereus: EFF birincisi FT'de kaçıncı", "Thereus: EFF–MT sıra korelasyonu",
             "Thereus: EFF birincisi eşit maliyetli durak seçimine göre değişebilir mi", "Doğrudan Dünya→Thereus"]]
s15 = []
for k in FL:
    s = SON[k]["S15"]
    if len(s):
        s = s.drop(columns=["_yol", "_effmin", "_effmax"], errors="ignore").copy(); s.insert(0, "Formül", k); s15.append(s)
T_s15 = pd.concat(s15, ignore_index=True) if s15 else pd.DataFrame()
T_kendi = T_s15[T_s15["Hedef türü"] == "Kendi H1 hedefi"] if len(T_s15) else pd.DataFrame()
kom = {k: h3.EL[v] for k, v in h3.KENDI_HEDEF.items() if v in h3.EL and k != "Ref"}
T_kom = pd.DataFrame([{"Formül": k, "Hedef": h3.KENDI_HEDEF[k], "a (AU)": v["a"], "e": v["e"], "i (°)": v["i"], "Tj": v["Tj"],
                       "Tj kaynağı": v.get("Tj_kaynak", "")} for k, v in kom.items()])

# ---------------------------------------------------------------- paneller
pk = os.path.join(h3.CACHE, "tr_paneller"); os.makedirs(pk, exist_ok=True)   # Türkçe çalışma panelleri (teslim edilmez)
pkEN = os.path.join(CIKTI, "karsilastirma_EN")
fig, axs = plt.subplots(len(FL), 2, figsize=(14, 3.2 * len(FL)))
for row, k in zip(axs, FL):
    h3.g_stres(row, k, SON[k])
fig.suptitle("Fig. 5 / S16 — Stres testi (Top 5 maliyet, k = 1–7; noktalı çizgi: doğrudan Dünya→kapı maliyeti) — 15 formül", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.99]); fig.savefig(os.path.join(pk, "panel_fig5_stres.png"), dpi=70); plt.close(fig)
fig, axs = plt.subplots(5, 3, figsize=(24, 26)); axs = axs.ravel()
for ax, k in zip(axs, FL):
    h3.g_uclu(ax, k, SON[k])
fig.suptitle("Fig. 8 / S20 — Thereus rotaları: MT (kırmızı), FT (mavi), EFF (yeşil) — 15 formül", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.98]); fig.savefig(os.path.join(pk, "panel_fig8_uclu.png"), dpi=70); plt.close(fig)
# FT – EFF ilişkisi: EFF'in MT ile ters ilişkisi
fig, axs = plt.subplots(5, 3, figsize=(20, 22)); axs = axs.ravel()
for ax, k in zip(axs, FL):
    s = SON[k]["S15"]
    s = s[s["Hedef"] == h3.THEREUS] if len(s) else s
    if len(s):
        sc = ax.scatter(s["MT (AU)"], s["EFF = FT/MT"], c=s["FT (toplam maliyet)"], cmap="viridis", s=40)
        ax.set_xlabel("MT (AU)"); ax.set_ylabel("EFF = FT/MT"); fig.colorbar(sc, ax=ax, label="FT")
    ax.set_title(k)
for ax in axs[len(FL):]:
    ax.axis("off")
fig.suptitle("EFF ile fiziksel mesafe (MT) ilişkisi — renk: toplam maliyet (FT)", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(pk, "panel_eff_mt.png"), dpi=70); plt.close(fig)


def kac(x):
    return int(np.nansum(x))


# ---------------------------------------------------------------- rapor
R = o.Rapor("İş 6 — Makale Bölüm 3.3 (Hipotez 3) Analizlerinin 15 Formül İçin Tekrarı")
R.h("Ne yapıldı")
R.p("Makalenin 3.3 bölümünde (Supplementary 3.6–3.8 ve 4.3) yazarın Top 8 grubu için yapılan tüm işlemler, İş 5'teki her formülün "
    "kendi elbow grubu için aynen tekrarlandı. Elbow grubu = ilk 31 sıradaki en büyük sapma boşluğunun önündeki eşleşmeler "
    "(yazarın formülünde 8). Hesaplama yöntemleri ve formüller değiştirilmedi; yalnız her formülün seçtiği cisimler ve onların değerleri kullanıldı.")
R.p("Kullanılan yöntemler (yazarın kodlarıyla birebir: yenimatrisgunceldb.py, k7top5icin.py, thereushedef6maliyet.py): maliyet = "
    "1·|Δa| + 5·|Δe| + 10·|Δi| + 2·|ΔTj|; ağ: Dünya → her eşleşmenin Q cismi, eşleşme içinde Q → U → J, eşleşmeler arası serbest geçiş; "
    "Dijkstra; Top 5 için 'budama' (rotanın ilk durağı silinir); stres testi k = 1–7 grup (grup büyüklüğü = elbow sayısı); "
    "kapı seçimi: ana kapı Tj < 3 (varsa Jüpiter Truvası), ara kapı Tj ≤ 3 içinde 3'e en yakın; Tablo S14: tüm eşleşmelerde Tj < 3 "
    "taraması; Tablo S15 / Fig. 8: her Tj < 3 kapı için Dünya → kapı en ucuz ağ yolu + kapı → hedef doğrudan maliyet; "
    "MT = 15.08.1977 konumları (JPL Horizons) arasındaki Öklid mesafeleri toplamı; FT = toplam maliyet; EFF = FT / MT.")
R.p("Yörünge elemanları: yazarın genisletilmis_asteroid_db2.json dosyası (eksikler Faz 2 SBDB önbelleği); Dünya ve Thereus yazarın "
    "kodundaki değerler. Ortak hedef Thereus (yazarın hedefi). Formülün kendi H1 hedefi tek bir doğal cisimse o da hedef alındı "
    "(F5 Honda, F7 ve F7-mutlak Swift, F8 Baeker, F10 Heck-Sause); bunlar parabolik/hiperbolik kuyruklu yıldızlardır (e ≥ 1, a < 0), "
    "Tj'leri Tisserand formülüyle hesaplandı; maliyet formülü bu cisimler için fiziksel anlam taşımaz (ayrı tabloda verildi).")

R.h("1. Sağlama — yazarın formülü makaledeki sayıları veriyor mu?")
R.t("Sağlama: kapılar, Top 5, S14", sag)
R.t("Sağlama: makaledeki 6 Thereus rotası birebir", sag_rota)
R.p("Kapılar, Tablo 3 / S13'teki Top 5 maliyetleri, Tablo S14'teki 4 yeni Tj < 3 cismi ve Tablo 4 / S15'teki 6 rota maliyeti (FT) "
    "birebir yeniden üretildi. Makaledeki rotalar aynen girildiğinde fiziksel mesafeler (MT) de 0,05–0,26 AU farkla tutuyor "
    "(ör. Route 5: 26,31 / 26,29 AU); küçük fark konum hesabındaki yöntem farkından gelir. Yöntem doğrulandı.")
R.p("Önemli bulgu: Ağda aynı minimum maliyeti veren birden çok ara durak vardır (maliyet formülü ağırlıklı mutlak farklar toplamı olduğu "
    "için). Dijkstra bunlardan birini seçer; hangisinin seçildiği maliyeti değiştirmez ama fiziksel mesafeyi (MT), dolayısıyla EFF'i "
    "değiştirir. Örneğin yazarın formülünde Ukalegon rotası aynı maliyetle (220,93) Qianxuesen → Uwontario yerine başka bir Q durağı "
    "üzerinden gidince MT 26,29'dan ~19,7 AU'ya iner ve EFF 8,87'den ~11,9'a çıkar. Bu yüzden S15 tablosunda her kapı için eşit "
    "maliyetli tek duraklı alternatiflerin sayısı ve MT / EFF aralıkları da verildi.")

R.h("Kısa sonuç")
kapili = ozet[~ozet["Ana kapı"].str.startswith("Yok")]["Formül"].tolist()
esit = ozet.get("Ana kapı: Top1 doğrudana eşit mi (k=1)", pd.Series(dtype=object))
R.p(f"1) Kapı seçimi: elbow grubunda Tj < 3 asteroit (yazarın kapı kuralı) yalnız {len(kapili)}/15 formülde var: {', '.join(kapili)}. "
    "Diğer formüllerde ana / ara kapı seçilemiyor; bu formüller için yalnız tüm eşleşmelerde Tj < 3 taraması (S14) ve Thereus rotaları yapıldı.")
R.p(f"2) Bu durum formülün değer aralığına bağlı: yazarın formülünde rastgele seçilen 8'li grupların "
    f"%{ref['Ek: rastgele grupta ≥1 Tj<3 asteroit olasılığı']*100:.0f}'inde en az bir Tj < 3 asteroit, %{ref['Ek: rastgele grupta ≥ gözlenen sayı olasılığı']*100:.0f}'inde "
    "en az iki tane var (Top 8'de 2). Yani Top 8'de iki kapı bulunması sıradan bir durum; U harfli havuzdaki Truva cisimleri (Ukalegon gibi) "
    "bu formülün eşleşmelerine sık katılır. Eşleşmeleri ana kuşağa düşen formüllerde (F4, F5, F6, F7, F9, F10) rastgele gruplarda da Tj < 3 asteroit neredeyse hiç yok.")
R.p("3) Kapısı olan formüllerin hepsinde ana kapıya k = 1'de bulunan en iyi rota maliyeti doğrudan Dünya → kapı maliyetine eşit veya ondan "
    "yüksek; hiçbir stres testinde maliyet bu tabanın altına inmiyor. Duraklı rota 'tasarruf' sağlamıyor.")
R.p("4) Thereus rotalarında birden fazla rotası olan 8 formülün 4'ünde (yazarın formülü, F3, F4-mutlak, F8) EFF (= FT / MT) birincisi en ucuz rota (FT) değil; EFF fiziksel mesafe arttıkça düşüyor; "
    "F8'de EFF birincisi 104 AU'luk bir rota (EFF 2,96). Ayrıca eşit maliyetli durak seçenekleri arasında hangisinin seçildiği EFF sıralamasını "
    "değiştirebiliyor (yazarın formülü dahil). Yazarın formülündeki 'tasarruf', 'yakınsama' ve 'verimlilik' bulguları maliyet formülünün ve "
    "EFF tanımının yapısından gelir; formüle özgü değildir.")

R.h("2. Elbow grubu, Tj tablosu ve kapı seçimi (Tablo S11, S12)")
R.t("Grup ve kapılar", T_grup)
R.p("Kapı adayı kuralı (makaledeki gibi): kararlı yörüngeli numaralı asteroitler; kuyruklu yıldız, Centaur (a > 5,5 AU), gezegen ve uydu kapı olamaz. "
    "'Ek' sütunları: formülün tüm eşleşmelerinden aynı büyüklükte 2.000 rastgele grup çekildiğinde Tj < 3 asteroit bulunma olasılıkları.")
if EKSIK:
    R.t("Eksik elemanların tamamlanması", pd.DataFrame({"Cisim": list(EKSIK), "Kaynak": list(EKSIK.values())}))
for k in FL:
    R.t(f"S11 — {k}", SON[k]["S11"], sadece_excel=True)
R.p("Her formülün grup cisimleri ve Tj değerleri Excel'de 'S11 — …' sayfalarındadır.")

R.h("3. Stres testi (Tablo 3 / S13, Fig. 5 / S16)")
R.t("Stres testi özeti", T_stres)
for k in FL:
    if len(SON[k]["stres"]):
        R.t(f"S13 — {k}", SON[k]["stres"], sadece_excel=True)
R.img(os.path.join(pkEN, "Panel_Fig5_S16_Stress_Test.png"), "Stres testi — 15 formül (noktalı çizgi: doğrudan Dünya→kapı maliyeti)", genislik_cm=16)
R.p("Her formülde Top 1 maliyeti daha k = 1'de doğrudan Dünya → kapı maliyetine eşittir ve k arttıkça değişmez; artan düğüm sayısı "
    "yalnız Top 2–5'i bu tabana çeker. Yazarın 'asimptotik kararlılık / Hohmann limiti' olarak yorumladığı taban, doğrudan maliyetin kendisidir.")

R.h("4. Ana ve ara rotalar, k = 7 (Fig. 6 / S17, Fig. 7 / S18)")
R.t("k=7 rotaları", T_rot7)
R.p("Her rotanın maliyeti doğrudan Dünya → kapı maliyetine eşittir: duraklı rota tasarruf sağlamaz. Maliyetin büyük kısmı eğim "
    "teriminden (10 × Δi, derece) gelir. Ağ topolojisi ve 3D grafikler formül klasörlerindedir (Fig6_S17_Network_Topology.png, Fig7_S18_3D_Illustration.png).")

R.h("5. Tüm eşleşmelerde Tj < 3 taraması (Tablo S14)")
s14 = []
for k in FL:
    s = SON[k]["S14"]
    if len(s):
        s = s.copy(); s.insert(0, "Formül", k); s14.append(s)
if s14:
    R.t("S14 yeni kapılar", pd.concat(s14, ignore_index=True))

R.h("6. Thereus'a giden rotalar ve üçlü karşılaştırma (Tablo 4 / S15, Fig. 8 / S20)")
R.t("Thereus rotaları özeti", T_th)
R.t("Tüm rotalar (S15)", T_s15, sadece_excel=len(T_s15) > 80)
R.img(os.path.join(pkEN, "Panel_Fig8_S20_Triple_Comparison.png"), "Üçlü karşılaştırma — 15 formül", genislik_cm=16)
R.img(os.path.join(pkEN, "Panel_EFF_vs_MT.png"), "EFF ile MT ilişkisi — 15 formül", genislik_cm=16)
R.p(f"Yazarın formülünde: en ucuz rota (FT) {ref['Thereus: en ucuz rota (FT)']}; Dijkstra'nın seçtiği duraklarla EFF birincisi "
    f"{ref[chr(84)+'hereus: en ' + chr(39) + 'verimli' + chr(39) + ' rota (EFF)']}. Doğrudan Dünya → Thereus maliyeti "
    f"{ref['Doğrudan Dünya→Thereus']:.2f}; tüm rotalardan ucuzdur.")

R.h("7. Formülün kendi H1 hedefi (kuyruklu yıldızlar)")
if len(T_kom):
    R.t("Kendi hedeflerin elemanları", T_kom)
if len(T_kendi):
    R.t("Kendi hedefe rotalar", T_kendi, sadece_excel=len(T_kendi) > 60)
R.p("Bu hedefler parabolik/hiperbolik yörüngeli kuyruklu yıldızlardır (a < 0, e ≥ 1). Maliyet formülündeki |Δa| terimi bu durumda "
    "binlerce birime çıkar ve sonuca hâkim olur; rotalar hesaplanmış ama fiziksel anlamı yoktur. Bu nedenle karşılaştırma Thereus üzerinden yapıldı.")
# ---------------------------------------------------------------- 9. kapısı olan 4 formül: maliyet–verim karşılaştırması
K4 = ["Ref", "F2", "F3", "F8"]
k4 = [{"Formül": "Makale (yazarın sonucu)", "Ana kapı": "55701 Ukalegon", "Ara kapı": "84011 Jean-Claude",
       "Dünya→ana: rota / doğrudan": "220,93 / 220,93", "Dünya→ara: rota / doğrudan": "50,56 / 50,56",
       "Ana üzerinden Thereus: FT / MT / EFF": "233,12 / 26,29 / 8,87 (Route 5)",
       "Ara üzerinden Thereus: FT / MT / EFF": "221,24 / 22,67 / 9,76 (Route 3)",
       "En ucuz Thereus rotası (FT)": "Jacoby — 220,88 (Route 1)", "EFF birincisi": "Ukalegon — 8,87 (Route 5)",
       "EFF birincisinin FT sırası": 5}]
for k in K4:
    R_ = SON[k]; rot = R_["rot7"].set_index("Kapı") if len(R_["rot7"]) else None
    th = R_["S15"][R_["S15"]["Hedef türü"] == "Thereus"]
    def via(g):
        x = th[th["Kapı"] == g]
        if not g or not len(x):
            return "—"
        x = x.iloc[0]
        return f"{x['FT (toplam maliyet)']:.2f} / {x['MT (AU)']:.2f} / {x['EFF = FT/MT']:.2f} (eşit maliyetli seçeneklerle EFF {x['EFF min–max (alternatifler)']})"
    def dk(ad):
        if rot is None or ad not in rot.index:
            return "—"
        return f"{rot.loc[ad, 'Maliyet']:.2f} / {rot.loc[ad, 'Doğrudan Dünya→kapı maliyeti']:.2f}"
    bf = th.loc[th["FT (toplam maliyet)"].idxmin()]; be = th.loc[th["EFF = FT/MT"].idxmin()]
    k4.append({"Formül": k, "Ana kapı": R_["ana"] or "—", "Ara kapı": R_["ara"] or "—",
               "Dünya→ana: rota / doğrudan": dk("Ana"), "Dünya→ara: rota / doğrudan": dk("Ara"),
               "Ana üzerinden Thereus: FT / MT / EFF": via(R_["ana"]), "Ara üzerinden Thereus: FT / MT / EFF": via(R_["ara"]),
               "En ucuz Thereus rotası (FT)": f"{bf['Kapı'].split(' (')[0]} — {bf['FT (toplam maliyet)']:.2f}",
               "EFF birincisi": f"{be['Kapı'].split(' (')[0]} — {be['EFF = FT/MT']:.2f} (MT {be['MT (AU)']:.1f} AU)",
               "EFF birincisinin FT sırası": int(be["FT sırası"])})
T_k4 = pd.DataFrame(k4)
# grafik: kapı rotalarının FT, MT, EFF değerleri
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
etk, ft_, mt_, ef_, rk = ["Makale\nUkalegon", "Makale\nJean-Claude"], [233.12, 221.24], [26.29, 22.67], [8.87, 9.76], ["grey", "grey"]
renk = {"Ref": "tab:red", "F2": "tab:blue", "F3": "tab:green", "F8": "tab:purple"}
for k in K4:
    th = SON[k]["S15"]; th = th[(th["Hedef türü"] == "Thereus") & th["Kapı grupta mı"]]
    for _, x in th.iterrows():
        etk.append(f"{k}\n{x['Kapı'].split(' (')[0].split(' ')[-1]}"); ft_.append(x["FT (toplam maliyet)"]); mt_.append(x["MT (AU)"])
        ef_.append(x["EFF = FT/MT"]); rk.append(renk[k])
for ax, v, ad in zip(axs, (ft_, mt_, ef_), ("FT: toplam maliyet", "MT: fiziksel mesafe (AU)", "EFF = FT/MT (düşük = 'verimli')")):
    ax.bar(range(len(v)), v, color=rk); ax.set_xticks(range(len(v)), etk, fontsize=7, rotation=45); ax.set_title(ad)
    for i, val in enumerate(v):
        ax.text(i, val, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
fig.suptitle("Kapısı olan 4 formül: elbow grubundaki kapılar üzerinden Thereus rotaları (gri: makaledeki değerler)")
fig.tight_layout(); fig.savefig(os.path.join(pk, "kapi4_karsilastirma.png"), dpi=110); plt.close(fig)

R.h("8. Kapısı olan 4 formül: maliyet–verim karşılaştırması")
R.p("Elbow grubunda kapı seçilebilen dört formül (yazarın formülü, F2, F3, F8) makaledeki sonuçlarla yan yana verilmiştir. 'Rota / doğrudan': "
    "ağda k = 7'de bulunan en ucuz Dünya → kapı rotasının maliyeti ve Dünya → kapı doğrudan maliyeti. Thereus rotalarında FT = toplam maliyet, "
    "MT = 15.08.1977 konumları arasındaki mesafeler toplamı (AU), EFF = FT / MT. Parantez içi: aynı minimum maliyeti veren diğer tek duraklı "
    "seçenekler kullanılsaydı EFF'in alabileceği değer aralığı.")
R.t("Kapısı olan 4 formül", T_k4)
R.img(os.path.join(pkEN, "Panel_Gateway_Formulas_Thereus_Routes.png"), "Kapısı olan 4 formül — kapılar üzerinden Thereus rotaları (gri: makale)", genislik_cm=17)
R.p("Yazarın formülü: Ukalegon ve Jean-Claude rotalarının maliyetleri makaleyle aynıdır (220,93 ve 50,56; ikisi de doğrudan maliyete eşit). "
    "Thereus'a ana kapı üzerinden FT 233,12 her durakta aynıdır; MT ve EFF ise seçilen ara durağa göre değişir (EFF 8,87 makaledeki iki duraklı "
    "rotada, tek duraklı eşit maliyetli seçeneklerde 9,98–14,89). En ucuz Thereus rotası Jacoby (220,88), Ukalegon rotası ise en pahalı ikinci (233,12).")
R.p("F2 (3 eşleşmelik grup): tek kapı Ulysses (Tj 2,81, Truva). Dünya → Ulysses 253,40 = doğrudan maliyet; Thereus'a FT 298,14, MT 19,66, EFF 15,16. "
    "Makaledeki Route 2 ile aynı rota tipidir ve makalede de en pahalı rotaydı.")
R.p("F3 (29 eşleşmelik grup): tek kapı Joanllaneras (Tj 2,945, Truva). Dünya → Joanllaneras 112,51 = doğrudan maliyet; Thereus'a FT 220,95, "
    "MT 23,35, EFF 9,46. Bu değerler makaledeki Route 4 ile aynıdır (220,95). Yani F3'ün kapısı, yazarın 'Top 8 dışından' bulduğu kapılardan "
    "birini kendi elbow grubunda veriyor ve yazarın Route 5'inden (233,12) daha ucuz bir rota üretiyor.")
R.p("F8 (28 eşleşmelik grup): kapılar Ulysses (ana) ve Jean-Claude (ara) — yazarın kapılarından biri (Jean-Claude) burada da çıkıyor. Ancak F8'in "
    "bütün eşleşmelerinde Q cismi Kuiper kuşağı cismi 50000 Quaoar (~43 AU) olduğu için ağ yapısı gereği Dünya'dan çıkan her rota önce Quaoar'a "
    "gider: Dünya → ana 329,25 (doğrudan 253,40), Dünya → ara 208,43 (doğrudan 50,56). Rotalar ~100 AU uzunluğundadır ve EFF = FT / MT bu "
    "yüzden çok düşük çıkar (2,96–3,75): EFF ölçütüne göre F8'in rotaları yazarınkilerden (8,87) üç kat 'daha verimli' görünür, oysa toplam "
    "maliyetleri (296–379) yazarınkilerden yüksektir.")
R.p("Sonuç: Dört formülde de (1) Dünya → kapı maliyeti ağ izin verdiğinde doğrudan maliyete eşittir, izin vermediğinde (F8) daha yüksektir; "
    "hiçbir yerde tasarruf yoktur. (2) Thereus'a toplam maliyet (FT) açısından yazarın Route 5'i (233,12) dört formülün kapı rotaları arasında "
    "ne en ucuz ne en pahalıdır; F3'ün kapısı daha ucuz bir rota verir. (3) EFF açısından 'en verimli' rota en uzun rotadır (F8, ~100 AU); "
    "EFF mesafeye bölündüğü için fiziksel uzunluğu ödüllendirir. Yazarın formülünün kapıları bu ölçütlerin hiçbirinde ayrışmaz.")

R.h("9. Yorum: farklı formüllerle ne bulduk?")
R.h("9.1 Yöntem doğrulandı", 3)
R.p("Yazarın formülüyle kapılar (Ukalegon, Jean-Claude), Tablo 3'teki Top 5 maliyetleri, Tablo S14'teki 4 yeni Tj < 3 cismi ve makaledeki "
    "6 Thereus rotasının maliyet (FT), mesafe (MT) ve verimlilik (EFF) değerleri birebir veya çok küçük farkla yeniden üretildi "
    "(ör. Route 5: FT 233,12 / 233,12; MT 26,29 / 26,31; EFF 8,87 / 8,86).")
R.h("9.2 Kapılar yalnız 4 formülde seçilebildi", 3)
R.p("Elbow grubunda yazarın kapı kuralına uyan (Tj < 3, kararlı asteroit) cisim yalnız yazarın formülünde, F2, F3 ve F8'de var; diğer 11 "
    f"formülde ana ve ara kapı yok. Bu formülün değer aralığına bağlıdır: yazarın formülünde rastgele 8'li grupların %{ref['Ek: rastgele grupta ≥1 Tj<3 asteroit olasılığı']*100:.0f}'inde "
    f"en az bir, %{ref['Ek: rastgele grupta ≥ gözlenen sayı olasılığı']*100:.0f}'inde en az iki Tj < 3 asteroit vardır; Top 8'de iki kapı bulunması sıradandır. "
    "U harfli havuzdaki Jüpiter Truvaları (Ukalegon gibi) bu formülün eşleşmelerine sık katılır. Eşleşmeleri ana kuşağa düşen formüllerde "
    "(F4, F5, F6, F7, F9, F10) rastgele gruplarda da Tj < 3 asteroit neredeyse hiç yoktur.")
R.h("9.3 Duraklı rotalar tasarruf sağlamıyor", 3)
R.p("Kapısı olan her formülde k = 1'deki en iyi rota maliyeti doğrudan Dünya → kapı maliyetine eşit veya ondan yüksektir (F8'de ağ rotayı önce "
    "bir Q cisminden geçmeye zorladığı için 329,25'e karşı 253,40). Hiçbir stres testinde maliyet bu tabanın altına inmez. Yazarın 'asimptotik "
    "kararlılık / Hohmann limiti' olarak yorumladığı değer doğrudan Dünya → kapı maliyetidir; maliyet formülü ağırlıklı mutlak farkların "
    "toplamı olduğu için duraklı rota doğrudan rotadan ucuz olamaz.")
R.h("9.4 EFF sıralaması keyfî", 3)
th = SON["Ref"]["S15"]
uk = th[th["Kapı"].str.startswith("55701")].iloc[0]
R.p(f"Ağda aynı minimum maliyeti veren çok sayıda ara durak vardır: yazarın formülünde her Thereus kapısı için "
    f"{int(th['Eşit maliyetli tek duraklı alternatif sayısı'].min())}–{int(th['Eşit maliyetli tek duraklı alternatif sayısı'].max())} "
    "eşit maliyetli tek duraklı seçenek bulunur. Maliyet aynı kaldığı hâlde seçilen durağa göre fiziksel mesafe ve dolayısıyla EFF değişir: "
    f"Ukalegon rotasının EFF'i tek duraklı seçeneklerde {uk['EFF min–max (alternatifler)']}, makaledeki iki duraklı rotada 8,87'dir. "
    "Makaledeki 'Route 5 en verimli' sonucu bu eşit maliyetli seçeneklerden birinin seçilmesine bağlıdır; Dijkstra başka bir durak "
    "seçtiğinde EFF birincisi Jean-Claude olur. EFF = FT / MT tanımı uzun rotaları ödüllendirir: F8'de EFF birincisi 104 AU uzunluğunda "
    "bir rotadır (EFF 2,96). Birden fazla rotası olan 8 formülün 4'ünde (yazarın formülü, F3, F4-mutlak, F8) EFF birincisi en ucuz rota (FT) değildir.")
R.h("9.5 Doğrudan rota en ucuzu", 3)
R.p(f"Doğrudan Dünya → Thereus maliyeti ({ref['Doğrudan Dünya→Thereus']:.2f}) tüm formüllerde tüm rotalardan ucuzdur; en ucuz duraklı rota "
    "yazarın formülünde Jacoby üzerinden (220,88), Ukalegon üzerinden değil (233,12).")
R.h("9.6 Formüllerin kendi H1 hedefleri", 3)
R.p("F5 (Honda), F7 ve F7-mutlak (Swift), F8 (Baeker) ve F10 (Heck-Sause) hedefleri parabolik/hiperbolik kuyruklu yıldızlardır (e ≥ 1, a < 0); "
    "maliyet formülünün |Δa| terimi bu durumda binlerce birime çıkar. Rotalar hesaplandı ama fiziksel anlam taşımaz.")
R.h("9.7 Genel sonuç", 3)
R.p("3.3 bölümündeki bulguların ('tasarruf', 'stres testinde yakınsama', 'gizli enerji tünelleri', 'en verimli rota') hepsi maliyet formülünün "
    "ve EFF tanımının matematiksel yapısından gelir; formüle özgü değildir. Yazarın formülünü farklı kılan tek şey, eşleşmelerine Jüpiter "
    "Truvası ve Hilda cisimlerinin katılmasıdır; bu da formülün değer aralığının (U ≈ 4,6 AU) sonucudur.")
R.h("9.8 FT, MT, EFF ne demek ve neden yazarın formülü ile F3 aynı sonucu veriyor?", 3)
R.p("FT (toplam formül maliyeti): rotadaki adımların maliyet formülüyle (1·|Δa| + 5·|Δe| + 10·|Δi| + 2·|ΔTj|) hesaplanan toplamı; "
    "yazarın 'enerji maliyeti'. MT (fiziksel mesafe): rotadaki cisimlerin 15.08.1977 konumları arasındaki düz çizgi mesafelerinin toplamı (AU). "
    "EFF (verimlilik) = FT / MT: 1 AU başına düşen maliyet; düşük değer 'verimli' sayılır.")
ab = []
for k_ in ("Ref", "F3"):
    d_ = SON[k_]["S15"]; d_ = d_[d_["Hedef türü"] == "Thereus"].copy(); d_["Kapı kısa"] = d_["Kapı"].str.split(" ").str[1]
    ab.append(d_.set_index("Kapı kısa")[["FT (toplam maliyet)", "MT (AU)", "EFF = FT/MT", "Kapı grupta mı"]].add_suffix(f" — {k_}"))
T_ab = pd.concat(ab, axis=1).reset_index().rename(columns={"Kapı kısa": "Kapı"})
R.t("Yazarın formülü ve F3: aynı kapılar, aynı maliyetler", T_ab)
R.p("Yazarın formülünde ve F3'te Thereus rotaları aynı 6 kapıdan geçer (Ukalegon, Jean-Claude, Jeffreyrobbins, Jacoby, Joanllaneras, Ulysses) "
    "ve FT değerleri birebir aynıdır; en ucuz rota ikisinde de Jacoby (220,88), EFF birincisi ikisinde de Jean-Claude'dur. Bunun nedeni: "
    "(1) Q, U, J havuzunda kapı kuralına uyan (Tj < 3, kararlı) asteroitler yalnız bu birkaç Truva/Hilda cismidir; formül yalnız hangisinin "
    "'elbow grubunda', hangisinin 'sonradan taramada' bulunduğunu belirler (yazarın formülünde Ukalegon ve Jean-Claude grupta, F3'te Joanllaneras). "
    "(2) Rota maliyeti FT = Dünya → kapı (ağda, doğrudan maliyete eşit) + kapı → Thereus (doğrudan) olduğu için yalnız kapının yörünge "
    "elemanlarına bağlıdır; formülden bağımsızdır. (3) MT ve EFF yalnız ağın eşit maliyetli seçenekler arasında seçtiği ara durağa göre "
    "küçük farklar gösterir (Jean-Claude: 27,05 / 26,05 AU; Jeffreyrobbins: 13,91 / 16,24 AU). Dolayısıyla iki formülün 'düşük' ve "
    "aynı çıkması bir rastlantı ya da sinyal değil, aynı aday kümesinin aynı maliyet formülüyle değerlendirilmesinin sonucudur.")
R.p("Jacoby en ucuzdur, çünkü eğimi (16,96°) Thereus'unkine (20,37°) yakın ve Dünya'dan büyüktür; maliyetin büyük kısmı eğim teriminden "
    "geldiği için eğimi Dünya ile Thereus arasında olan kapılar toplamda doğrudan maliyete en yakın rotayı verir (doğrudan Dünya → Thereus "
    "220,26). Jean-Claude EFF birincisidir, çünkü maliyeti neredeyse en düşük olanlarla aynıyken (221,23) rotası en uzun olanlardandır (≈ 26–27 AU); "
    "EFF mesafeye böldüğü için uzun rotayı ödüllendirir.")

R.h("9.9 Veri notları", 3)
R.p(f"Yörünge elemanı eksik 11 cisim tamamlandı: Uranüs ve Jüpiter (JPL ortalama elemanları), uydular Umbriel, Janus, Jarnsaxa (ait oldukları "
    f"gezegenin yörüngesi), 5 kuyruklu yıldız ve 4760 Jia-xiang (SBDB). 15.08.1977 konumları JPL Horizons'tan çekildi ({len(h3.HOR)} cisim). "
    "Makaledeki 'kararlı asteroit' şartı gereği kuyruklu yıldız, Centaur (a > 5,5 AU), gezegen ve uydular kapı adayı sayılmadı; bu kural "
    "olmadan F9'da bir kuyruklu yıldız (C/2000 W1) kapı seçiliyordu (maliyet 182.622). Dünya ve Thereus için yazarın kodundaki değerler kullanıldı.")

R.kaydet("06_H3_karsilastirma", klasor=CIKTI)
print(sag.to_string()); print(sag_rota.round(2).to_string())
