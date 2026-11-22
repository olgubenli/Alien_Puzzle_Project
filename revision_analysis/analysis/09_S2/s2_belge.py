# -*- coding: utf-8 -*-
"""Supplementary Material S2 — alternatif okumalar ve 1.000 rastgele okuma (İngilizce; .md / .docx / .pdf).
Veri kaynakları (yeniden hesap yok, kayıtlı sonuçlar okunur):
  07_profil/cache/kapi_tj.pkl   — A/B/C sayımı (Tj kapı kuralı), 20 alternatif + 1.000 rastgele (kapi_tj.py)
  04_111gun/cikti/04_111gun_karsilastirma.xlsx — Wow! günü eşleşme sayıları ve cisimleri (İş 4)
  05_h2/cache/ozet.pkl + <kod>.npz — H2 eşleşme sayısı, Top 8, sapma aralığı, boşluk sırası (İş 5)
  uzaylı bulmaca/faz3_sonuclar/faz3_ham.csv, faz3_formuller.py — rastgele okumalar (Faz 3)"""
import json, os, re, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

KOK = os.path.dirname(os.path.abspath(__file__)); ANALIZ = os.path.dirname(KOK)
sys.path.insert(0, ANALIZ); sys.path.insert(0, os.path.join(ANALIZ, "05_h2"))
import ortak as o  # noqa: E402
import h2  # noqa: E402

CIKTI = os.path.join(KOK, "cikti"); FIG = os.path.join(CIKTI, "figures"); os.makedirs(FIG, exist_ok=True)
AD = "Supplementary_Material_S2"
RED, GREY = "#D62728", "#7F7F7F"

# ------------------------------------------------------------------ veri
K = pd.read_pickle(os.path.join(ANALIZ, "07_profil", "cache", "kapi_tj.pkl"))
ALT, HAM, SON = K["alt"].copy(), K["ham"], K["sonuc"]
oz, _ = pd.read_pickle(os.path.join(ANALIZ, "05_h2", "cache", "ozet.pkl"))
es = pd.read_excel(os.path.join(ANALIZ, "04_111gun", "cikti", "04_111gun_karsilastirma.xlsx"), "Eşleşme sayıları")
es["Formül"] = es.Formül.replace({"Ref-makale": "Ref"})
WOWOBJ = dict(zip(es.Formül, es["Wow! günü cisim(ler)i"]))
LABEL = {k: ("Adopted" if k == "Ref" else k.replace("-mutlak", "-abs")) for k in h2.KODLAR}
EQ = {k: v.replace("(makale)", "").strip() for k, v in h2.YAZIM.items()}

ELEM = {}
for f, anah in ((os.path.join(o.BULMACA, "faz2_sonuclar", "cache", "sbdb_elemanlar.json"), "tj"),
                (os.path.join(os.path.dirname(o.BULMACA), "Alien_Puzzle_Project", "data", "genisletilmis_asteroid_db2.json"), "T_J")):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        try:
            ELEM[k] = {"a": float(v["a"]), "e": float(v["e"]), "Tj": float(v[anah])}
        except Exception:
            pass


def kapi_adayi(isim):
    e = ELEM.get(isim)
    if e is None or not re.match(r"^\d+ ", isim) or re.match(r"^\d+[PDI]/", isim):
        return False
    return e["e"] < 1 and e["a"] <= 5.5


def kisa(n):
    """'55701 Ukalegon (1193 T-3)' → '55701 Ukalegon'"""
    return re.sub(r"\s*\(.*\)$", "", str(n)).strip()


def wow_obj(k):
    s = str(WOWOBJ.get(k, "—"))
    n = ALT.loc[ALT.Formül == k, "Wow! günü eşleşme"].iloc[0]
    if n == 0:
        return "—"
    if n == 1:
        return kisa(s)
    return f"{n} objects"


DUP = {}
for _, r in oz.iterrows():
    m = re.match(r"(\S+) ile aynı sonuç", str(r.get("Not", "")))
    if m:
        DUP[r.Formül] = m.group(1)

# ------------------------------------------------------------------ Table S2.1 (21 okuma)
rows = []
for _, r in ALT.iterrows():
    k = r.Formül; z = oz[oz.Formül == k].iloc[0]
    kap = ", ".join(kisa(x) for x in (r["ana kapı"], r["ara kapı"]) if x) or "—"
    rows.append({"Reading": LABEL[k], "Equation": EQ[k],
                 "Wow!-epoch matches (H1)": int(r["Wow! günü eşleşme"]), "H1 object(s)": wow_obj(k),
                 "H2 matches (±1.5%)": f"{int(z['Eşleşme (±%1,5)']):,}",
                 "Top 8 deviation range (%)": z["Top 8 sapma aralığı (%)"].replace("–", "–"),
                 "Largest-gap rank": int(r["Boşluk sırası"]),
                 "Top 8 gateways (T_J < 3)": kap,
                 "A": "✓" if r.A else "✗", "B": "✓" if r.B else "✗", "C": "✓" if r.C_Tj else "✗",
                 "Criteria met": int(r["Şart sayısı (C_Tj)"]),
                 "Note": (f"H2 identical to {LABEL[DUP[k]]}" if k in DUP else "")})
T1 = pd.DataFrame(rows)

# ------------------------------------------------------------------ figürler
plt.rcdefaults()
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "savefig.dpi": 300})
kod = list(ALT.Formül); x = np.arange(len(kod)); xl = [LABEL[k] for k in kod]


def kaydet(fig, ad):
    for u in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{ad}.{u}"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return os.path.join(FIG, f"{ad}.png")


# Fig. S2.1 — A
n1 = ALT["Wow! günü eşleşme"].values
fig, ax = plt.subplots(figsize=(14, 5.5))
cols = [RED if k == "Ref" else ("#1F77B4" if v == 1 else "#AEC7E8") for k, v in zip(kod, n1)]
ax.bar(x, np.where(n1 == 0, 0.6, n1), color=cols, edgecolor="black", linewidth=0.5)
ax.set_yscale("log"); ax.axhline(1, color="black", ls="--", lw=1)
for xi, v in zip(x, n1):
    ax.text(xi, max(v, 0.6) * 1.15, str(v), ha="center", va="bottom", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(xl, rotation=60, ha="right")
ax.set_ylabel("Matches on 1977-08-15 within ±1% (log scale)"); ax.set_ylim(0.5, 20000)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=RED), plt.Rectangle((0, 0), 1, 1, color="#1F77B4"),
                   plt.Rectangle((0, 0), 1, 1, color="#AEC7E8"), Line2D([], [], color="black", ls="--")],
          labels=["Adopted reading (6EQ=5UJ)", "Alternative with a single match (criterion A met)",
                  "Alternative with 0 or ≥2 matches", "Single match"], loc="upper right", fontsize=9)
ax.grid(axis="y", which="both", ls=":", alpha=0.5)
F1 = kaydet(fig, "FigS2_1_criterion_A_wow_epoch_matches")

# Fig. S2.2 — B
gr = ALT["Boşluk sırası"].values
fig, ax = plt.subplots(figsize=(14, 5))
ax.axhline(8, color=RED, ls="--", lw=1.2, label="Rank 8 (criterion B)")
ax.scatter(x, gr, s=70, c=[RED if (k == "Ref") else ("#1F77B4" if g == 8 else GREY) for k, g in zip(kod, gr)],
           edgecolor="black", zorder=3)
