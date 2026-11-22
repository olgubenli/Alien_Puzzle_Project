# -*- coding: utf-8 -*-
"""Bölüm 3.1 (Hipotez 1) grafiklerinin 22 eşitlik için makaledeki / Supplementary'deki (İngilizce) biçimde yeniden çizimi.
Biçim yazarın orijinal kodlarından alındı (Alien_Puzzle_Project/src):
  Fig. 1 / S1  → yenigrafik49.plot_au_distribution             (violin + kutu, medyan ve bıyık değerleri, n etiketi)
  Fig. S2      → yenigrafik49.plot_au_stripplot                (pencere başına jitter saçılım)
  Fig. S3      → yenigrafik49.plot_presence_heatmap_10d_with_1d_inset
  Fig. S4      → yenigrafik49.plot_presence_matrix_111d_149obj (4 panel, AU renkli, O/D kodları)
  Fig. S5      → piegrafik18.py                                (1 / 10 / 100 gün tekrar pastaları)
  Fig. 2 / S6  → yenigrafik49.plot_au_density_by_epoch         (1990 öncesi / sonrası KDE + medyanlar)
  Fig. 3 / S7  → yenigrafik49.plot_dbscan_clustering_au_vs_time (eps = 0,3, min_samples = 5)
  Fig. S8      → yenigrafik49.plot_au_over_time_scatter        (30 noktalık hareketli ortalama, ±2σ bant, Spearman)
  Fig. S9/S10  → yenigrafik49.plot_regression_analysis_au_vs_time (3. derece polinom, artıklar)
Yazarın kodunda AU eksenleri makaledeki formüle göre (11–14 AU) sabitti; burada her formülün kendi veri aralığına göre,
makaledeki oranlarla ölçeklendi. Diğer bütün biçim ayrıntıları (renkler, boyutlar, yazı tipleri, başlıklar) aynıdır.
Veri: Ref-makale için yazarın kendi 189 tespiti (yenigrafik49.py; makaledeki şekillerin verisi), diğer formüller için
Excel taraması (cache/eslesmeler.pkl). Çıktı: cikti/formuller/<kod>/ (PNG 300 dpi + PDF)."""
import colorsys, math, os, re, sys, warnings
from concurrent.futures import ProcessPoolExecutor
from io import StringIO
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
from scipy.stats import spearmanr
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

warnings.filterwarnings("ignore")
KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
from tarama import KODLAR  # noqa: E402

