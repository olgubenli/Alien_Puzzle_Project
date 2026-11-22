# -*- coding: utf-8 -*-
"""Makale Bölüm 3.1 (Hipotez 1) analizlerinin 22 eşitlik için tekrarı.
Parametreler yazarın orijinal kodundan (Alien_Puzzle_Project/src/yenigrafik49.py) ve Supplementary Denklem 1–8'den alındı:
  - P-değeri = (Wow! günü eşleşme sayısı) / N, N = 26.576 (makaledeki havuz)
  - Z = (p̂ − 0,5)/√(0,25/n), n = gün × N
  - Fisher: λ = Wow! günü eşleşme sayısı; p_i = P(X ≥ k_i | λ) (Poisson sağ kuyruk); χ² = −2 Σ ln p_i, df = 2k
  - SNR = Wow! günü cisim(ler)inin pencere içindeki tespitleri / diğer tespitler
  - KDE: 1990 öncesi / sonrası, medyanlar
  - DBSCAN: StandardScaler(zaman ordinal, AU), eps = 0,3, min_samples = 5
  - 30 noktalık merkezli hareketli ortalama, artıkların 2σ dışı = aykırı; Spearman ρ (zaman ordinal, AU)
  - 3. derece polinom regresyon (zaman ordinal), R², artıklar"""
import os, re, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402
from tarama import KODLAR, YAZIM  # noqa: E402

warnings.filterwarnings("ignore")
KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti")
N_HAVUZ = 26576
SPLIT = pd.Timestamp("1990-01-01")
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10})

m_all = pd.read_pickle(os.path.join(KOK, "cache", "eslesmeler.pkl"))
h_all = pd.read_pickle(os.path.join(KOK, "cache", "hedefler.pkl"))
GUNLER = h_all[["day", "window"]].drop_duplicates().sort_values("day")
WOW = GUNLER[GUNLER.window == 1].day.iloc[0]
G10 = GUNLER[GUNLER.window == 10].day.tolist()
G100 = GUNLER[GUNLER.window == 100].day.tolist()