for xi, g in zip(x, gr):
    ax.text(xi, g + 0.8, str(g), ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(xl, rotation=60, ha="right"); ax.set_ylim(0, 33)
ax.set_ylabel("Rank after which the largest\ndeviation gap occurs (ranks 1–31)")
ax.legend(loc="upper left", fontsize=9); ax.grid(axis="y", ls=":", alpha=0.5)
F2 = kaydet(fig, "FigS2_2_criterion_B_largest_gap_rank")
# Fig. S2.2b — elbow zoom-in (Fig. 4 formatı), sayfa başına 6 okuma, büyük yazı
import seaborn as sns  # noqa: E402
G_SPEC = [("red", "--"), ("orange", ":"), ("green", "--"), ("blue", ":"), ("purple", "--"), ("brown", ":")]


def elbow(ax, k):
    dv = np.load(os.path.join(ANALIZ, "05_h2", "cache", f"{k}.npz"))["dv"]
    N = len(dv); n = min(48, N)
    sns.kdeplot(pd.Series(dv), fill=True, ax=ax, color="lightblue", cut=0)
    for j in range(n):
        c, s_ = G_SPEC[j // 8]; ax.axvline(dv[j], color=c, linestyle=s_, linewidth=1.1)
    zoom = dv[n - 1] * 1.2 if dv[n - 1] > 0 else 1e-6
    ax.set_xlim(0, zoom); ax.set_xlabel("Percentage Difference (Applied Formula Matched)", fontsize=10)
    ax.set_ylabel("Density", fontsize=10); ax.tick_params(labelsize=9)
    # Fig. 4'teki gibi: 90° döndürülmüş ondalık etiketler + Grup 1 (kırmızı) ve Grup 2 (turuncu) ilk değerleri
    ozel = [(dv[0], "red")] + ([(dv[8], "orange")] if N > 8 else [])
    oto = [t for t in ax.get_xticks() if 0 <= t <= zoom and all(abs(t - v) > zoom * 0.04 for v, _ in ozel)]
    if dv[0] > zoom * 0.025 and 0.0 not in oto:         # makaledeki gibi eksen başında 0 (kırmızıya çok yakın değilse)
        oto.append(0.0)
    tk = sorted(oto + [v for v, _ in ozel])
    dec = max(5, int(-np.floor(np.log10(zoom))) + 2)
    ax.set_xticks(tk); ax.set_xticklabels([f"{t:.{dec}f}" for t in tk], rotation=90, fontsize=8)
    for lbl, t in zip(ax.get_xticklabels(), tk):
        for v, c in ozel:
            if t == v:
                lbl.set_color(c); lbl.set_fontweight("bold")
    ax.set_xlim(0, zoom)
    kk = min(32, N); m = int(np.diff(dv[:kk]).argmax())
    ax.text(0.98, 0.97, f"Largest gap (ranks 1–{kk}):\nbetween rank {m + 1} and {m + 2}", transform=ax.transAxes,
            ha="right", va="top", fontsize=10, color=RED if m + 1 == 8 else "black",
            bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=0.95))
    ax.set_title(f"{LABEL[k]}: {EQ[k]}   (N = {N:,})", fontsize=11)


F2b = []
gruplar = [kod[i:i + 6] for i in range(0, len(kod), 6)]
for gi, grp in enumerate(gruplar, 1):
    plt.rcdefaults(); sns.set_theme(style="ticks")
    nr = int(np.ceil(len(grp) / 2))
    fig, axs = plt.subplots(nr, 2, figsize=(14, 5.2 * nr)); axs = np.atleast_1d(axs).ravel()
    for ax, k in zip(axs, grp):
        elbow(ax, k)
    for ax in axs[len(grp):]:
        ax.axis("off")
    hand = [Line2D([], [], color=c, ls=s_, lw=1.5) for c, s_ in G_SPEC]
    lab = [f"Group {i + 1} ({'Top 8' if i == 0 else 'Next 8'})" for i in range(6)]
    if len(grp) % 2:
        axs[-1].legend(hand, lab, loc="center", fontsize=13, title="Ranks 1–48", title_fontsize=13)
    else:
        fig.legend(hand, lab, loc="lower center", ncol=6, fontsize=10, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=[0, 0.03 if len(grp) % 2 == 0 else 0, 1, 1])
    F2b.append(kaydet(fig, f"FigS2_2b_elbow_zoom_part{gi}"))
    plt.rcdefaults(); plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "savefig.dpi": 300})

# Fig. S2.3 — C (Top 8 cisimlerinin Tj değerleri)
fig, ax = plt.subplots(figsize=(14, 6.5))
for xi, k in zip(x, kod):
    ix = np.load(os.path.join(ANALIZ, "05_h2", "cache", f"{k}.npz"))["ix"][:8]
    tek = sorted(set(h2.Qn[ix[:, 0]]) | set(h2.Un[ix[:, 1]]) | set(h2.Jn[ix[:, 2]]))
    r = ALT[ALT.Formül == k].iloc[0]; kap = {r["ana kapı"], r["ara kapı"]} - {""}
    for j, n in enumerate(tek):
        e = ELEM.get(n)
        if not e or not np.isfinite(e["Tj"]):
            continue
        tj = float(np.clip(e["Tj"], 1.5, 4.5))
        tro, hil = 5.05 <= e["a"] <= 5.35, 3.7 <= e["a"] <= 4.2
        aday = kapi_adayi(n)
        m = "^" if tro else ("s" if hil else "o")
        c = RED if n in kap else ("#1F77B4" if aday and e["Tj"] < 3 else ("white" if not aday else "#BBBBBB"))
        ax.scatter(xi + (j % 5 - 2) * 0.07, tj, marker=m, s=46 if n in kap else 26, c=c, edgecolor="black",
                   linewidth=0.6 if n in kap else 0.4, zorder=3 if n in kap else 2)