FORM = os.path.join(KOK, "cikti", "formuller")
APP_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(KOK))), "Alien_Puzzle_Project", "src", "yenigrafik49.py")
RC = {"figure.dpi": 100, "savefig.dpi": 300, "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
      "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9}
ENG = {"Ref-makale": "6|E−Q| = 5|U−J|  (adopted reading; positive root only, as in the paper)",
       "Ref-mutlak": "6|E−Q| = 5|U−J|  (including the absolute value of the negative root)",
       "F1": "6+E+Q = U+J+5", "F1-mutlak": "|6+E+Q| = |U+J+5|", "F2": "(6+E+Q+U+J+5)/6 = 5", "F2-mutlak": "|(6+E+Q+U+J+5)/6| = 5",
       "F3": "(6+5)(Q−E) = U+J", "F3-mutlak": "(6+5)|Q−E| = U+J", "F4": "√(6×5) = (Q−E)/(U−J)", "F4-mutlak": "√(6×5) = |Q−E|/|U−J|",
       "F5": "Q×E = U+J", "F5-mutlak": "|Q×E| = U+J", "F6": "(U−6)+(E−5) = Q−J", "F6-mutlak": "|U−6|+|E−5| = |Q−J|",
       "F7": "(6×J)/(U−Q) = E/5", "F7-mutlak": "(6×J)/|U−Q| = E/5", "F8": "(U+6)/(Q−5) = E/J", "F8-mutlak": "(U+6)/|Q−5| = E/J",
       "F9": "(Q+U)/(J+6) = 5", "F9-mutlak": "|Q+U|/(J+6) = 5", "F10": "E×5 = (Q−U)/(J−6)", "F10-mutlak": "E×5 = |Q−U|/|J−6|"}
ADI = {"Ref-makale": "Ref"}
ESKI = ["fig1_violin.png", "fig2_kde_1990.png", "fig3_dbscan.png", "figS10_artiklar.png", "figS2_strip.png", "figS3_varlik_10g.png",
        "figS4_matris_111g.png", "figS5_pasta.png", "figS8_hareketli_ort.png", "figS9_regresyon.png"]
MAX10, MAXM, MAX_DB, MAX_ETIKET = 40, 300, 15000, 60


# ================================================================== veri
def yazar_189():
    src = open(APP_SRC, encoding="utf-8").read(); parca = []
    for ad in ("csv_1d_matches", "csv_10d_matches", "csv_100d_matches"):
        txt = re.search(ad + r' = """(.*?)"""', src, re.S).group(1)
        for a, b in (("2İNDİ-12-13", "2008-12-13"), ("2Oc06-09-24", "2006-09-24"), ("2GEÇ-12-13", "2008-12-13"), ("2GEÇ-09-24", "2006-09-24")):
            txt = txt.replace(a, b)
        parca.append(pd.read_csv(StringIO(txt)))
    d = pd.concat(parca).dropna(subset=["window"]).copy()
    d["day"] = pd.to_datetime(d["day"], errors="coerce")
    d["window"] = d["window"].astype(str).str.extract(r"(\d+)")[0].astype(int)
    return d[["object_id", "au", "day", "window"]]


def veri(kod):
    if kod == "Ref-makale":
        return yazar_189().sort_values(["window", "day"]).reset_index(drop=True)
    m = pd.read_pickle(os.path.join(KOK, "cache", "eslesmeler.pkl"))
    return m[m.formul == kod][["object_id", "au", "day", "window"]].sort_values(["window", "day"]).reset_index(drop=True)


def gunler():
    h = pd.read_pickle(os.path.join(KOK, "cache", "hedefler.pkl"))
    g = h[["day", "window"]].drop_duplicates().sort_values("day")
    return {w: list(g[g.window == w].day) for w in (1, 10, 100)}


# ================================================================== ortak yardımcılar
def adim(span, n=6):
    span = span if span > 0 else 1.0
    raw = span / n; mag = 10 ** math.floor(math.log10(raw))
    for k in (1, 2, 2.5, 5, 10):
        if raw <= k * mag:
            return k * mag
    return 10 * mag


def sinir(au, alt, ust):
    """Makaledeki oranlar: Fig. 1'de 11–14 AU (veri 11,71–13,74), Fig. S2'de 11–14,5 AU."""
    lo, hi = float(np.min(au)), float(np.max(au)); span = max(hi - lo, 1e-3)
    st = adim(span * 1.4)
    return math.floor((lo - alt * span) / st) * st, math.ceil((hi + ust * span) / st) * st, st


class Cizici:
    def __init__(self, kod, df, G):
        self.kod, self.df, self.G = kod, df, G
        self.kl = os.path.join(FORM, kod); os.makedirs(self.kl, exist_ok=True)
        self.etiket = f"{ADI.get(kod, kod).replace('-mutlak', '-abs')}:  {ENG[kod]}"
        self.not_ = "paper data, N = 189" if kod == "Ref-makale" else f"N = {len(df)}"
        self.rep = {w: df[df.window == w].object_id.value_counts() for w in (1, 10, 100)}
        self.tum = sorted(df.object_id.unique())

    def baslik(self, fig, y=1.0, fs=12):
        fig.suptitle(f"{self.etiket}    [111 epochs 1960–2025, ±1%; {self.not_}]", fontsize=fs, fontweight="bold", y=y)

    def kaydet(self, fig, ad):
        for u in ("png", "pdf"):
            fig.savefig(os.path.join(self.kl, f"{ad}.{u}"), dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    def bos(self, ad, ne, neden):
        fig, ax = plt.subplots(figsize=(10, 3)); ax.axis("off")
        ax.text(0.5, 0.5, f"{ne}\nnot applicable: {neden}", ha="center", va="center", fontsize=13)
        self.baslik(fig); self.kaydet(fig, ad)

    # ---------------------------------------------------------- Fig. 1 / S1
    def fig1(self):
        df = self.df; data = [df[df.window == w].au.values for w in (1, 10, 100)]
        fig = plt.figure(figsize=(7.2, 4.0)); ax = plt.gca()
        lo, hi, st = sinir(df.au, 0.25, 0.12); R = hi - lo
        vd = [(i, d) for i, d in enumerate(data, 1) if len(d) > 1 and np.ptp(d) > 0]
        if vd:
            parts = ax.violinplot([d for _, d in vd], positions=[i for i, _ in vd], showmeans=False, showmedians=False, showextrema=False)
            for pc in parts["bodies"]:
                pc.set_facecolor("#D0E4F5"); pc.set_edgecolor("grey"); pc.set_alpha(0.7)
        ax.boxplot([d for d in data if len(d) > 0], positions=[i for i, d in enumerate(data, 1) if len(d) > 0], widths=0.2,
                   showfliers=True, patch_artist=True, boxprops=dict(facecolor="white", alpha=0.9, zorder=2),
                   medianprops=dict(color="darkorange", linewidth=2, zorder=3), whiskerprops=dict(zorder=4), capprops=dict(zorder=4),
                   flierprops=dict(marker="o", markerfacecolor="grey", markeredgecolor="dimgrey", markersize=4, alpha=0.7, zorder=4))
        fs_w, dx = 6, 0.12
        if len(data[0]) == 1:
            ax.plot(1, data[0][0], "o", color="grey", markersize=5, zorder=5)
            ax.text(1 - dx, data[0][0], f"{data[0][0]:.2f}", ha="right", va="center", fontsize=fs_w, zorder=11)
        for pos, d in ((1, data[0]), (2, data[1]), (3, data[2])):
            if len(d) < 2:
                continue
            q1, q3 = np.percentile(d, [25, 75]); iqr = q3 - q1
            wmin = d[d >= q1 - 1.5 * iqr].min(); wmax = d[d <= q3 + 1.5 * iqr].max(); med = np.median(d)
            ax.text(pos, med + 0.0167 * R, f"{med:.2f}", ha="center", va="bottom", fontsize=8, fontweight="bold", zorder=11)
            ax.text(pos - dx, wmin, f"{wmin:.2f}", ha="right", va="center", fontsize=fs_w, zorder=11)
            ax.text(pos - dx, wmax, f"{wmax:.2f}", ha="right", va="center", fontsize=fs_w, zorder=11)
        ax.set_ylim(lo, hi); ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["1d", "10d", "100d"]); ax.set_ylabel("AU")
        for i, w in enumerate((1, 10, 100), 1):
            n = int((df.window == w).sum())
            if n:
                ax.text(i, hi - 0.033 * R, f"n={n}", ha="center", va="top", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.04, fs=9); self.kaydet(fig, "FigS1_Fig1_AU_Distribution_by_Window")

    # ---------------------------------------------------------- Fig. S2
    def figS2(self):
        df = self.df; fig = plt.figure(figsize=(7.2, 4.0)); ax = plt.gca()
        lo, hi, st = sinir(df.au, 0.25, 0.35); R = hi - lo
        xp = {1: 1, 10: 2, 100: 3}; col = {1: "#6baed6", 10: "#fdae6b", 100: "#74c476"}; rng = np.random.default_rng(0)
        for w in (1, 10, 100):
            v = df[df.window == w].au.values
            if not len(v):
                continue
            ax.scatter(rng.normal(xp[w], 0.10, len(v)), v, s=20, alpha=0.6, edgecolors="none", c=col[w], zorder=1)
            ax.text(xp[w], hi - 0.0143 * R, f"n={len(v)}", ha="center", va="top", fontsize=9)
        for x in (1.5, 2.5):
            ax.axvline(x, color="grey", linewidth=0.8, alpha=0.8)
        ax.set_xlim(0.5, 3.5); ax.set_ylim(lo, hi); ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["1d", "10d", "100d"]); ax.set_ylabel("AU")
        ax.set_yticks(np.arange(lo, hi + st * 0.2, st)); ax.grid(which="major", axis="y", linestyle="--", alpha=0.5, color="darkgrey")
        mn = st / 5; ax.yaxis.set_minor_locator(MultipleLocator(mn))
        for y in np.arange(lo + st, hi - st + 1e-9, mn):
            if not np.isclose((y - lo) / st, round((y - lo) / st)):
                ax.axhline(y, color="lightgrey", linestyle=":", alpha=0.7, linewidth=0.6, zorder=0)
        ax.tick_params(axis="y", which="both", direction="in", right=True); plt.tight_layout()
        self.baslik(fig, y=1.04, fs=9); self.kaydet(fig, "FigS2_AU_Scatter_by_Window")

    # ---------------------------------------------------------- Fig. S3
    def figS3(self):
        d10 = self.df[self.df.window == 10]; d1 = self.df[self.df.window == 1]
        if d10.empty:
            return self.bos("FigS3_Presence_Matrix_10d_1d_Inset", "Fig. S3 (presence matrix 10d)", "no detections in the 10-day window")

        def shade(c, tot, rk):
            if tot <= 1:
                return c
            r, g, b, a = to_rgba(c); h, s, v = colorsys.rgb_to_hsv(r, g, b)
            v = np.clip(v * (1.0 - 0.5 * rk / (tot - 1)), 0, 1); r, g, b = colorsys.hsv_to_rgb(h, s, v); return (r, g, b, a)
        rep = self.rep[10]; nall = len(rep); objs = list(rep.index[:MAX10]); n = len(objs)
        oi = {o: i for i, o in enumerate(objs)}; cmap = plt.get_cmap("Spectral", max(n, 2)); base = {o: cmap(i) for i, o in enumerate(objs)}
        days = list(self.G[10]); di = {d: j for j, d in enumerate(days)}; nd = len(days)
        s = d10.sort_values(["object_id", "day"]).copy(); s["rk"] = s.groupby("object_id").cumcount(); tot = s.groupby("object_id").size().to_dict()
        # yazarın iç grafiği sol üstte (gün 1–4, nesnelerin üst yarısı); orada tespit varsa şeklin sağına alınır
        disari = any((di.get(r.day, 99) <= 3) and (oi.get(r.object_id, -1) >= 0.45 * n) for r in s.itertuples())
        fig, ax = plt.subplots(figsize=(8.5 + (3.0 if disari else 0), max(5, 0.19 * n + 0.8))); ax.set_facecolor("#ffffff")
        ax.set_yticks(range(n)); ax.set_yticklabels(objs, fontsize=7 if n <= 30 else 6)
        ax.set_xticks(range(nd)); ax.set_xticklabels([pd.Timestamp(d).strftime("%Y-%m-%d") for d in days], rotation=90, fontsize=8)
        ax.set_xlim(-0.5, nd - 0.5); ax.set_ylim(-0.65, n - 0.35)
        ax.set_xlabel("Date"); ax.set_ylabel("Object Name")
        ax.set_title("Presence Matrix 10d" + (f" ({n} most frequent of {nall} objects)" if nall > n else ""))
        ax.set_xticks(np.arange(-.5, nd - 0.5, 1), minor=True); ax.set_yticks(np.arange(-.5, n - 0.5, 1), minor=True)
        ax.grid(which="minor", color="#d9d9d9", linestyle="-", linewidth=1.5, zorder=10); ax.grid(which="major", visible=False)
        ax.tick_params(which="minor", bottom=False, left=False)
        for sp in ax.spines.values():
            sp.set_zorder(20)
        for r in s.itertuples():
            if r.object_id in oi and r.day in di:
                i, j = oi[r.object_id], di[r.day]
                ax.add_patch(plt.Rectangle((j - 0.4, i - 0.45), 0.8, 0.9, facecolor=shade(base[r.object_id], tot[r.object_id], r.rk),
                                           alpha=0.85, linewidth=0, zorder=5))
        ins = ax.inset_axes([1.03, 0.45, 0.30, 0.50] if disari else [0.02, 0.455, 0.38, 0.49])
        ins.set_zorder(30); ins.set_facecolor("#ffffff"); ins.set_xticks([]); ins.set_yticks([])
        for sp in ins.spines.values():
            sp.set_edgecolor("black"); sp.set_linewidth(1.5); sp.set_zorder(20)
        o1 = list(self.rep[1].index)
        if len(o1) == 1:   # yazarın tek cisimli düzeni (dikey isim, altta tarih, kesikli kılavuzlar)
            pip = plt.get_cmap("hot")(0.5); bb = [-0.3, 9.5, 3.5, 20.5]; sx = 0.2
            ins.set_xlim(bb[0], bb[2]); ins.set_ylim(bb[1], bb[3])
            ins.text(1.0 + sx, 19.8, "Presence Matrix 1d", fontsize=8, ha="center", va="top", zorder=25)
            ins.set_xticks(np.arange(np.ceil(bb[0] - 0.5) + 0.5, bb[2] + 1e-9, 1), minor=True); ins.set_yticks(np.arange(bb[1], bb[3] + 1e-9, 1), minor=True)
            for xg in np.arange(np.ceil(bb[0] - 0.5) + 0.5, bb[2] + 1e-9, 1):
                ins.plot([xg, xg], [bb[1], bb[3]], color="#bdbdbd", lw=1.5, zorder=10.5, scalex=False, scaley=False)
            for yg in np.arange(bb[1], bb[3] + 1e-9, 1):
                ins.plot([bb[0], bb[2]], [yg, yg], color="#bdbdbd", lw=1.5, zorder=10.5, scalex=False, scaley=False)
            ins.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
            cx, cy = 1.5 + sx, 14.5
            ins.text(0.0 + sx, cy, o1[0], ha="center", va="center", rotation=90, fontsize=6, zorder=15)
            ins.text(cx, 10.5, pd.Timestamp(self.G[1][0]).strftime("%Y-%m-%d"), ha="center", va="center", fontsize=6, zorder=15)
            ins.add_patch(plt.Rectangle((cx - 0.475, cy - 0.45), 0.95, 0.9, facecolor=pip, alpha=0.85, linewidth=0, zorder=12))
            ins.plot([sx + 0.1, cx], [cy, cy], color="black", lw=1.0, ls="--", zorder=11)
            ins.plot([cx, cx], [10.8, cy], color="black", lw=1.0, ls="--", zorder=11)
        elif o1:   # birden fazla cisim: tek sütunlu küçük matris, isimler hücrelerin sağında
            k = min(len(o1), 6); pip = plt.get_cmap("hot")(0.5)
            ins.set_xlim(0, 6); ins.set_ylim(-0.7, k + 1.4)
            ins.text(3.0, k + 1.2, "Presence Matrix 1d", fontsize=8, ha="center", va="top")
            for i_ in range(k + 1):
                ins.plot([0.3, 1.5], [i_, i_], color="#bdbdbd", lw=1.5, zorder=10.5)
            for xg in (0.3, 1.5):
                ins.plot([xg, xg], [0, k], color="#bdbdbd", lw=1.5, zorder=10.5)
            for i_, o_ in enumerate(o1[:k]):
                yc = k - i_ - 0.5
                ins.add_patch(plt.Rectangle((0.42, yc - 0.45), 0.96, 0.9, facecolor=pip, alpha=0.85, linewidth=0, zorder=12))
                ins.text(1.65, yc, o_, ha="left", va="center", fontsize=6 if k <= 4 else 5, zorder=15)
            ins.text(0.9, -0.38, pd.Timestamp(self.G[1][0]).strftime("%Y-%m-%d"), ha="center", va="center", fontsize=6)
            if len(o1) > k:
                ins.text(3.8, -0.38, f"(+{len(o1) - k} more objects)", ha="center", va="center", fontsize=6)
        else:
            ins.text(0.5, 0.5, "Presence Matrix 1d\n(no match on the Wow! epoch)", ha="center", va="center", fontsize=7, transform=ins.transAxes)
        self.baslik(fig, y=1.02, fs=10); self.kaydet(fig, "FigS3_Presence_Matrix_10d_1d_Inset")

    # ---------------------------------------------------------- Fig. S4 (+ Tablo S1/S2 kodları)
    def figS4(self):
        df = self.df; tum = self.tum; nall = len(tum)
        if nall > MAXM:
            ust = set(df.object_id.value_counts().index[:MAXM]); objs = [o for o in tum if o in ust]
        else:
            objs = tum
        days = sorted(set(self.G[1]) | set(self.G[10]) | set(self.G[100])); nd = len(days)
        oc = [f"O{i+1}" for i in range(len(objs))]; dc = [f"D{j+1}" for j in range(nd)]
        oi = {o: i for i, o in enumerate(objs)}; di = {d: j for j, d in enumerate(days)}
        with pd.ExcelWriter(os.path.join(self.kl, "TableS1_S2_Day_and_Object_Codes.xlsx")) as w:
            pd.DataFrame({"Day Code": dc, "Date": [pd.Timestamp(d).date() for d in days],
                          "Window": ["1d" if d in self.G[1] else ("10d" if d in self.G[10] else "100d") for d in days]}).to_excel(w, sheet_name="Table S1 Day codes", index=False)
            pd.DataFrame({"Object Code": oc, "Object Name": objs, "Detections": [int((df.object_id == o).sum()) for o in objs]}).to_excel(w, sheet_name="Table S2 Object codes", index=False)
        no = len(objs); isp = no // 2; jsp = (nd + 1) // 2
        lo, hi = df.au.min(), df.au.max(); sm = cm.ScalarMappable(norm=mcolors.Normalize(vmin=lo, vmax=hi), cmap=plt.get_cmap("turbo"))
        olc = max(1.0, no / 149)
        fig = plt.figure(figsize=(18, 11.7 * olc))
        gs = fig.add_gridspec(2, 2, left=0.05, right=0.90, bottom=0.05, top=0.92 if olc == 1 else 0.95, wspace=0.1, hspace=0.15 / olc)
        ek = f" ({no} most frequent of {nall})" if nall > no else ""
        fig.suptitle(f"Presence Matrix (Master {nd}d x {no}obj{ek}) - Color by AU [{lo:.2f} - {hi:.2f}]", fontsize=16, y=0.965 if olc == 1 else 0.972)
        P = {}
        for ad, (r_, c_) in {"A": (0, 0), "C": (0, 1), "B": (1, 0), "D": (1, 1)}.items():
            ax = fig.add_subplot(gs[r_, c_]); P[ad] = ax
            ol = oc[:isp] if r_ == 0 else oc[isp:]; dl = dc[:jsp] if c_ == 0 else dc[jsp:]
            ax.set_facecolor("#ffffff"); ax.set_yticks(range(len(ol))); ax.set_yticklabels(ol, fontsize=5)
            xi = np.arange(0, len(dl), 5); ax.set_xticks(xi); ax.set_xticklabels([dl[i] for i in xi], fontsize=5, rotation=90)
            ax.set_xlim(-0.5, len(dl) - 0.5); ax.set_ylim(-0.5, len(ol) - 0.5); ax.invert_yaxis()
            ax.set_xlabel("Day Code"); ax.set_ylabel("Object Code")
            o0 = 1 if r_ == 0 else isp + 1; o1 = isp if r_ == 0 else no; d0 = 1 if c_ == 0 else jsp + 1; d1 = jsp if c_ == 0 else nd
            ax.set_title(f"Panel {ad}: Objects O{o0}-O{o1} (N={len(ol)}), Days D{d0}-D{d1} (N={len(dl)})", fontsize=10)
            ax.set_xticks(np.arange(-.5, len(dl) - 0.5, 1), minor=True); ax.set_yticks(np.arange(-.5, len(ol) - 0.5, 1), minor=True)
            ax.grid(which="minor", color="#d9d9d9", linestyle="-", linewidth=0.3, zorder=10); ax.grid(which="major", visible=False)
            ax.tick_params(which="both", length=0)
            for sp in ax.spines.values():
                sp.set_zorder(20)
        for r in df.sort_values(["object_id", "day"]).itertuples():
            if r.object_id in oi and r.day in di:
                i, j = oi[r.object_id], di[r.day]
                ax = P[("A" if j < jsp else "C") if i < isp else ("B" if j < jsp else "D")]
                ax.add_patch(plt.Rectangle(((j if j < jsp else j - jsp) - 0.5, (i if i < isp else i - isp) - 0.5), 1, 1,
                                           facecolor=sm.to_rgba(r.au), alpha=0.9, edgecolor="none", linewidth=0, zorder=5))
        cb = fig.colorbar(sm, cax=fig.add_axes([0.92, 0.15, 0.02, 0.7])); cb.set_label("AU Values", rotation=270, labelpad=20, fontsize=12)
        fig.text(0.5, 0.995, f"{self.etiket}    [{self.not_}]", ha="center", va="top", fontsize=12, fontweight="bold")
        for u in ("png", "pdf"):
            fig.savefig(os.path.join(self.kl, f"FigS4_Presence_Matrix_Master_111d.{u}"), dpi=300 if olc == 1 else 200, facecolor="white")
        plt.close(fig)

    # ---------------------------------------------------------- Fig. S5 (piegrafik18.py)
    def figS5(self):
        fig, axs = plt.subplots(1, 3, figsize=(18, 6)); fig.patch.set_facecolor("white")
        acik = ["#D4E6F1", "#E6F5E0", "#F4ECF7"]; koyu = ["#A9CCE3", "#AED581", "#C39BD3"]
        for ax, w, a, k in zip(axs, (1, 10, 100), acik, koyu):
            rep = self.rep[w]
            if rep.empty:
                ax.axis("off"); ax.text(0.5, 0.5, f"No detections\n(n = {w} day{'s' if w > 1 else ''})", ha="center", va="center", fontsize=11); continue
            top = rep[rep > 2].head(5); diger3 = rep[rep > 2].iloc[5:].sum()
            r2 = rep[rep == 2].sum(); r1 = rep[rep == 1].sum()
            if w == 1 and len(rep) <= 3:
                vals, labs = list(rep.values), list(rep.index); cols = [a] * len(vals); exp = [0] * len(vals)
            else:
                vals = list(top.values) + ([diger3] if diger3 else []) + ([r2] if r2 else []) + ([r1] if r1 else [])
                labs = ([o.split(" (")[0] for o in top.index] + (["Other objects (≥3x)"] if diger3 else []) +
                        (["Repeated 2x"] if r2 else []) + (["Repeated 1x" if w == 100 else "Others (1 repeat)"] if r1 else []))
                if w == 10 and len(rep[rep > 1]) == 1 and len(vals) >= 2:   # yazarın 10 gün pastası: tekrar eden cisim + diğerleri
                    vals = [int(rep[rep > 1].sum()), r1]; labs = [rep[rep > 1].index[0].split(" (")[0], "Others (1 repeat)"]
                ncok = len(vals) - (1 if r1 else 0)
                cols = [k] * max(ncok - (1 if r2 else 0), 0) + (["#E8DAEF" if w == 100 else k] if r2 else []) + ([a] if r1 else [])
                cols = cols[:len(vals)]; exp = [0.1] * (len(vals) - 1) + [0.05 if w == 100 else 0]
            wd, tx, at = ax.pie(vals, autopct="%1.1f%%", startangle=90, colors=cols, explode=exp, labels=labs,
                                pctdistance=0.72 if len(vals) > 2 else 0.6, labeldistance=1.05, rotatelabels=len(vals) > 1,
                                wedgeprops={"edgecolor": "white", "linewidth": 1.5})
            for t_, a_ in zip(tx, at):
                t_.set_fontsize(9 if len(vals) > 3 else 10); a_.set_fontsize(8 if len(vals) > 3 else 9)
            if len(vals) >= 1:   # en büyük dilimin etiketi dilimin içine (yazarın düzenlemesi)
                b = int(np.argmax(vals)); tx[b].set_position((0, -0.15 if len(vals) > 1 else 0)); tx[b].set_rotation(0); tx[b].set_ha("center")
                at[b].set_position((0, -0.35 if len(vals) > 1 else -0.15)); at[b].set_rotation(0)
        fig.tight_layout(rect=[0.05, 0.15, 0.95, 0.88])
        for x, t in ((0.20, "n = 1 day"), (0.506, "n = 10 days"), (0.812, "n = 100 days")):
            fig.text(x, 0.12, t, ha="center", fontsize=12)
        fig.text(0.5, 0.97, f"{self.etiket}    [{self.not_}]", ha="center", va="top", fontsize=12, fontweight="bold")
        for u in ("png", "pdf"):
            fig.savefig(os.path.join(self.kl, f"FigS5_Repetition_Frequency_Pies.{u}"), dpi=300, facecolor="white")
        plt.close(fig)

    # ---------------------------------------------------------- Fig. 2 / S6
    def fig2(self, split=1990):
        df = self.df; sd = pd.Timestamp(f"{split}-01-01"); a = df.au; pre = df[df.day < sd].au; post = df[df.day >= sd].au
        fig, ax = plt.subplots(figsize=(10, 6))
        span = max(a.max() - a.min(), 1e-3); lo, hi = a.min() - 0.10 * span, a.max() + 0.13 * span
        ax.hist(a, bins=np.linspace(lo, hi, 50), density=True, color="grey", alpha=0.25, label="Overall Histogram (All Data)")

        def kde(s, **kw):
            if len(s) > 1 and s.nunique() > 1:
                s.plot.kde(ax=ax, **kw)
            else:
                ax.plot([], [], **{k: v for k, v in kw.items() if k != "label"}, label=kw["label"] + " – too few points")
        kde(a, color="black", linestyle="--", linewidth=2, label=f"Overall KDE (N={len(a)})")
        kde(pre, color="#0072B2", linewidth=3, label=f"Pre-{split} KDE (N={len(pre)})")
        kde(post, color="#D55E00", linewidth=3, label=f"Post-{split} KDE (N={len(post)})")
        if len(pre):
            ax.axvline(pre.median(), color="#0072B2", linestyle=":", linewidth=2, label=f"Median (Pre-{split}): {pre.median():.2f} AU")
        if len(post):
            ax.axvline(post.median(), color="#D55E00", linestyle=":", linewidth=2, label=f"Median (Post-{split}): {post.median():.2f} AU")
        ax.set_title(f"AU Distribution Density by Epoch (Split @ {split})", fontsize=14)
        ax.set_xlabel("AU Value"); ax.set_ylabel("Density (Kernel Density Estimate)"); ax.set_xlim(lo, hi)
        ax.legend(fontsize=9); ax.grid(True, linestyle=":", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.03, fs=11); self.kaydet(fig, "FigS6_Fig2_AU_Density_by_Epoch_1990")

    # ---------------------------------------------------------- Fig. 3 / S7
    def fig3(self, eps=0.3, ms=5):
        d = self.df.sort_values("day").copy()
        if len(d) < ms:
            return self.bos("FigS7_Fig3_DBSCAN_Clusters", "Fig. 3 / S7 (DBSCAN)", f"only {len(d)} detections")
        X = StandardScaler().fit_transform(np.c_[d.day.map(pd.Timestamp.toordinal), d.au]); ek = ""
        if len(d) > MAX_DB:
            from sklearn.neighbors import KNeighborsClassifier
            ix = np.random.default_rng(0).choice(len(d), MAX_DB, replace=False)
            ls = DBSCAN(eps=eps, min_samples=ms).fit_predict(X[ix])
            lab = KNeighborsClassifier(1).fit(X[ix], ls).predict(X); lab[ix] = ls
            ek = f"\n(clustered on a fixed-seed sample of {MAX_DB:,} points; remaining points take the label of the nearest sampled point)"
        else:
            lab = DBSCAN(eps=eps, min_samples=ms).fit_predict(X)
        renk = {0: "#E41A1C", 1: "#4DAF4A", 2: "#377EB8", 3: "#984EA3"}; ek_renk = plt.get_cmap("tab20")
        fig, ax = plt.subplots(figsize=(15, 7)); hs = []
        for k in sorted(set(lab), key=lambda x: (x == -1, x)):
            xy = d[lab == k]
            if k == -1:
                hs.append(ax.scatter(xy.day, xy.au, s=50, c="black", marker="x", label=f"Noise / Outlier (N={len(xy)})", zorder=10))
            else:
                hs.append(ax.scatter(xy.day, xy.au, s=30, alpha=0.8, c=[renk.get(k, ek_renk((k - 4) % 20))], edgecolor="black", linewidth=0.5,
                                     label=f"Cluster {k + 1} (N={len(xy)})", zorder=5))
        ax.set_title(f"DBSCAN Clustering Analysis (Time vs. AU) (eps={eps}, min_samples={ms}){ek}", fontsize=14)
        ax.set_xlabel("Date"); ax.set_ylabel("AU Value")
        ax.legend(handles=hs, title="Detected Groups", fontsize=9 if len(hs) < 12 else 7, ncol=1 if len(hs) < 12 else 2)
        ax.grid(True, linestyle=":", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.03 if not ek else 1.06, fs=12); self.kaydet(fig, "FigS7_Fig3_DBSCAN_Clusters")

    # ---------------------------------------------------------- Fig. S8
    def figS8(self):
        d = self.df.sort_values("day", kind="mergesort").copy()
        if len(d) < 3:
            return self.bos("FigS8_AU_vs_Time_Rolling_Mean_Outliers", "Fig. S8 (rolling mean)", f"only {len(d)} detections")
        d["rm"] = d.au.rolling(30, min_periods=1, center=True).mean(); d["res"] = d.au - d.rm; thr = 2.0 * d.res.std()
        d["out"] = d.res.abs() > thr; rho, pv = spearmanr(d.day.map(pd.Timestamp.toordinal), d.au)
        code = {o: f"O{i+1}" for i, o in enumerate(self.tum)}
        norm = mcolors.Normalize(vmin=d.au.min(), vmax=d.au.max()); cmap = plt.get_cmap("turbo")
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.fill_between(d.day, d.rm - thr, d.rm + thr, color="grey", alpha=0.2, zorder=1)
        mk = {1: "o", 10: "s", 100: "^"}; sz = {1: 100, 10: 40, 100: 40}; lb = {1: "1d Window", 10: "10d Window", 100: "100d Window"}; hs = []; sc = None
        for w in (100, 10, 1):
            dw = d[d.window == w]
            if dw.empty:
                continue
            sc = ax.scatter(dw.day, dw.au, c=dw.au, cmap=cmap, norm=norm, marker=mk[w], s=sz[w], alpha=0.8, edgecolor="black", linewidth=0.5, zorder=5)
            hs.append(Line2D([0], [0], marker=mk[w], color="w", label=f"{lb[w]} (N={len(dw)})", markerfacecolor="grey", markeredgecolor="black", markersize=8))
        ln, = ax.plot(d.day, d.rm, color="red", linestyle="--", linewidth=2.5, label="30-Point Rolling Mean (All Data)", zorder=10); hs.append(ln)
        o = d[d.out]
        ax.scatter(o.day, o.au, marker="x", s=60, c="black", linewidth=1.5, zorder=7)
        if len(o) <= MAX_ETIKET:
            for r in o.itertuples():
                ax.text(r.day, r.au, f" {code[r.object_id]}", fontsize=7, ha="left", va="center_baseline", fontweight="bold", zorder=8)
        cb = fig.colorbar(sc, ax=ax, orientation="vertical", pad=0.01); cb.set_label("AU Value")
        hs.append(Patch(facecolor="grey", alpha=0.3, label="Normal Range (±2σ)"))
        hs.append(Line2D([0], [0], marker="x", color="w", label=f"Outlier (> 2σ) (N={len(o)})", markerfacecolor="black", markeredgecolor="black", markersize=7))
        ax.legend(handles=hs, title="Detection Source", fontsize=9, loc="lower right")
        ax.text(0.02, 0.98, f"Spearman's $\\rho$ = {rho:.2f}\n" + ("p < 0.001" if pv < 0.001 else f"p = {pv:.3f}"), transform=ax.transAxes, fontsize=9,
                va="top", ha="left", bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="black"))
        ax.set_xlabel("Date"); ax.set_ylabel("AU Value")
        ax.set_title(f"All Detections (N={len(d)}) by Date and AU (with 2$\\sigma$ Outlier Analysis)" + (" — outlier labels omitted (too many)" if len(o) > MAX_ETIKET else ""), fontsize=14)
        ax.grid(True, linestyle=":", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.03, fs=12); self.kaydet(fig, "FigS8_AU_vs_Time_Rolling_Mean_Outliers")

    # ---------------------------------------------------------- Fig. S9 / S10
    def figS9_S10(self, deg=3):
        d = self.df.sort_values("day", kind="mergesort").copy()
        if len(d) < 5 or d.day.nunique() < 4:
            for ad, ne in (("FigS9_Polynomial_Regression_Deg3", "Fig. S9"), ("FigS10_Regression_Residuals", "Fig. S10")):
                self.bos(ad, ne, f"only {len(d)} detections on {d.day.nunique()} epochs")
            return
        y = d.au.values; X = d.day.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
        mod = make_pipeline(PolynomialFeatures(degree=deg, include_bias=False), LinearRegression()).fit(X, y)
        yp = mod.predict(X); res = y - yp; r2 = r2_score(y, yp)
        Xs = np.linspace(X.min(), X.max(), 500).reshape(-1, 1); ys = mod.predict(Xs); Xd = [pd.Timestamp.fromordinal(int(v)) for v in Xs.ravel()]
        d["rm"] = d.au.rolling(30, min_periods=1, center=True).mean()
        fig, ax = plt.subplots(figsize=(15, 7))
        sc = ax.scatter(d.day, y, c=y, cmap="turbo", norm=mcolors.Normalize(vmin=y.min(), vmax=y.max()), alpha=0.6, s=30, zorder=5,
                        label=f"Actual Detections (N={len(d)})")
        fig.colorbar(sc, ax=ax, label="AU Value")
        ax.plot(d.day, d.rm, color="red", linestyle="--", linewidth=2.5, label="30-Point Rolling Mean (Data-Driven)", zorder=10)
        ax.plot(Xd, ys, color="blue", linestyle="-", linewidth=3.0, label=f"{deg}-Deg. Polynomial Fit (Model-Driven)", zorder=11)
        ax.text(0.02, 0.98, f"$R^2 = {r2:.3f}$", transform=ax.transAxes, fontsize=12, va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor="black"))
        ax.set_title(f"Polynomial Regression Fit (Degree={deg}) vs. Rolling Mean", fontsize=14); ax.set_xlabel("Date"); ax.set_ylabel("AU Value")
        ax.legend(); ax.grid(True, linestyle=":", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.03, fs=12); self.kaydet(fig, "FigS9_Polynomial_Regression_Deg3")
        fig, ax = plt.subplots(figsize=(15, 5)); m = np.abs(res).max() or 1
        sc = ax.scatter(d.day, res, c=res, cmap="coolwarm", vmin=-m, vmax=m, alpha=0.8, s=30, label="Residuals (Actual - Predicted)")
        fig.colorbar(sc, ax=ax, label="Residual Value (AU)")
        ax.axhline(0, color="black", linestyle="--", linewidth=1.5, label="Zero Error (Model Prediction)")
        ax.set_title(f"Residuals of {deg}-Degree Polynomial Model vs. Time", fontsize=14); ax.set_xlabel("Date")
        ax.set_ylabel("Residual (Actual AU - Predicted AU)"); ax.legend(); ax.grid(True, linestyle=":", alpha=0.7); plt.tight_layout()
        self.baslik(fig, y=1.04, fs=12); self.kaydet(fig, "FigS10_Regression_Residuals")


def calistir(kod):
    plt.rcParams.update(RC)
    df = veri(kod); c = Cizici(kod, df, gunler())
    for f in (c.fig1, c.figS2, c.figS3, c.figS4, c.figS5, c.fig2, c.fig3, c.figS8, c.figS9_S10):
        try:
            f()
        except Exception as ex:   # bir şekil hata verirse diğerleri yine üretilsin
            plt.close("all"); print(f"  {kod} {f.__name__}: HATA {ex}", flush=True)
    for e in ESKI:
        p = os.path.join(c.kl, e)
        if os.path.exists(p):
            os.remove(p)
    return f"{kod}: {len(df)} tespit"


if __name__ == "__main__":
    secim = sys.argv[1:] or list(KODLAR)
    with ProcessPoolExecutor(min(6, len(secim))) as ex:
        for s in ex.map(calistir, secim):
            print(s, flush=True)