# ================================================================== hesaplar
def istatistik(kod):
    m = m_all[m_all.formul == kod].sort_values("day", kind="mergesort").copy()
    r = {"Formül": kod, "Eşitlik": YAZIM[kod]}
    n1, n10, n100 = (int((m.window == w).sum()) for w in (1, 10, 100))
    r.update({"1 gün": n1, "10 gün": n10, "100 gün": n100, "Toplam (111)": len(m),
              "Benzersiz cisim": m.object_id.nunique()})
    wow_obj = set(m[m.window == 1].object_id)
    r["Wow! günü cisim(ler)i"] = "; ".join(sorted(wow_obj)) if wow_obj else "—"
    rep = m.object_id.value_counts()
    r["En sık 3 cisim"] = "; ".join(f"{k} ({v})" for k, v in rep.head(3).items())
    # Denklem 1 ve Z-testleri
    r["P-değeri (n₁/N)"] = n1 / N_HAVUZ
    r["P / α(0,001) oranı"] = (0.001 / (n1 / N_HAVUZ)) if n1 else np.nan
    for w, k in ((10, 10), (100, 100)):
        n = k * N_HAVUZ; ph = (n10 if w == 10 else n100) / n
        r[f"Z ({w} gün)"] = (ph - 0.5) / np.sqrt(0.25 / n)
    # Fisher
    fis = {}
    for w, gun in ((10, G10), (100, G100)):
        say = m[m.window == w].groupby("day").size().reindex(gun, fill_value=0)
        if n1 == 0:
            r[f"Fisher χ² ({w} gün)"] = np.nan; r[f"Fisher sonuç ({w} gün)"] = "Tanımsız (λ = 0)"
            fis[w] = pd.DataFrame({"Tarih": [d.date() for d in gun], "Eşleşme": say.values})
            continue
        p = np.array([stats.poisson.sf(k - 1, n1) if k > 0 else 1.0 for k in say.values])
        katki = -2 * np.log(p); chi = katki.sum(); df_ = 2 * len(gun)
        kr = {a: stats.chi2.ppf(1 - a, df_) for a in (0.05, 0.01, 0.001)}
        r[f"Fisher χ² ({w} gün)"] = chi
        r[f"Fisher sonuç ({w} gün)"] = ", ".join(f"α={a}: {'H0 red' if chi > c else 'H0 kabul'}" for a, c in kr.items())
        fis[w] = pd.DataFrame({"Tarih": [d.date() for d in gun], "Eşleşme": say.values, "p_i": p, "−2·ln(p_i)": katki})
    # SNR
    for w in (10, 100):
        mw = m[m.window == w]
        if not wow_obj:
            r[f"SNR ({w} gün)"] = np.nan
        else:
            hedef = mw.object_id.isin(wow_obj).sum(); diger = len(mw) - hedef
            r[f"SNR ({w} gün)"] = hedef / diger if diger else np.nan
    # KDE / medyanlar
    pre, post = m[m.day < SPLIT].au, m[m.day >= SPLIT].au
    r.update({"Medyan tümü (AU)": m.au.median() if len(m) else np.nan,
              "Medyan 1990 öncesi": pre.median() if len(pre) else np.nan,
              "Medyan 1990 sonrası": post.median() if len(post) else np.nan,
              "N öncesi / sonrası": f"{len(pre)} / {len(post)}"})
    # DBSCAN
    db = None
    if len(m) >= 5:
        X = StandardScaler().fit_transform(np.c_[m.day.map(pd.Timestamp.toordinal), m.au])
        if len(m) > 15000:  # bellek sınırı: sabit tohumlu 15.000 örnek, kalan noktalar en yakın örneğin etiketini alır
            from sklearn.neighbors import KNeighborsClassifier
            ix = np.random.default_rng(0).choice(len(m), 15000, replace=False)
            lab_s = DBSCAN(eps=0.3, min_samples=5).fit_predict(X[ix])
            lab = KNeighborsClassifier(1).fit(X[ix], lab_s).predict(X); lab[ix] = lab_s
            r["DBSCAN not"] = "15.000 noktalık örnekle"
        else:
            lab = DBSCAN(eps=0.3, min_samples=5).fit_predict(X)
        m["kume"] = lab
        ks = [k for k in sorted(set(lab)) if k != -1]
        r["DBSCAN küme sayısı"] = len(ks); r["DBSCAN gürültü"] = int((lab == -1).sum())
        r["DBSCAN küme boyutları"] = ", ".join(str(int((lab == k).sum())) for k in ks)
        db = m.groupby("kume").agg(Adet=("au", "size"), AU_min=("au", "min"), AU_max=("au", "max"),
                                   İlk=("day", "min"), Son=("day", "max")).reset_index()
    else:
        r["DBSCAN küme sayısı"] = np.nan; r["DBSCAN gürültü"] = np.nan; r["DBSCAN küme boyutları"] = "Yetersiz veri"
    # hareketli ortalama, aykırı, Spearman
    if len(m) >= 3:
        rm = m.au.rolling(30, min_periods=1, center=True).mean(); res = m.au - rm
        sig = res.std(); m["rm"] = rm.values; m["aykiri"] = (res.abs() > 2 * sig).values
        rho, pv = stats.spearmanr(m.day.map(pd.Timestamp.toordinal), m.au)
        r.update({"2σ aykırı sayısı": int(m.aykiri.sum()), "Spearman ρ": rho, "Spearman p": pv})
    else:
        r.update({"2σ aykırı sayısı": np.nan, "Spearman ρ": np.nan, "Spearman p": np.nan})
    # kübik regresyon
    if len(m) >= 5 and m.day.nunique() >= 4:
        X = m.day.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
        mod = make_pipeline(PolynomialFeatures(3, include_bias=False), LinearRegression()).fit(X, m.au.values)
        pr = mod.predict(X); m["pred"] = pr
        r["Kübik R²"] = r2_score(m.au.values, pr)
        e = m.au.values - pr
        r["Artık lag-1 otokorelasyon"] = np.corrcoef(e[:-1], e[1:])[0, 1] if len(e) > 2 and e.std() > 0 else np.nan
        m.attrs["model"] = mod
    else:
        r["Kübik R²"] = np.nan; r["Artık lag-1 otokorelasyon"] = np.nan
    hd = h_all[h_all.formul == kod]
    r["Hedef Q aralığı (AU)"] = f"{hd.hedef_ana.min():.2f}–{hd.hedef_ana.max():.2f}" if hd.hedef_ana.notna().any() else "Kök yok"
    return r, m, fis, db, rep