ax.axhline(3, color="black", ls="--", lw=1); ax.text(len(kod) - 0.4, 3.03, r"$T_J$ = 3", ha="right", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(xl, rotation=60, ha="right"); ax.set_ylim(1.4, 4.6)
ax.set_ylabel("Tisserand parameter $T_J$ of Top 8 objects\n(clipped to 1.5–4.5)")
ax.legend(handles=[Line2D([], [], marker="^", ls="", mfc=RED, mec="black", ms=9, label="Selected gateway: Jupiter Trojan"),
                   Line2D([], [], marker="s", ls="", mfc=RED, mec="black", ms=8, label="Selected gateway: Hilda"),
                   Line2D([], [], marker="o", ls="", mfc=RED, mec="black", ms=8, label="Selected gateway: other"),
                   Line2D([], [], marker="o", ls="", mfc="#1F77B4", mec="black", ms=7, label="Stable asteroid, $T_J$ < 3 (not selected)"),
                   Line2D([], [], marker="o", ls="", mfc="#BBBBBB", mec="black", ms=7, label="Stable asteroid, $T_J$ ≥ 3"),
                   Line2D([], [], marker="o", ls="", mfc="white", mec="black", ms=7, label="Not a gateway candidate (comet, Centaur, planet …)")],
          loc="upper left", fontsize=8.5, ncol=2)
ax.grid(axis="y", ls=":", alpha=0.5)
F3 = kaydet(fig, "FigS2_3_criterion_C_top8_tisserand")

# Fig. S2.4 — 1.000 rastgele okuma
R = HAM[HAM.id != "YAZAR"]; Y = HAM[HAM.id == "YAZAR"].iloc[0]
fig, axs = plt.subplots(1, 3, figsize=(18, 5.8)); axs = np.array([[axs[0], axs[1]], [axs[2], None]], dtype=object)
# (a) Wow! günü eşleşme sayısı
bins = [(0, 0, "0"), (1, 1, "1"), (2, 2, "2"), (3, 5, "3–5"), (6, 20, "6–20"), (21, 100, "21–100"), (101, 10 ** 9, ">100")]
c_ = [int(((R["H1 Wow"] >= a) & (R["H1 Wow"] <= b)).sum()) for a, b, _ in bins]
ax = axs[0, 0]; ax.bar(range(len(bins)), c_, color=[RED if l == "1" else "#1F77B4" for *_, l in bins], edgecolor="black")
for i, v in enumerate(c_):
    ax.text(i, v + 8, str(v), ha="center", fontsize=9)
ax.set_xticks(range(len(bins))); ax.set_xticklabels([l for *_, l in bins])
ax.set_xlabel("Matches on 1977-08-15 (Hypothesis 1, ±1%)"); ax.set_ylabel("Random readings")
ax.set_title("(a) Criterion A — adopted reading: 1 match (red bin)")
# (b) boşluk sırası
G = R[R.güvenilir]["boşluk sırası"].dropna().astype(int)
cnt = G.value_counts().reindex(range(1, 32), fill_value=0)
ax = axs[0, 1]; ax.bar(cnt.index, cnt.values, color=[RED if i == 8 else "#1F77B4" for i in cnt.index], edgecolor="black", linewidth=0.4)
ax.set_xlabel("Rank after which the largest deviation gap occurs"); ax.set_ylabel("Random readings")
ax.set_title(f"(b) Criterion B — adopted reading: rank 8 (red); n = {len(G)}")
# (c) kapılar
v = {"Main Trojan gateway +\nsecond gateway ($T_J$ < 3)": int(R.C_Tj.sum()),
     "… second gateway\nis a Hilda (strict)": int(R.C_Tj_H.sum()),
     "Trojan + Hilda by\nsemi-major axis only": int(R.C_eski.sum())}
ax = axs[1, 0]; ax.bar(range(3), list(v.values()), color="#1F77B4", edgecolor="black")
for i, w in enumerate(v.values()):
    ax.text(i, w + 3, f"{w} ({w / 10:.1f}%)", ha="center", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels(list(v.keys()), fontsize=9); ax.set_ylabel("Random readings (of 1,000)")
ax.set_title("(c) Criterion C — gateways in the top octet (adopted reading: all three)")
# (d) ortak sayım → Fig. S2.0'a taşındı (07_profil Joint Features)
s = SON["Tüm 1.000"]["C_Tj"]
for a_ in [a for a in axs.ravel() if a is not None]:
    a_.grid(axis="y", ls=":", alpha=0.5)
fig.tight_layout()
F4 = kaydet(fig, "FigS2_4_random_readings_distributions")

# ------------------------------------------------------------------ tablolar S2.2–S2.4
T2 = []
for alt_ad, tanim in (("Tüm 1.000", "All 1,000"), ("H2 güvenilir", "Reliable H2 profile (581)")):
    for c, cad in (("C_Tj", "Main Trojan + second gateway, T_J < 3 (as in the main text)"),
                   ("C_Tj_H", "… second gateway is a Hilda (strict)"), ("C_eski", "Trojan + Hilda by semi-major axis only")):
        s = SON[alt_ad][c]
        T2.append({"Sample": tanim, "Definition of C": cad, "A": s["A"], "B": s["B"], "C": s["C"], "A+B": s["A+B"],
                   "A+C": s["A+C"], "B+C": s["B+C"], "A+B+C": s["A+B+C"]})
T2 = pd.DataFrame(T2)
iki = R[((R.A & R.B) | (R.A & R.C_Tj) | (R.B & R.C_Tj))].copy()
T3 = pd.DataFrame({"ID": iki.id, "Random reading": iki.formül.str.replace("abs", "|·|"),
                   "Wow!-epoch matches": iki["H1 Wow"].astype(int),
                   "Largest-gap rank": iki["boşluk sırası"].apply(lambda v: "—" if pd.isna(v) else int(v)),
                   "Gateways (main / second)": [" / ".join(kisa(a) for a in (p, q) if a) or "—" for p, q in zip(iki["ana kapı"], iki["ara kapı"])],
                   "Criteria": ["+".join(c for c, f in (("A", a), ("B", b), ("C", cc)) if f) for a, b, cc in zip(iki.A, iki.B, iki.C_Tj)]})
d3 = pd.read_csv(os.path.join(o.BULMACA, "faz3_sonuclar", "faz3_ham.csv"))
th = d3[(d3.h1_thereus == True) & (d3["h1_1977-08-15"] == 1)]
T4 = pd.DataFrame({"ID": th.id.replace({"YAZAR": "Adopted"}), "Reading": th.formul.str.replace("abs", "|·|"),
                   "Deviation of 32532 Thereus (%)": th.h1_en_iyi_sapma.round(3)})

# ------------------------------------------------------------------ makaledeki istatistikler: 21 okuma (İş 4–6 kayıtları) + 1.000 okuma
from scipy import stats as _st
KR = {d: {a: _st.chi2.ppf(1 - a, d) for a in (0.01, 0.001)} for d in (20, 200)}
x4 = os.path.join(ANALIZ, "04_111gun", "cikti", "04_111gun_karsilastirma.xlsx")
I4 = pd.read_excel(x4, "İstatistik testleri").set_index("Formül").rename(index={"Ref-makale": "Ref"})
Z4 = pd.read_excel(x4, "Zaman yapısı").set_index("Formül").rename(index={"Ref-makale": "Ref"})
O5 = oz.set_index("Formül")
O6 = pd.read_pickle(os.path.join(ANALIZ, "06_h3", "cache", "h3_sonuc.pkl"))[0].set_index("Formül")


def fis(v, d):
    if not np.isfinite(v):
        return "undefined"
    return f"{v:.1f} ({'✓' if v > KR[d][0.01] else '✗'}/{'✓' if v > KR[d][0.001] else '✗'})"


T5, T6 = [], []
for k in kod:
    i4, z4, o5 = I4.loc[k], Z4.loc[k], O5.loc[k]
    o6 = O6.loc[k] if k in O6.index else O6.loc[DUP[k]]
    T5.append({"Reading": LABEL[k], "P (1 day)": f"{i4['P-değeri (n₁/N)']:.2e}",
               "Z (10 d)": f"{i4['Z (10 gün)']:.1f}", "Z (100 d)": f"{i4['Z (100 gün)']:.1f}",
               "Fisher χ² 10 d (0.01/0.001)": fis(i4["Fisher χ² (10 gün)"], 20),
               "Fisher χ² 100 d (0.01/0.001)": fis(i4["Fisher χ² (100 gün)"], 200),
               "S/N (10 d / 100 d)": f"{i4['SNR (10 gün)']:.2f} / {i4['SNR (100 gün)']:.2f}",
               "Median shift post–pre 1990 (AU)": f"{z4['Medyan farkı (sonrası − öncesi)']:+.2f}",
               "DBSCAN clusters / noise": f"{int(z4['DBSCAN küme sayısı'])} / {int(z4['DBSCAN gürültü'])}",
               "Spearman ρ": f"{z4['Spearman ρ']:.2f}", "Cubic R²": f"{z4['Kübik R²']:.2f}"})
    ana = str(o6["Ana kapı"]); ara = str(o6["Ara kapı"])
    T6.append({"Reading": LABEL[k], "H2 matches": f"{int(o5['Eşleşme (±%1,5)']):,}",
               "Top 8 range (%)": o5["Top 8 sapma aralığı (%)"],
               "Method A P = 8/N": f"{o5['Method A P = 8/N']:.2e}", "Method A Z": f"{o5['Method A Z (p₀=0,5)']:.1f}",
               "Method B Z": f"{o5['Method B Z (p₀=0,5)']:.1f}", "H0 rejected (P < 0.001)": "✓" if o5["Method A P = 8/N"] < 0.001 else "✗",
               "Main / second gateway": (kisa(ana) if not ana.startswith("Yok") else "—") + " / " + (kisa(ara) if not ara.startswith("Yok") else "—"),
               "Cheapest route to Thereus (FT)": str(o6.get("Thereus: en ucuz rota (FT)", "—")).replace(" — ", ": ").replace("nan", "—"),
               "Lowest-EFF route to Thereus": str(o6.get("Thereus: en 'verimli' rota (EFF)", "—")).split(" (FT")[0].replace(" — ", ": ").replace("nan", "—")})
T5, T6 = pd.DataFrame(T5), pd.DataFrame(T6)

# 1.000 rastgele okuma: kayıtlı Faz 3 sayılarından (yeni tarama yok)
GUN10 = ["1965-03-15", "1973-11-29", "1981-09-01", "1988-06-23", "1994-01-10", "1999-08-14", "2005-02-28", "2010-12-05", "2016-04-19", "2022-07-22"]
D3 = d3[d3.id != "YAZAR"].copy(); NPOOL = 26576; ZK = _st.norm.ppf(1 - 0.001 / 2)
n1 = D3["h1_1977-08-15"].values; K10 = D3[[f"h1_{g}" for g in GUN10]].values
P1 = np.where(n1 > 0, n1 / NPOOL, np.nan)
nn = 10 * NPOOL; ph = K10.sum(1) / nn; Z10 = (ph - 0.5) / np.sqrt(0.25 / nn)
chi = np.full(len(D3), np.nan)
for i_, (lam, ks) in enumerate(zip(n1, K10)):
    if lam > 0:
        p = np.array([_st.poisson.sf(k_ - 1, lam) if k_ > 0 else 1.0 for k_ in ks]); chi[i_] = -2 * np.log(np.clip(p, 1e-300, 1)).sum()
NH2 = D3.h2_n_esik.values.astype(float)
with np.errstate(all="ignore"):
    PA = np.where(NH2 >= 8, 8 / NH2, np.nan); ZA = (PA - 0.5) / np.sqrt(0.25 / NH2)
    nB = NH2 / 8; ZB = (1 / nB - 0.5) / np.sqrt(0.25 / nB); ZB = np.where(NH2 >= 8, ZB, np.nan)
REJ = [("P (1 day) < 0.001", P1 < 0.001, np.isfinite(P1)),
       ("|Z| (10 d) > 3.29", np.abs(Z10) > ZK, np.isfinite(Z10)),
       ("Fisher 10 d, α = 0.01", chi > KR[20][0.01], np.isfinite(chi)),
       ("Fisher 10 d, α = 0.001", chi > KR[20][0.001], np.isfinite(chi)),
       ("Method A: P = 8/N < 0.001", PA < 0.001, np.isfinite(PA)),
       ("Method A: |Z| > 3.29", np.abs(ZA) > ZK, np.isfinite(ZA)),
       ("Method B: |Z| > 3.29", np.abs(ZB) > ZK, np.isfinite(ZB))]
T7 = pd.DataFrame([{"Test (as in the main text)": a, "Readings where defined": int(dfn.sum()),
                    "H0 rejected": int((r_ & dfn).sum()), "Share rejected": f"{(r_ & dfn).sum() / max(dfn.sum(), 1):.1%}"}
                   for a, r_, dfn in REJ])
fig, ax = plt.subplots(figsize=(13, 5.5))
sh = [(r_ & dfn).sum() / max(dfn.sum(), 1) * 100 for _, r_, dfn in REJ]
bb = ax.bar(range(len(REJ)), sh, color=["#1F77B4"] * len(REJ), edgecolor="black")
for i_, (v_, (_, r_, dfn)) in enumerate(zip(sh, REJ)):
    ax.text(i_, v_ + 1.5, f"{v_:.1f}%\n(n = {int(dfn.sum())})", ha="center", fontsize=9)
ax.set_xticks(range(len(REJ))); ax.set_xticklabels([a for a, *_ in REJ], rotation=20, ha="right", fontsize=10)
ax.set_ylabel("Random readings for which H0 is rejected (%)"); ax.set_ylim(0, 115); ax.grid(axis="y", ls=":", alpha=0.5)
F5 = kaydet(fig, "FigS2_5_main_text_tests_on_random_readings")

# ================================================================== GENİŞLETME (30 Ekim 2026) — yalnız kayıtlı sonuçlar
import shutil, sqlite3  # noqa: E402
# Tablo S2.0 — rastgele okumalardan örnek + tam liste (xlsx)
FJ = json.load(open(os.path.join(o.BULMACA, "faz3_sonuclar", "formuller.json"), encoding="utf-8"))
def okunur(sol, sag):
    return f"{sol} = {sag}".replace("abs", "|·|").replace("*", "×").replace("/", "÷")
TALL = pd.DataFrame([{"ID": "Adopted" if f["id"] == "YAZAR" else f["id"], "Reading": okunur(f["sol"], f["sag"])} for f in FJ])
T0 = TALL[TALL.ID != "Adopted"].head(10).reset_index(drop=True)

# Fig. S2.0 — A/B/C ortak sayım (07_profil, makaledeki Tj kuralı)
F0 = os.path.join(FIG, "FigS2_0_joint_features_ABC.png")
for u in ("png", "pdf"):
    shutil.copy(os.path.join(ANALIZ, "07_profil", "cikti", f"Joint_Features_ABC_Random_and_Alternative_Readings.{u}"),
                os.path.join(FIG, f"FigS2_0_joint_features_ABC.{u}"))
# Fig. S2.6 — 1990 kayması, 21 okuma; Fig. 2 biçiminde, sayfa başına 6 okuma (Fig. S2.2b gibi)
M4 = pd.read_pickle(os.path.join(ANALIZ, "04_111gun", "cache", "eslesmeler.pkl"))
sys.path.insert(0, os.path.join(ANALIZ, "04_111gun"))
from makale_grafikleri_h1 import yazar_189  # noqa: E402  (benimsenen okuma: makaledeki 189 tespit)
D189 = yazar_189()
def kde1990(ax, k):
    d = D189 if k == "Ref" else M4[M4.formul == k]
    a = d.au; sd = pd.Timestamp("1990-01-01"); pre, post = d[d.day < sd].au, d[d.day >= sd].au
    span = max(a.max() - a.min(), 1e-3); lo, hi = a.min() - 0.10 * span, a.max() + 0.13 * span
    ax.hist(a, bins=np.linspace(lo, hi, 50), density=True, color="grey", alpha=0.25, label="Histogram (all)")
    for ser, kw in ((a, dict(color="black", linestyle="--", linewidth=1.8, label=f"All (N={len(a)})")),
                    (pre, dict(color="#0072B2", linewidth=2.6, label=f"Pre-1990 (N={len(pre)})")),
                    (post, dict(color="#D55E00", linewidth=2.6, label=f"Post-1990 (N={len(post)})"))):
        if len(ser) > 1 and ser.nunique() > 1:
            ser.plot.kde(ax=ax, **kw)
        else:
            ax.plot([], [], **kw)
    if len(pre):
        ax.axvline(pre.median(), color="#0072B2", ls=":", lw=2, label=f"Median pre: {pre.median():.2f} AU")
    if len(post):
        ax.axvline(post.median(), color="#D55E00", ls=":", lw=2, label=f"Median post: {post.median():.2f} AU")
    ax.set_xlim(lo, hi); ax.set_xlabel("AU Value", fontsize=10); ax.set_ylabel("Density (KDE)", fontsize=10)
    ax.tick_params(labelsize=9); ax.grid(True, ls=":", alpha=0.7); ax.legend(fontsize=8, loc="upper left")
    ax.set_title(f"{LABEL[k]}: {EQ[k]}" + ("   (data of the main text)" if k == "Ref" else ""), fontsize=11)
F6 = []
for gi, grp in enumerate([kod[i:i + 6] for i in range(0, len(kod), 6)], 1):
    plt.rcdefaults(); plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "savefig.dpi": 300})
    nr = int(np.ceil(len(grp) / 2))
    fig, axs = plt.subplots(nr, 2, figsize=(14, 5.2 * nr)); axs = np.atleast_1d(axs).ravel()
    for ax, k in zip(axs, grp):
        kde1990(ax, k)
    for ax in axs[len(grp):]:
        ax.axis("off")
    fig.tight_layout()
    F6.append(kaydet(fig, f"FigS2_6_shift_1990_part{gi}"))
plt.rcdefaults(); plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "savefig.dpi": 300})
for eski in ("FigS2_6_shift_1990_all_readings.png",):
    if os.path.exists(os.path.join(FIG, eski)):
        os.remove(os.path.join(FIG, eski))
# Fig. S2.8 — Thereus pencereleri (08)
F8 = os.path.join(FIG, "FigS2_8_thereus_recurrence_1950_2100.png")
for u in ("png", "pdf"):
    shutil.copy(os.path.join(ANALIZ, "08_thereus_tarihleri", f"thereus_pencereleri.{u}"), os.path.join(FIG, f"FigS2_8_thereus_recurrence_1950_2100.{u}"))

# S2.5 — Q(t) değerleri (08/gunluk.csv)
GQ = pd.read_csv(os.path.join(ANALIZ, "08_thereus_tarihleri", "gunluk.csv"), parse_dates=["t"]).set_index("t")
QV = {d: float(GQ.loc[d, "Qhedef"]) for d in ("1960-07-11", "1977-08-15", "2010-12-05")}
W_ = GQ.loc["1950":"2025"]; U_MIN, U_MAX = W_.U.idxmin(), W_.U.idxmax()
Q6025 = GQ.loc["1960-07-01":"2025-09-30"].Qhedef

# S2.6 — Tablo S2.8 (H2 düzgün dağılım) ve S2.9 (Grup A)
r5 = O5.loc["Ref"]
T8 = pd.DataFrame([
    ("H2 matches within ±1.5% (N)", f"{int(r5['Eşleşme (±%1,5)']):,}", "—"),
    ("Mean deviation (%)", f"{r5['Ortalama sapma (%)']:.3f}", "0.750 (uniform on 0–1.5%)"),
    ("Kolmogorov–Smirnov test against uniform (p)", f"{r5['KS testi p (düzgün 0–1,5)']:.2f}", "—"),
    ("Group boundaries of Fig. S11 (%)", r5["S11 kesimler (%)"].replace(" / ", " / "), r5["S11 kesimler, düzgün dağılım beklentisi (%)"] + " (uniform quantiles)"),
    ("Deviation of rank 8 (%)", r5["Top 8 sapma aralığı (%)"].split("–")[-1].strip() + " (0.000778 in the main text)", "≈ 12/N under uniformity"),
    ("Matches with deviation ≤ rank-8 value", "8", f"{r5['Ek: ≤ 8. sapma, beklenen sayı']:.1f} expected under uniformity"),
    ("Methods A and B", f"P = 8/N = {r5['Method A P = 8/N'] * 1e4:.2f} × 10⁻⁴", "depends only on N"),
    ("Largest gap among the first 31 ranks", f"after rank {int(r5['En büyük boşluğun yeri (… sıradan sonra)'])}", "criterion B"),
], columns=["Quantity (adopted reading, Hypothesis 2)", "Value", "Reference / expectation"])
SINIF = {"Jüpiter Truvası (1:1)": "Jupiter Trojan (1:1)", "Hilda (3:2) / dış kuşak": "Hilda (3:2) / outer belt", "Ana kuşak": "Main belt",
         "Gezegen": "Planet", "Kentaur / dış": "Centaur / outer", "Kuyruklu yıldız": "Comet"}
S11 = SON6 = pd.read_pickle(os.path.join(ANALIZ, "06_h3", "cache", "h3_sonuc.pkl"))[1]["Ref"]["S11"].copy()
S11["Cisim"] = S11["Cisim"].replace({"399 Earth": "399 Earth (reference)"})
T9 = pd.DataFrame({"Object": [kisa(c) if "Earth" not in c else c for c in S11.Cisim], "a (AU)": S11["a (AU)"].round(3),
                   "e": S11.e.round(3), "i (°)": S11["i (°)"].round(2), "T_J": S11.Tj.round(3),
                   "Class": S11["Sınıf"].map(lambda s_: SINIF.get(s_, s_))})
GA = S11[~S11.Cisim.str.contains("Earth")]
O6R = O6.loc["Ref"]
GA_OZ = {"n": len(GA), "e_med": GA.e.median(), "e_lt": int((GA.e < 0.02).sum()), "i_med": GA["i (°)"].median(),
         "i_lt20": int((GA["i (°)"] < 20).sum()), "tj_min": GA.Tj.min(), "tj_max": GA.Tj.max(), "tj_med": GA.Tj.median(),
         "tj_lt3": int((GA.Tj < 3).sum()), "p1": O6R["Ek: rastgele grupta ≥1 Tj<3 asteroit olasılığı"],
         "p2": O6R["Ek: rastgele grupta ≥ gözlenen sayı olasılığı"]}