# ================================================================== grafikler (ax tabanlı)
def _bos(ax, kod, neden="Yetersiz veri"):
    ax.text(0.5, 0.5, neden, ha="center", va="center", transform=ax.transAxes, color="grey")
    ax.set_title(kod)


def _qt(ax, kod):
    hd = h_all[h_all.formul == kod].sort_values("day")
    for _, r in hd.iterrows():
        for v in str(r.hedefler).split("; "):
            if v and v != "nan":
                ax.plot(r.day, float(v), "_", color="grey", ms=5, alpha=0.6)


def g_violin(ax, kod, m):
    veri = [m[m.window == w].au.values for w in (1, 10, 100)]
    if not len(m):
        return _bos(ax, kod)
    for i, v in enumerate(veri, 1):
        if len(v) >= 2 and np.ptp(v) > 0:
            vp = ax.violinplot(v, [i], showextrema=False); [b.set_alpha(0.35) for b in vp["bodies"]]
            ax.boxplot(v, positions=[i], widths=0.15, showfliers=False)
        if len(v):
            ax.scatter(np.full(len(v), i) + np.random.default_rng(0).uniform(-0.05, 0.05, len(v)), v, s=6, c="k", alpha=0.5)
        ax.text(i, 1.01, f"n={len(v)}", transform=ax.get_xaxis_transform(), ha="center", fontsize=8)
    ax.set_xticks([1, 2, 3], ["1g", "10g", "100g"]); ax.set_ylabel("AU"); ax.set_title(kod)


def g_strip(ax, kod, m):
    if not len(m):
        return _bos(ax, kod)
    rng = np.random.default_rng(1)
    for i, w in enumerate((1, 10, 100), 1):
        v = m[m.window == w].au.values
        ax.scatter(np.full(len(v), i) + rng.uniform(-0.1, 0.1, len(v)), v, s=8, alpha=0.6)
    ax.set_xticks([1, 2, 3], ["1g", "10g", "100g"]); ax.set_ylabel("AU"); ax.set_title(kod)


def g_varlik10(ax, kod, m, maks=60):
    d = m[m.window.isin([1, 10])]
    if not len(d):
        return _bos(ax, kod, "1g + 10g'de eşleşme yok")
    gun = [WOW] + G10
    obj = d.object_id.value_counts().index[:maks].tolist()[::-1]
    M = np.full((len(obj), len(gun)), np.nan)
    for _, r in d[d.object_id.isin(obj)].iterrows():
        M[obj.index(r.object_id), gun.index(r.day)] = r.au
    im = ax.imshow(M, aspect="auto", cmap="turbo", interpolation="nearest")
    ax.set_xticks(range(len(gun)), ["1977*"] + [g.strftime("%Y") for g in G10], rotation=90, fontsize=6)
    ax.set_yticks(range(len(obj)), [x[:22] for x in obj] if len(obj) <= 30 else [""] * len(obj), fontsize=5)
    ax.set_title(kod + (f" (ilk {maks})" if d.object_id.nunique() > maks else ""))
    return im


def g_matris111(ax, kod, m, maks=150):
    if not len(m):
        return _bos(ax, kod)
    gun = GUNLER.day.tolist()
    obj = sorted(m.object_id.value_counts().index[:maks].tolist())
    M = np.full((len(obj), len(gun)), np.nan)
    ix = {g: i for i, g in enumerate(gun)}; io = {x: i for i, x in enumerate(obj)}
    for r in m[m.object_id.isin(obj)].itertuples():
        M[io[r.object_id], ix[r.day]] = r.au
    im = ax.imshow(M, aspect="auto", cmap="turbo", interpolation="nearest")
    ax.set_xlabel("Gün (D1…D111, kronolojik)"); ax.set_ylabel("Cisim")
    ax.set_title(kod + (f" (en sık {maks} cisim)" if m.object_id.nunique() > maks else f" ({len(obj)} cisim)"))
    return im


def g_pasta(ax, kod, rep, n=8):
    if not len(rep):
        return _bos(ax, kod)
    ust = rep.head(n); diger = rep.iloc[n:].sum()
    vals = list(ust.values) + ([diger] if diger else []); lab = [x[:18] for x in ust.index] + (["Diğer"] if diger else [])
    ax.pie(vals, labels=lab, autopct=lambda p: f"{p:.1f}%" if p > 3 else "", textprops={"fontsize": 6})
    ax.set_title(kod)