# S2.7 — Tablo S2.10 (yazarın maliyet matrisi) ve S2.11 (Thereus rotaları)
CM = pd.read_sql("select * from CostMatrix", sqlite3.connect(os.path.join(os.path.dirname(o.BULMACA), "Alien_Puzzle_Project", "data", "uzayli_bulmacasi_matrixson.db")))
def cm(a, b):
    v = CM[CM.From_Asteroid.str.startswith(a) & CM.To_Asteroid.str.startswith(b)].Cost
    return float(v.iloc[0])
c1, c2, c3 = cm("399", "3763 "), cm("3763 ", "15025 "), cm("15025 ", "55701 ")
d_uk, uk_th, q1, q2, d_jc, d_th = cm("399", "55701 "), cm("55701 ", "32532 "), cm("399", "755 "), cm("755 ", "84011 "), cm("399", "84011 "), cm("399", "32532 ")
T10 = pd.DataFrame([
    ("Earth → 3763 Qianxuesen", f"{c1:.2f}"), ("3763 Qianxuesen → 15025 Uwontario", f"{c2:.2f}"), ("15025 Uwontario → 55701 Ukalegon", f"{c3:.2f}"),
    ("Main route, total (Earth → 55701 Ukalegon)", f"{c1 + c2 + c3:.2f}"), ("Direct transfer Earth → 55701 Ukalegon", f"{d_uk:.2f}"),
    ("55701 Ukalegon → 32532 Thereus", f"{uk_th:.2f}"), ("Route 5, total to 32532 Thereus", f"{c1 + c2 + c3 + uk_th:.2f}"),
    ("Earth → 755 Quintilla → 84011 Jean-Claude", f"{q1:.2f} + {q2:.2f} = {q1 + q2:.2f}"), ("Direct transfer Earth → 84011 Jean-Claude", f"{d_jc:.2f}"),
    ("Direct transfer Earth → 32532 Thereus", f"{d_th:.2f}")], columns=["Connection", "Cost (CU)"])
S15 = pd.read_pickle(os.path.join(ANALIZ, "06_h3", "cache", "h3_sonuc.pkl"))[1]["Ref"]["S15"]
S15 = S15[S15["Hedef türü"] == "Thereus"]
MAK = {"25869 Jacoby": (1, 220.88, 22.23, 9.94), "5254 Ulysses": (2, 298.12, 21.81, 13.67), "84011 Jean-Claude": (3, 221.214, 22.67, 9.76),
       "306001 Joanllaneras": (4, 220.95, 21.27, 10.39), "55701 Ukalegon": (5, 233.12, 26.29, 8.87), "169509 Jeffreyrobbins": (6, 221.31, 18.00, 12.29)}
r11 = []
for _, rw in S15.iterrows():
    g = kisa(rw["Kapı"]); no, ft, mtm, eff = MAK[g]
    mn, mx = [float(v) for v in rw["MT min–max (alternatifler)"].split("–")]; en, ex = [float(v) for v in rw["EFF min–max (alternatifler)"].split("–")]
    parca = rw["Rota"].split(" → ")
    r11.append({"Route": no, "Gateway (first match; T_J)": parca[-2].replace(")", f"; {rw['Kapı Tj']:.3f})"),
                "Intermediate stop(s) (first match)": " → ".join(parca[1:-2]),
                "FT": f"{rw['FT (toplam maliyet)']:.2f}", "MT (AU)": f"{mtm:.2f}", "EFF": f"{eff:.2f}",
                "Equal-cost single-stop routes": int(rw["Eşit maliyetli tek duraklı alternatif sayısı"]),
                "EFF range of these routes": f"{en:.2f} – {ex:.2f}", "_ft": rw["FT (toplam maliyet)"], "_mt": (mn, mx), "_p": (mtm, eff)})
T11 = pd.DataFrame(r11).sort_values("Route").reset_index(drop=True)
# Fig. S2.7 — EFF – MT (EFF = FT/MT; eşit maliyetli seçenekler aynı FT ile hiperbol üzerinde)
fig, ax = plt.subplots(figsize=(12, 6.5)); cm_ = plt.get_cmap("tab10")
for i_, rw in T11.iterrows():
    mn, mx = rw["_mt"]; xs_ = np.linspace(min(mn, rw["_p"][0]), max(mx, rw["_p"][0]), 100)
    ax.plot(xs_, rw["_ft"] / xs_, color=cm_(i_), lw=2, alpha=0.55)
    ax.plot([mn, mx], [rw["_ft"] / mn, rw["_ft"] / mx], "|", color=cm_(i_), ms=14, mew=2)
    ax.scatter(*rw["_p"], s=110, color=cm_(i_), edgecolor="black", zorder=5, label=f"Route {rw['Route']}: {rw['Gateway (first match; T_J)'].split(' (')[0]} (FT {float(rw['FT']):.2f})")
    ax.annotate(f"R{rw['Route']}", rw["_p"], xytext=(6, 6), textcoords="offset points", fontsize=10, fontweight="bold")
ax.set_xlabel("MT: physical route length on 1977-08-15 (AU)"); ax.set_ylabel("EFF = FT / MT")
ax.set_title("Efficiency score versus route length for the routes to 32532 Thereus (adopted reading)", fontsize=13)
ax.grid(True, ls=":", alpha=0.7); ax.legend(fontsize=9, loc="upper right")
F7 = kaydet(fig, "FigS2_7_eff_vs_route_length")

# S2.8 — Tablo S2.12 (Thereus pencereleri)
PW = pd.read_csv(os.path.join(ANALIZ, "08_thereus_tarihleri", "pencereler.csv"), parse_dates=["bas", "son", "en_iyi_gun"])
T12 = pd.DataFrame({"Window": range(1, len(PW) + 1),
                    "From": [("≤ " if i == 0 else "") + f"{d:%d %b %Y}" + (" (start of data)" if i == 0 else "") for i, d in enumerate(PW.bas)],
                    "To": [f"{d:%d %b %Y}" for d in PW.son], "Days": PW.gun.astype(int),
                    "Closest match": [f"{d:%d %b %Y}" for d in PW.en_iyi_gun], "Deviation (%)": [f"{v:.4f}" for v in PW.en_iyi]})

# S2.9 — Tablo S2.13 (ana metin değerlerinin yeniden hesaplanması; 10_dogrulama)
DV = json.load(open(os.path.join(ANALIZ, "10_dogrulama", "cikti", "dogrulama_sonuc.json"), encoding="utf-8"))
f100 = DV["H1.Fisher_100"]
T13 = pd.DataFrame([
    ("Matches in the 1-, 10- and 100-day windows; detections / unique bodies", "1 / 23 / 165; 189 / 149", "same", "Reproduced"),
    ("P-value (1 day); Z-scores (10 d / 100 d)", "≈ 3.76 × 10⁻⁵; −515.37 / −1630.01", f"{DV['H1.P'] * 1e5:.2f} × 10⁻⁵; −{abs(DV['H1.Z_10']):.2f} / −{abs(DV['H1.Z_100']):.2f}", "Reproduced (rounding)"),
    ("Fisher χ² (10 d / 100 d)", "42.57 / 270.06", f"{DV['H1.Fisher_10']['chi2']:.2f} / {f100['chi2']:.2f}", "Reproduced"),
    ("Critical χ² for df = 200 at α = 0.05 / 0.01 / 0.001", "233.9 / 248.4 / 278.5", " / ".join(str(v) for v in f100["kritik"].values()), "Corrected in the revision"),
    ("Medians pre/post 1990; DBSCAN clusters and noise; 2σ outliers; cubic R²", "12.22 / 13.22; 21, 155 and 13; 12; 0.746", "same", "Reproduced"),
    ("Spearman coefficient", "printed as 'p = 0.48'", f"ρ = {DV['H1.spearman'][0]:.2f}", "Symbol corrected"),
    ("H2 matches; Methods A and B", "20,590; 2.57×; Z ≈ −50.69", f"{DV['H2.N']:,}; {DV['H2.MethodA']['alfa/P']:.2f}×; Z = −{abs(DV['H2.MethodB']['Z(2573.5)']):.2f}", "Reproduced"),
    ("Group A eccentricities", "e ≈ 0.0–0.02", f"median e = {GA_OZ['e_med']:.2f}", "Corrected in the revision"),
    ("Table 3 (stress test), k = 6, top routes to 55701 Ukalegon", "229.9343", "220.9343", "Typographical error corrected"),
    ("Direct transfer Earth → 55701 Ukalegon", "233.12 CU", f"{d_uk:.2f} CU (Table S2.10)", "Corrected in the revision"),
    ("Route legs 76.94 / 4.41; Euclidean distance 4.126 AU; route length ~14.8 AU", "as printed", f"{c1:.2f} / {c2:.2f}; {DV['H3.oklid_Dunya_Ukalegon']:.3f} AU; {DV['H3.ana_rota_oklid_toplam']:.1f} AU", "Reproduced"),
    ("Routes 1–6 to Thereus (FT, EFF ranking 5 > 3 > 1 > 4 > 6 > 2)", "Table 4, Fig. 8", "same routes and ranking (Table S2.11)", "Reproduced"),
    ("Match numbers of 15025 Uwontario / 755 Quintilla in Section 3.3", "34 / 31", "6 / 26 (first occurrence, as in Table 4)", "Harmonised"),
], columns=["Quantity", "Main text (original)", "Recomputed from the author's data", "Status"])

# ------------------------------------------------------------------ metin
n_rel = SON["H2 güvenilir"]["C_Tj"]["N"]
s = SON["Tüm 1.000"]["C_Tj"]
pA, pB, pC = s["A"] / 1000, s["B"] / 1000, s["C"] / 1000
B = []  # ('h', lvl, text) | ('p', text) | ('img', path, caption, width_cm) | ('t', caption, df)
B += [("p", "This supplement accompanies Section 4.6 of the main text. It documents a post hoc robustness check of the adopted "
             "reading 6EQ=5UJ against 20 alternative parsings of the same sequence and against 1,000 random readings built from "
             "the same six characters. All values refer to the epoch used throughout the study (1977-08-15 00:00 UT) and to the "
             "same data, tolerances and procedures as in the main text.")]
B += [("p", "Figure S2.0 summarises the result: the number of random readings meeting each of the three criteria defined in "
             "Section S2.1.1 and each combination of them, and the number of criteria met by each alternative parsing. The "
             "following sections give the methods and the detailed results.")]
B += [("img", F0, "Fig. S2.0 Features of the adopted reading among the 1,000 random readings (left) and the number of features "
                  "satisfied by the 20 alternative parsings (right). Criterion C as in the main text (Section S2.1.1).", 16.5)]
B += [("h", 1, "S2.1 Methods")]
B += [("h", 2, "S2.1.1 Criteria")]
B += [("p", "Three features of the adopted reading, one for each hypothesis, were evaluated for every reading:")]
B += [("p", "(A) Hypothesis 1 — with E = Earth, U = Uranus and J = Jupiter, the equation is solved for Q and exactly one catalogued "
             "body lies within ±1% of the solution on 1977-08-15.")]
B += [("p", "(B) Hypothesis 2 — with E = Earth and all Q × U × J combinations of bodies whose names begin with the respective "
             "letters (±1.5%), the largest gap between consecutive deviations among the first 31 ranks occurs after rank 8, i.e. "
             "the top octet is separated from the remaining matches.")]
B += [("p", "(C) Hypothesis 3 — the objects of the top octet include a main gateway and a second gateway selected with the "
             "gateway rule of the main text: gateway candidates are numbered, dynamically stable asteroids (comets, Centaurs with "
             "a > 5.5 AU, planets, satellites and spacecraft are excluded); the main gateway is a Jupiter Trojan (5.05 ≤ a ≤ 5.35 AU) "
             "with T_J < 3, and the second gateway is another candidate with T_J < 3. Two variants are also reported: a strict variant "
             "in which the second gateway must be a Hilda (3.7 ≤ a ≤ 4.2 AU), and a semi-major-axis-only variant (a Trojan and a "
             "Hilda in the top octet, regardless of T_J).")]
B += [("h", 2, "S2.1.2 Alternative parsings")]
B += [("p", "The 20 alternative parsings are ten alternative expressions of the six characters compiled by the author, each "
             "evaluated in its algebraic form and in an absolute-value form (Table S2.1). In seven pairs the two forms give "
             "identical Hypothesis 2 results, although their Hypothesis 1 results may differ. For Hypothesis 1, all real roots for Q were used, "
             "with negative roots replaced by their absolute values; Hypotheses 2 and 3 were evaluated exactly as for the adopted reading.")]
B += [("h", 2, "S2.1.3 Random readings")]
B += [("p", "The 1,000 random readings use each of the six characters 6, E, Q, U, J and 5 exactly once, as in the adopted reading. "
             "For each reading the characters were placed in random order, the equality sign was inserted at a random position "
             "(with at least one letter on each side), and each side was built as a random binary expression using the operators "
             "+, −, ×, ÷ and the absolute difference |a − b|. Readings that are algebraically equivalent (identical deviations on "
             "64 random test inputs) or that are constant or undefined were discarded and replaced. A fixed random seed (2026) was "
             "used, so the list is fully reproducible; the complete list (formuller.json) and the generator are provided in the "
             "data repository.")]
B += [("p", "In detail, each random reading was generated as follows: (i) the six characters are randomly permuted; (ii) the "
             "position of the equality sign is drawn uniformly from the five possible positions, and the draw is repeated unless "
             "each side contains at least one of the letters E, Q, U, J; (iii) each side is built as a random binary expression "
             "tree, the split point of every node being drawn uniformly; (iv) each internal node receives one of the operators "
             "+, −, ×, ÷ or |a − b| with equal probability; (v) the reading is evaluated on 64 random test inputs (heliocentric "
             "distances drawn uniformly between 0.5 and 30 AU) and discarded if its relative deviations are constant, undefined, "
             "or identical (to seven decimals) to those of a reading already accepted, including the adopted reading and its "
             "algebraically equivalent forms; (vi) steps (i)–(v) are repeated until 1,000 readings are accepted. Table S2.0 lists the "
             "first ten readings; the complete list of 1,000 readings is given in the accompanying spreadsheet "
             "(Supplementary_Material_S2_tables.xlsx).")]
B += [("t", "Table S2.0. The first ten of the 1,000 random readings (× multiplication, ÷ division, |·| absolute value).", T0)]
B += [("p", f"Criterion B requires a sufficient number of H2 matches to define the deviation gaps reliably; this was the case for "
             f"{n_rel} of the 1,000 random readings. For the remaining readings criterion B was counted as not met.")]
B += [("h", 1, "S2.2 Alternative parsings")]
B += [("p", "Table S2.1 summarises the three criteria for the adopted reading and the 20 alternatives. Only the adopted reading meets "
             "all three. Two distinct alternatives meet two criteria: F7 (single Wow!-epoch match and largest gap after rank 8, but "
             "no gateway with T_J < 3 in the top octet) and F8 (single match and gateways 5254 Ulysses / 84011 Jean-Claude, but the "
             "largest gap after rank 28; its single H1 match is the comet C/1863 T1). Figures S2.1–S2.3 show the three criteria "
             "separately; Figure S2.2b reproduces the elbow analysis of Fig. 4 for all readings.")]
B += [("t", "Table S2.1. The three criteria for the adopted reading and the 20 alternative parsings (1977-08-15 00:00 UT). "
             "✓ = criterion met; ✗ = not met. The Top 8 deviation range and largest-gap rank refer to Hypothesis 2.", T1)]
B += [("img", F1, "Fig. S2.1 Criterion A: number of catalogued bodies within ±1% of the Hypothesis 1 solution on 1977-08-15 for "
                  "each reading (logarithmic scale; zero matches shown as a short bar). The dashed line marks a single match.", 16.5)]
B += [("img", F2, "Fig. S2.2 Criterion B: rank after which the largest deviation gap among the first 31 Hypothesis 2 matches occurs. "
                  "The dashed line marks rank 8.", 16.5)]
for gi, f_ in enumerate(F2b, 1):
    B += [("img", f_, f"Fig. S2.2b (part {gi} of {len(F2b)}) 'Elbow' analysis (zoom-in on the top 48 matches) in the format of "
                      "Fig. 4. The box in each panel gives the position of the largest gap among the first 32 ranks "
                      "(red when the gap follows rank 8).", 16.5)]
B += [("img", F3, "Fig. S2.3 Criterion C: Tisserand parameter of the objects in the top octet of each reading. Red symbols are the "
                  "gateways selected by the rule of Section S2.1.1 (triangle: Jupiter Trojan; square: Hilda).", 16.5)]
B += [("h", 1, "S2.3 Random readings")]
B += [("p", f"Individually, the three features are not rare among random readings: criterion A is met by {s['A']} readings "
             f"({pA:.1%}), criterion B by {s['B']} ({pB:.1%}) and criterion C by {s['C']} ({pC:.1%}) (Fig. S2.4, Table S2.2). "
             f"Pairs occur in {s['A+B'] + s['A+C'] + s['B+C']} readings, listed in Table S2.3. None of the 1,000 random readings "
             f"meets all three criteria, for any of the three definitions of criterion C. Because the expected number of readings "
             f"meeting all three by chance is small even if the features were independent "
             f"({pA:.3f} × {pB:.3f} × {pC:.3f} × 1,000 ≈ {pA * pB * pC * 1000:.2f}), the absence of such readings is not in itself "
             f"a strong discriminator; the more informative quantity is the estimated joint frequency, of order "
             f"{pA * pB * pC:.0e} (about one in {round(1 / (pA * pB * pC), -3):,.0f}) under independence. The observed pairwise counts are "
             f"close to those expected under independence (A + B: {s['A+B']} observed vs {pA * pB * 1000:.1f} expected; "
             f"A + C: {s['A+C']} vs {pA * pC * 1000:.1f}; B + C: {s['B+C']} vs {pB * pC * 1000:.1f}).".replace("e-04", " × 10⁻⁴"))]