def g_kde(ax, kod, m):
    pre, post = m[m.day < SPLIT].au.values, m[m.day >= SPLIT].au.values
    if len(m) < 2 or np.ptp(m.au) == 0:
        return _bos(ax, kod)
    lo, hi = m.au.min(), m.au.max(); pad = 0.05 * (hi - lo); x = np.linspace(lo - pad, hi + pad, 300)
    ax.hist(m.au, bins=40, density=True, color="grey", alpha=0.25)
    for v, c, ad in ((m.au.values, "k", "Tümü"), (pre, "tab:blue", "1990 öncesi"), (post, "tab:orange", "1990 sonrası")):
        if len(v) >= 2 and np.ptp(v) > 0:
            ax.plot(x, stats.gaussian_kde(v)(x), color=c, ls="--" if c == "k" else "-", label=f"{ad} (N={len(v)})")
        if len(v):
            ax.axvline(np.median(v), color=c, ls=":", lw=1)
    ax.set_xlabel("AU"); ax.set_title(kod); ax.legend(fontsize=6)


def g_dbscan(ax, kod, m):
    if "kume" not in m:
        return _bos(ax, kod)
    for k in sorted(m.kume.unique()):
        s = m[m.kume == k]
        if k == -1:
            ax.scatter(s.day, s.au, marker="x", c="k", s=14, label=f"Gürültü ({len(s)})")
        else:
            ax.scatter(s.day, s.au, s=9, label=f"Küme {k+1} ({len(s)})")
    _qt(ax, kod); ax.set_title(kod); ax.legend(fontsize=6); ax.set_ylabel("AU")


def g_rolling(ax, kod, m, rho=None):
    if "rm" not in m:
        return _bos(ax, kod)
    ax.scatter(m.day, m.au, s=7, c=m.au, cmap="turbo", alpha=0.7)
    ax.plot(m.day, m.rm, "r-", lw=1.5, label="30 nokta hareketli ort.")
    sig = (m.au - m.rm).std()
    ax.fill_between(m.day, m.rm - 2 * sig, m.rm + 2 * sig, color="grey", alpha=0.2, label="±2σ")
    a_ = m[m.aykiri]; ax.scatter(a_.day, a_.au, marker="x", c="k", s=18, label=f"Aykırı ({len(a_)})")
    _qt(ax, kod)
    ax.set_title(kod + (f"  ρ={rho:.2f}" if rho is not None and np.isfinite(rho) else "")); ax.legend(fontsize=6); ax.set_ylabel("AU")


def g_regresyon(ax, kod, m, r2=None):
    if "pred" not in m:
        return _bos(ax, kod)
    ax.scatter(m.day, m.au, s=7, alpha=0.6)
    xs = np.linspace(m.day.map(pd.Timestamp.toordinal).min(), m.day.map(pd.Timestamp.toordinal).max(), 300)
    ax.plot([pd.Timestamp.fromordinal(int(v)) for v in xs], m.attrs["model"].predict(xs.reshape(-1, 1)), "b-", label="Kübik model")
    ax.plot(m.day, m.rm, "r--", lw=1, label="Hareketli ort.")
    _qt(ax, kod)
    ax.set_title(kod + (f"  R²={r2:.3f}" if r2 is not None and np.isfinite(r2) else "")); ax.legend(fontsize=6); ax.set_ylabel("AU")


def g_artik(ax, kod, m):
    if "pred" not in m:
        return _bos(ax, kod)
    e = m.au - m.pred
    ax.scatter(m.day, e, s=7, c=np.sign(e), cmap="coolwarm"); ax.axhline(0, color="k", lw=0.8)
    ax.set_title(kod); ax.set_ylabel("Artık (AU)")


GRAFIKLER = [  # dosya adı, makaledeki karşılığı, fonksiyon anahtarı
    ("fig1_violin", "Fig. 1 — Pencerelere göre AU dağılımı", "violin"),
    ("figS2_strip", "Fig. S2 — Pencerelere göre AU (jitter)", "strip"),
    ("figS3_varlik_10g", "Fig. S3 — 10 gün (+1977) varlık matrisi", "varlik10"),
    ("figS4_matris_111g", "Fig. S4 — 111 gün varlık matrisi", "matris111"),
    ("figS5_pasta", "Fig. S5 — Cisim tekrar payları", "pasta"),
    ("fig2_kde_1990", "Fig. 2 — 1990 öncesi/sonrası AU yoğunluğu (KDE)", "kde"),
    ("fig3_dbscan", "Fig. 3 — DBSCAN kümeleme (zaman × AU)", "dbscan"),
    ("figS8_hareketli_ort", "Fig. S8 — Hareketli ortalama, 2σ aykırılar, Spearman", "rolling"),
    ("figS9_regresyon", "Fig. S9 — Kübik polinom regresyon", "regresyon"),
    ("figS10_artiklar", "Fig. S10 — Regresyon artıkları", "artik"),
]