B += [("img", F4, "Fig. S2.4 Distribution of the three criteria among the 1,000 random readings: (a) Wow!-epoch matches under "
                  "Hypothesis 1; (b) rank of the largest deviation gap under Hypothesis 2 (readings with a reliable profile); "
                  "(c) gateways in the top octet under three definitions. Red marks the value of the adopted reading; the joint "
                  "occurrence of the criteria is shown in Fig. S2.0.", 16.5)]
B += [("t", "Table S2.2. Number of random readings meeting each criterion and their combinations.", T2)]
B += [("t", "Table S2.3. Random readings meeting two of the three criteria (criterion C as in the main text).", T3)]
B += [("t", "Table S2.4. Random readings whose single Wow!-epoch match is 32532 Thereus (Hypothesis 1, ±1%). Deviations are "
             "from the random-reading pipeline, in which the adopted reading gives 0.90% (0.83% in the main analysis).", T4)]
B += [("h", 1, "S2.4 Main-text statistics across readings")]
B += [("p", "For completeness, the statistics reported in Sections 3.1–3.3 of the main text were computed for the adopted "
             "reading and all 20 alternative parsings with the same data and procedures (Tables S2.5 and S2.6), and the tests that "
             "can be evaluated from the stored match counts were applied to the 1,000 random readings (Fig. S2.5, Table S2.7). "
             "These statistics take similar values across readings. The Z-scores against p₀ = 0.5 are of the same magnitude for "
             "every reading because any small proportion yields a large negative Z; the P-values of Methods A and B depend only on "
             "the number of matches (P = 8/N), so that every reading with N > 8,000 rejects H0; and the temporal structures of "
             "Section 3.1 (bimodality, the shift around 1990, two DBSCAN clusters) arise in most readings because they follow the "
             "time dependence of the planetary distances entering the equations. These statistics are therefore not used as "
             "discriminating criteria; the comparison in Sections S2.2 and S2.3 relies on the joint criteria A–C.")]
B += [("t", "Table S2.5. Hypothesis 1 statistics of the main text (Section 3.1) for all readings (1, 10, 100 and 111 epochs). "
             "Fisher χ² is followed by the decision at α = 0.01 / 0.001 (critical values 37.57 / 45.31 for df = 20 and "
             "249.45 / 267.54 for df = 200; ✓ = H0 rejected); 'undefined' where no match occurs on the Wow! epoch (λ = 0).", T5)]
B += [("t", "Table S2.6. Hypothesis 2 and 3 statistics of the main text (Sections 3.2–3.3) for all readings. Gateways refer to "
             "the elbow group; routes to 32532 Thereus use all T_J < 3 gateways found among the matches.", T6)]
B += [("p", "Notes to Tables S2.5 and S2.6. For the adopted reading, the 100-day Fisher value in Table S2.5 (272.7) includes two "
             "matches on 2012-07-08 that were obtained after a missing Jupiter distance in the source file had been completed from "
             "the database; with the original data χ² = 270.06 (main text), which also exceeds the critical value at α = 0.001 "
             "(267.54). The Hypothesis 2 deviations in Table S2.6 were recomputed for all readings from heliocentric distances "
             "stored with six decimals; for the adopted reading the same eight matches are obtained, and the slightly different "
             "values in the main text (0.000159–0.000778%) derive from higher-precision distances.")]
B += [("img", F5, "Fig. S2.5 Share of the 1,000 random readings for which the tests of the main text reject H0 at the stated "
                  "thresholds (n = number of readings for which the test is defined; Fisher requires at least one match on the "
                  "Wow! epoch, Methods A and B at least eight Hypothesis 2 matches). The 10 control epochs are those of Table S3.", 16.5)]
B += [("t", "Table S2.7. Tests of the main text applied to the 1,000 random readings.", T7)]
B += [("p", "The shift of the matched heliocentric distances around 1990 (Fig. 2 of the main text) is shown for all readings in "
             "Fig. S2.6; it appears in most readings, for the reason given in Section S2.5.")]
for gi, f_ in enumerate(F6, 1):
    B += [("img", f_, f"Fig. S2.6 (part {gi} of {len(F6)}) Distribution of the matched heliocentric distances before and after "
                      "1990 in the format of Fig. 2 (111 epochs, ±1%). Dotted lines: medians before and after 1990.", 16.5)]
T11G = T11.drop(columns=[c for c in T11.columns if c.startswith("_")])
B += [("h", 1, "S2.5 Hypothesis 1: time dependence of the target distance")]
B += [("p", f"For the adopted reading, the Hypothesis 1 target distance is Q(t) = E + (5/6)|U − J|, where E, U and J are the "
             f"heliocentric distances of Earth, Uranus and Jupiter at epoch t. Between 1960 and 2025 Q(t) varies between "
             f"{Q6025.min():.2f} and {Q6025.max():.2f} AU ({QV['1960-07-11']:.2f} AU on 1960-07-11, {QV['1977-08-15']:.2f} AU on "
             f"1977-08-15 and {QV['2010-12-05']:.2f} AU on 2010-12-05), mainly because the heliocentric distance of Uranus increased "
             f"from its perihelion ({U_MIN:%Y}) to its aphelion ({U_MAX:%Y}); the smaller oscillation follows the heliocentric "
             f"distance of Jupiter (orbital period 11.86 years). The matched bodies follow this curve (Fig. S2.8), which accounts "
             f"for the shift of the matched distances around 1990, the S-shaped trend of Fig. S8 and the quasi-periodic residuals "
             f"of Fig. S10. Because every reading that contains the distances of Uranus and Jupiter inherits a similar time "
             f"dependence, these temporal structures appear in most readings (Table S2.5, Fig. S2.6).")]
B += [("h", 1, "S2.6 Hypothesis 2: deviation distribution and the top octet")]
B += [("p", "Within the ±1.5% tolerance, the deviations of the 20,590 Hypothesis 2 matches of the adopted reading are uniformly "
             "distributed (Table S2.8). Under uniformity the deviation of rank 8 is expected to be of order 12/N, so that the high "
             "precision of the top octet follows from the number of matches; the specific feature of the adopted reading is the "
             "gap after rank 8 (criterion B). The P-values of Methods A and B depend only on N.")]
B += [("t", "Table S2.8. Distribution of the Hypothesis 2 deviations of the adopted reading (1977-08-15, E = Earth, ±1.5%).", T8)]
B += [("p", f"Table S2.9 lists the orbital elements of the {GA_OZ['n']} distinct objects of the top octet (Group A of Fig. S15) and "
             f"of Earth. The eccentricities are mostly between 0.1 and 0.25 (median {GA_OZ['e_med']:.2f}; {GA_OZ['e_lt']} of "
             f"{GA_OZ['n']} objects have e < 0.02), the inclinations are mostly below 20° ({GA_OZ['i_lt20']} of {GA_OZ['n']}; median "
             f"{GA_OZ['i_med']:.1f}°), and T_J ranges from {GA_OZ['tj_min']:.2f} to {GA_OZ['tj_max']:.2f} (median {GA_OZ['tj_med']:.2f}); "
             f"{GA_OZ['tj_lt3']} objects have T_J < 3 (the two gateways). In groups of eight matches drawn at random from the same "
             f"20,590 matches, at least one asteroid with T_J < 3 occurs in {GA_OZ['p1']:.0%} and at least two in {GA_OZ['p2']:.0%} "
             f"of cases.")]
B += [("t", "Table S2.9. Orbital elements of the objects of the top octet of the adopted reading (Group A) and of Earth, sorted by T_J.", T9)]
B += [("h", 1, "S2.7 Hypothesis 3: cost function and route selection")]
B += [("p", "The transfer cost of the main text is a weighted sum of absolute differences of orbital elements "
             "(1|Δa| + 5|Δe| + 10|Δi| + 2|ΔT_J|). Such a cost satisfies the triangle inequality, so a route with intermediate stops "
             "cannot be cheaper than the direct transfer; it has the same cost when the intermediate objects lie between the end "
             "points in every element. Accordingly, the values to which the stress test converges (220.93 for 55701 Ukalegon and "
             "50.56 for 84011 Jean-Claude; Table 3) are the direct Earth–gateway costs, and the three-step main route has the same "
             "cost as the direct transfer (Table S2.10). The cost of Route 5 to 32532 Thereus (233.12) is this value plus the final "
             "leg from Ukalegon to Thereus (12.19).")]