def ciz(anahtar, ax, kod, m, rep, r):
    f = {"violin": lambda: g_violin(ax, kod, m), "strip": lambda: g_strip(ax, kod, m),
         "varlik10": lambda: g_varlik10(ax, kod, m), "matris111": lambda: g_matris111(ax, kod, m),
         "pasta": lambda: g_pasta(ax, kod, rep), "kde": lambda: g_kde(ax, kod, m), "dbscan": lambda: g_dbscan(ax, kod, m),
         "rolling": lambda: g_rolling(ax, kod, m, r.get("Spearman ρ")),
         "regresyon": lambda: g_regresyon(ax, kod, m, r.get("Kübik R²")), "artik": lambda: g_artik(ax, kod, m)}
    return f[anahtar]()


# ================================================================== referans: makaledeki 189 tespit
def makale_189():
    src = open(os.path.join(os.path.dirname(o.BULMACA), "Alien_Puzzle_Project", "src", "yenigrafik49.py"), encoding="utf-8").read()
    from io import StringIO
    parcalar = []
    for ad in ("csv_1d_matches", "csv_10d_matches", "csv_100d_matches"):
        txt = re.search(ad + r' = """(.*?)"""', src, re.S).group(1)
        for a, b in (("2İNDİ-12-13", "2008-12-13"), ("2Oc06-09-24", "2006-09-24"), ("2GEÇ-12-13", "2008-12-13"), ("2GEÇ-09-24", "2006-09-24")):
            txt = txt.replace(a, b)
        parcalar.append(pd.read_csv(StringIO(txt)))
    d = pd.concat(parcalar).dropna(subset=["window"])
    d["day"] = pd.to_datetime(d["day"], errors="coerce")
    return d


# ================================================================== ana akış
if __name__ == "__main__":
    os.makedirs(CIKTI, exist_ok=True)
    ozet, sonuc = [], {}
    for kod in KODLAR:
        r, m, fis, db, rep = istatistik(kod)
        ozet.append(r); sonuc[kod] = (r, m, fis, db, rep)
        kl = os.path.join(CIKTI, "formuller", kod); os.makedirs(kl, exist_ok=True)
        klTR = os.path.join(os.path.join(KOK, "cache"), "tr_grafik", kod); os.makedirs(klTR, exist_ok=True)   # Türkçe çalışma grafikleri (teslim edilmez; İngilizceleri makale_grafikleri*.py)
        for dosya, baslik, anahtar in GRAFIKLER:
            fig, ax = plt.subplots(figsize=(11, 6) if anahtar not in ("pasta",) else (8, 8))
            im = ciz(anahtar, ax, kod, m, rep, r)
            if im is not None and anahtar in ("varlik10", "matris111"):
                fig.colorbar(im, ax=ax, label="AU")
            ax.set_title(f"{kod}: {YAZIM[kod]}\n{baslik}", fontsize=10)
            fig.tight_layout(); fig.savefig(os.path.join(klTR, dosya + ".png"), dpi=130); plt.close(fig)
        with pd.ExcelWriter(os.path.join(kl, f"{kod}_veri.xlsx")) as w:
            pd.DataFrame([r]).T.reset_index().rename(columns={"index": "Ölçüt", 0: "Değer"}).to_excel(w, "Özet", index=False)
            cols = [c for c in ["day", "window", "object_id", "au", "hedef", "sapma", "kume", "rm", "aykiri", "pred"] if c in m]
            m[cols].to_excel(w, "Tüm tespitler", index=False)
            rep.rename_axis("Cisim").reset_index(name="Tekrar").to_excel(w, "Tekrar sayıları", index=False)
            for k, v in fis.items():
                v.to_excel(w, f"Fisher {k} gün", index=False)
            if db is not None:
                db.to_excel(w, "DBSCAN kümeleri", index=False)
            h_all[h_all.formul == kod].to_excel(w, "Hedef Q(t)", index=False)
        print(f"{kod}: 1g={r['1 gün']} 10g={r['10 gün']} 100g={r['100 gün']} benzersiz={r['Benzersiz cisim']}", flush=True)
    ozet = pd.DataFrame(ozet)

    # karşılaştırma panelleri
    pk = os.path.join(KOK, "cache", "tr_paneller"); os.makedirs(pk, exist_ok=True)   # Türkçe çalışma panelleri
    for dosya, baslik, anahtar in GRAFIKLER:
        fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
        for ax, kod in zip(axs, KODLAR):
            r, m, fis, db, rep = sonuc[kod]
            ciz(anahtar, ax, kod, m, rep, r)
            if ax.get_legend():
                ax.get_legend().remove()
            if anahtar in ("dbscan", "rolling", "regresyon", "artik"):
                ax.xaxis.set_major_locator(mdates.YearLocator(20)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        for ax in axs[len(KODLAR):]:
            ax.axis("off")
        fig.suptitle(f"{baslik} — 22 eşitlik (gri çizgiler: formülün hedef mesafesi Q(t))", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.97]); fig.savefig(os.path.join(pk, f"panel_{dosya}.png"), dpi=90); plt.close(fig)

    # sağlama: Ref-makale ↔ makaledeki 189 tespit
    ref = makale_189()
    biz = sonuc["Ref-makale"][1]
    A = set(zip(ref.object_id, ref.day.dt.date)); B = set(zip(biz.object_id, biz.day.dt.date))
    saglama = pd.DataFrame([
        ["1 / 10 / 100 gün eşleşme", "1 / 23 / 165",
         f"{(biz.window==1).sum()} / {(biz.window==10).sum()} / {(biz.window==100).sum()}"],
        ["Toplam tespit / benzersiz cisim", "189 / 149", f"{len(biz)} / {biz.object_id.nunique()}"],
        ["Makaledeki tespitlerle ortak (cisim, gün)", len(A), len(A & B)],
        ["Yalnız makalede", "", "; ".join(f"{x} {d}" for x, d in sorted(A - B, key=str)[:10])],
        ["Yalnız yeni hesapta", "", "; ".join(f"{x} {d}" for x, d in sorted(B - A, key=str)[:10])],
        ["En sık cisim", "10199 Chariklo (13)", sonuc["Ref-makale"][0]["En sık 3 cisim"]],
        ["P-değeri", "≈ 0,0000376 (26 kat)", f"{sonuc['Ref-makale'][0]['P-değeri (n₁/N)']:.7f}"],
        ["Z (10 / 100 gün)", "−515,37 / −1630,01", f"{sonuc['Ref-makale'][0]['Z (10 gün)']:.2f} / {sonuc['Ref-makale'][0]['Z (100 gün)']:.2f}"],
        ["Fisher χ² (10 / 100 gün)", "42,57 / 270,06", f"{sonuc['Ref-makale'][0]['Fisher χ² (10 gün)']:.2f} / {sonuc['Ref-makale'][0]['Fisher χ² (100 gün)']:.2f}"],
        ["Medyan 1990 öncesi / sonrası", "12,22 / 13,22", f"{sonuc['Ref-makale'][0]['Medyan 1990 öncesi']:.2f} / {sonuc['Ref-makale'][0]['Medyan 1990 sonrası']:.2f}"],
        ["DBSCAN küme / gürültü", "2 küme (21, 155) / 13", f"{sonuc['Ref-makale'][0]['DBSCAN küme sayısı']} ({sonuc['Ref-makale'][0]['DBSCAN küme boyutları']}) / {sonuc['Ref-makale'][0]['DBSCAN gürültü']}"],
        ["2σ aykırı", "12", sonuc["Ref-makale"][0]["2σ aykırı sayısı"]],
        ["Spearman ρ", "0,48", f"{sonuc['Ref-makale'][0]['Spearman ρ']:.3f}"],
        ["Kübik R²", "0,746", f"{sonuc['Ref-makale'][0]['Kübik R²']:.3f}"],
    ], columns=["Ölçüt", "Makale", "Yeni hesap"])
    pd.to_pickle((ozet, saglama), os.path.join(KOK, "cache", "ozet.pkl"))
    print(saglama.to_string())
    pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 40)
    print(ozet.drop(columns=["Eşitlik", "Fisher sonuç (10 gün)", "Fisher sonuç (100 gün)"]).to_string())