B += [("t", "Table S2.10. Leg costs of the main and intermediate routes (cost matrix of the original analysis, k = 7).", T10)]
B += [("p", "Because the cost does not depend on distance, many intermediate stops give the same total cost (FT) but different "
             "route lengths (MT). The efficiency score EFF = FT/MT therefore depends on the stop chosen and decreases with route "
             "length (Table S2.11, Fig. S2.7). The routes of the main text are those returned by the Dijkstra implementation of the "
             "original analysis; in terms of EFF the two best routes pass through the gateways of the top octet (Routes 5 and 3), "
             "whereas the lowest total cost is obtained via 25869 Jacoby (Route 1). Numbers in parentheses give the match in which "
             "each object first appears (e.g. 15025 Uwontario in match 6 of the top octet).")]
B += [("t", "Table S2.11. Routes from Earth to 32532 Thereus (Table 4 and Fig. 8 of the main text) and the equal-cost alternatives "
             "with a single intermediate stop. FT recomputed from the cost matrix (Fig. 8 of the main text shows 298.15 and 221.24 for "
             "Routes 2 and 3 owing to rounding); MT and EFF as in the main text; the EFF range of the alternatives uses "
             "instantaneous positions from JPL Horizons (1977-08-15).", T11G)]
B += [("img", F7, "Fig. S2.7 EFF versus route length (MT) for the six routes of Table S2.11. Curves show EFF = FT/MT for the "
                  "equal-cost alternatives of each route (tick marks: range of their lengths).", 16.5)]
B += [("h", 1, "S2.8 Recurrence of the Thereus solution, 1950–2100")]
B += [("p", "Daily heliocentric distances of Earth, Jupiter, Uranus and 32532 Thereus from JPL Horizons (00:00 UT, 1950–2100) show "
             "that the adopted reading returns Thereus within ±1% in five windows (Fig. S2.8, Table S2.12). Window 2 contains the "
             "Wow! epoch; windows 4 (2045–2046) and 5 (2056) are the epochs proposed for targeted observations in Section 5 of "
             "the main text.")]
B += [("img", F8, "Fig. S2.8 Target distance Q(t) ± 1% of the adopted reading and the heliocentric distance of 32532 Thereus, "
                  "1950–2100. Gold bands mark the epochs at which Thereus lies within ±1% of Q(t).", 16.5)]
B += [("t", "Table S2.12. Windows in which the adopted reading returns 32532 Thereus (±1%, daily epochs 00:00 UT).", T12)]
B += [("h", 1, "S2.9 Limitations")]
B += [("p", "(1) The three criteria were defined after the results of the adopted reading had been inspected. The joint test "
             "therefore cannot be interpreted as a confirmatory test, and the result is reported as a hypothesis-generating "
             "observation (Section 4.6 of the main text).")]
B += [("p", "(2) Each feature taken individually is common among random readings. In single-criterion tests on the same set of "
             "random readings, 45% appear at least as specific to the 1977 epoch as the adopted reading under Hypothesis 1, 5.2% "
             "produce a larger deviation gap under Hypothesis 2, and 8.0% (59 of 740 with a top octet) contain both a Jupiter "
             f"Trojan and a Hilda in the top octet. Nine random readings also return 32532 Thereus as their single Wow!-epoch "
             "match, all with a smaller deviation than the adopted reading (Table S2.4); in 1977 Thereus is the only catalogued "
             "body between 12.0 and 12.9 AU, so any reading whose solution falls in this range returns it.")]
B += [("p", "(3) The joint frequency estimate assumes independence between the criteria. The observed pairwise counts are "
             "consistent with this assumption, but the estimate remains approximate.")]
B += [("p", "(4) All values refer to the standard daily epoch of the detection date (1977-08-15 00:00 UT); the single Hypothesis 1 "
             "match (32532 Thereus) is unchanged at the time of detection (1977-08-16 02:16 UT), whereas the ranking of the top "
             "octet under Hypothesis 2, on which criteria B and C depend, is sensitive to the ~26-hour difference.")]
B += [("p", "(5) The cost function admits many equal-cost intermediate stops; route selection and the EFF values therefore depend "
             "on the stop returned by the routing algorithm (Section S2.7).")]
B += [("h", 1, "S2.10 Data and code availability")]
B += [("p", "The data repository contains: the list of random readings (formuller.json) and its generator (faz3_formuller.py); "
             "the evaluation scripts of the joint test (kapi_tj.py) and of the main analysis (Hypotheses 1–3), including the "
             "routing implementation; per-reading figures in the "
             "formats of Figs. 1–8 and S1–S20 for the adopted reading and all 20 alternative parsings, together with comparison "
             "panels of all readings for each figure type; and all tables of this supplement as a spreadsheet.")]

TITLE = "Supplementary Material S2 — Robustness of the Adopted Reading: Alternative Parsings and Random Readings"


def fmt(v):
    if isinstance(v, (float, np.floating)):
        return f"{v:g}"
    return str(v)


def md(path):
    L = [f"# {TITLE}", ""]
    for b in B:
        if b[0] == "h":
            L += ["#" * (b[1] + 1) + " " + b[2], ""]
        elif b[0] == "p":
            L += [b[1], ""]
        elif b[0] == "img":
            rel = os.path.relpath(b[1], os.path.dirname(path)).replace("\\", "/").replace(" ", "%20")
            L += [f"![{os.path.basename(b[1])}]({rel})", "", f"*{b[2]}*", ""]
        else:
            L += [f"**{b[1]}**", "", "| " + " | ".join(b[2].columns) + " |", "|" + "---|" * len(b[2].columns)]
            L += ["| " + " | ".join(fmt(v).replace("|", "\\|") for v in r) + " |" for r in b[2].itertuples(index=False)]
            L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L))


def docx_(path):
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    sec = doc.sections[0]
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(2))
    doc.add_heading(TITLE, 0)
    for b in B:
        if b[0] == "h":
            doc.add_heading(b[2], b[1])
        elif b[0] == "p":
            p = doc.add_paragraph(b[1]); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif b[0] == "img":
            from PIL import Image
            w_, h_ = Image.open(b[1]).size
            gen = b[3]
            if gen * h_ / w_ > 21.5:                          # sayfaya sığsın (A4, 2 cm kenar, açıklama payı)
                gen = 21.5 * w_ / h_
            doc.add_picture(b[1], width=Cm(gen))
            pp = doc.paragraphs[-1]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pp.paragraph_format.keep_with_next = True         # grafik ile açıklaması aynı sayfada
            c = doc.add_paragraph(); r = c.add_run(b[2]); r.bold = True; r.font.size = Pt(9.5)
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            c.paragraph_format.space_after = Pt(12)
        else:
            c = doc.add_paragraph(); r = c.add_run(b[1]); r.bold = True; r.font.size = Pt(9.5)
            c.paragraph_format.keep_with_next = True          # tablo başlığı tabloyla aynı sayfada
            df = b[2]; tb = doc.add_table(rows=1, cols=len(df.columns)); tb.style = "Table Grid"
            for j, col in enumerate(df.columns):
                tb.rows[0].cells[j].text = str(col)
            for row in df.itertuples(index=False):
                cells = tb.add_row().cells
                for j, v in enumerate(row):
                    cells[j].text = fmt(v)
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            uzun = len(tb.rows) > 24                            # sayfaya sığmayacak tablolar: başlık satırı her sayfada tekrar etsin
            for i, row in enumerate(tb.rows):
                trPr = row._tr.get_or_add_trPr()
                cs = OxmlElement("w:cantSplit"); trPr.append(cs)     # satır iki sayfaya bölünmesin
                if i == 0:
                    th = OxmlElement("w:tblHeader"); trPr.append(th)  # başlık satırı devam sayfalarında tekrar
                for cell in row.cells:
                    for par in cell.paragraphs:
                        par.paragraph_format.space_after = Pt(0)
                        if not uzun and i < len(tb.rows) - 1:
                            par.paragraph_format.keep_with_next = True   # kısa tablo: başlığıyla birlikte tek parça
                        elif uzun and i == 0:
                            par.paragraph_format.keep_with_next = True   # uzun tablo: başlık + ilk satırlar birlikte
                        for run in par.runs:
                            run.font.size = Pt(7 if len(df.columns) > 9 else 8); run.bold = (i == 0)
            doc.add_paragraph()
    doc.save(path)


if __name__ == "__main__":
    md(os.path.join(CIKTI, AD + ".md"))
    dx = os.path.join(CIKTI, AD + ".docx"); docx_(dx)
    with pd.ExcelWriter(os.path.join(CIKTI, AD + "_tables.xlsx")) as w:
        for nm, df in (("Random readings (1,000)", TALL), ("Table S2.0", T0), ("Table S2.1", T1), ("Table S2.2", T2), ("Table S2.3", T3),
                       ("Table S2.4", T4), ("Table S2.5", T5), ("Table S2.6", T6), ("Table S2.7", T7), ("Table S2.8", T8),
                       ("Table S2.9", T9), ("Table S2.10", T10), ("Table S2.11", T11G), ("Table S2.12", T12)):
            df.to_excel(w, nm, index=False)
    from docx2pdf import convert
    convert(dx, os.path.join(CIKTI, AD + ".pdf"))
    print("tamam", CIKTI)
