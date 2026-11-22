# -*- coding: utf-8 -*-
"""Bölüm 3.2 (Hipotez 2) grafiklerinin 21 eşitlik için makaledeki (İngilizce) formatta yeniden çizimi.
Biçim, yazarın orijinal çizim kodlarından alındı (Alien_Puzzle_Project/src):
  Fig. 4 / S12  → yenigrafik50.py        (KDE genel görünüm + 'Elbow' zoom-in, ilk 48 nokta, 6 grup × 8)
  Fig. S11      → bigpie20590grafik6.py  (kavramsal pasta; Top 8 dilimi görsel olarak büyütülmüş)
  Fig. S13      → historgram1bucuk.py    (log-log histogram, 100 logaritmik aralık, Top 8 kırmızı kesikli)
  Fig. S14      → auatlama.py            (Top 8 heliosentrik uzaklık profili, elmas işaretler)
  Fig. S15      → violingrafik.py        (Grup A – Grup B bölünmüş violin; a ≤ 10, i ≤ 75, uzaklık ≤ 10 filtreleri)
Veri: h2.py'nin önbelleği (cache/<kod>.npz). Çıktı: cikti/formuller/<kod>/ (PNG 300 dpi + PDF)."""
import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
import h2  # noqa: E402  (veri, havuzlar, yörünge elemanları, formül yazımları)

warnings.filterwarnings("ignore")
CACHE = os.path.join(KOK, "cache"); FORM = os.path.join(KOK, "cikti", "formuller")
DATE = "1977-08-15 (Wow! epoch), E = Earth"
YAZ = {k: v.replace("(makale)", "(paper)") for k, v in h2.YAZIM.items()}
ESKI = ["figS11_gruplar.png", "fig4_S12_kde.png", "fig4_S12_elbow_ilk48.png", "figS13_loglog.png",
        "figS14_profiller.png", "figS15_grupAB.png"]
# Yazarın violin kodundaki Dünya değerleri (HARDCODED_GRUP_A_DATA['399'])
EARTH_EL = {"a": 1.0000, "e": 0.0167, "i": 0.0000, "Tj": 6.138}
MAX_VIOLIN = 500_000   # çok büyük uzaklık örneklerinde violin için sabit tohumlu alt örnek


def baslik(fig, kod, y=1.0):
    fig.suptitle(f"{kod.replace('-mutlak', '-abs')}:  {YAZ[kod]}    [{DATE}]", fontsize=13, y=y, fontweight="bold")


def kaydet(fig, kl, ad, **kw):
    for uz in ("png", "pdf"):
        fig.savefig(os.path.join(kl, f"{ad}.{uz}"), dpi=300, facecolor="white", **kw)
    plt.close(fig)


def fmt(x):
    return f"{x:.3f}" if x >= 0.001 else f"{x:.2e}"


def yetersiz(kl, ad, kod, N, ne):
    fig, ax = plt.subplots(figsize=(10, 4)); ax.axis("off")
    ax.text(0.5, 0.5, f"{ne}\nnot applicable: only N = {N} matches within ±1.5% (at least 9 required)",
            ha="center", va="center", fontsize=13)
    baslik(fig, kod); kaydet(fig, kl, ad)


# ------------------------------------------------------------------ Fig. 4 / S12  (yenigrafik50.py)
def fig4_kde_elbow(kl, kod, dv):
    sns.set_theme(style="ticks"); plt.rcdefaults()
    vals = pd.Series(dv); N = len(vals); srt = vals.sort_values().reset_index(drop=True)
    spec = [("Group 1 (Top 8)", "red", "--"), ("Group 2 (Next 8)", "orange", ":"), ("Group 3 (Next 8)", "green", "--"),
            ("Group 4 (Next 8)", "blue", ":"), ("Group 5 (Next 8)", "purple", "--"), ("Group 6 (Next 8)", "brown", ":")]
    groups = {ad: (srt.iloc[8 * k:8 * k + 8], c, s) for k, (ad, c, s) in enumerate(spec) if len(srt.iloc[8 * k:8 * k + 8])}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [1, 2]}, sharex=False)
    kde_ok = N >= 2 and np.ptp(dv) > 0
    if kde_ok:
        sns.kdeplot(vals, fill=True, ax=ax1, color="blue", label=f"All Candidates Distribution (N={N})", cut=0)
    ax1.set_title(f"Overview (Full Distribution, 0% - {vals.max():.2f}%)")
    ax1.set_xlabel("Percentage Difference (Applied Formula Matched)"); ax1.set_ylabel("Density")
    ax1.set_xlim(0, 1.5); ax1.legend(loc="lower left") if kde_ok else None
    if kde_ok:
        sns.kdeplot(vals, fill=True, ax=ax2, color="lightblue", label=f"All Candidates Distribution (N={N})", cut=0)
    for ad, (data, c, s) in groups.items():
        for i, v in enumerate(data):
            ax2.axvline(v, color=c, linestyle=s, linewidth=1.2, label=ad if i == 0 else "")
    son = list(groups.values())[-1][0].max()
    zoom = son * 1.2 if son > 0 else 1e-6
    ax2.set_xlim(0, zoom)
    n48 = min(48, N)
    ax2.set_title(f"'Elbow' Analysis (Zoom-in - Top {n48} Points: 0% - {zoom:.4f}%)" if zoom >= 1e-4 else
                  f"'Elbow' Analysis (Zoom-in - Top {n48} Points: 0% - {zoom:.2e}%)")
    ax2.set_xlabel("Percentage Difference (Applied Formula Matched)"); ax2.set_ylabel("Density")
    ax2.legend(loc="upper left")
    # özel x işaretleri: Grup 1 ve Grup 2'nin ilk değerleri (kırmızı / turuncu, kalın)
    g1 = groups["Group 1 (Top 8)"][0].min(); g2 = groups["Group 2 (Next 8)"][0].min() if "Group 2 (Next 8)" in groups else None
    ozel = [g1] + ([g2] if g2 is not None else [])
    oto = [x for x in ax2.get_xticks() if all(abs(x - v) > zoom * 0.025 for v in ozel)]   # özel etikete çok yakın otomatik etiketleri at
    t = np.sort(np.unique(np.append(oto, ozel))); t = t[(t >= 0) & (t <= zoom)]
    dec = max(5, int(-np.floor(np.log10(zoom))) + 2)
    ax2.set_xticks(t); ax2.set_xticklabels([f"{x:.{dec}f}" for x in t], rotation=90, fontsize=8)
    for v, c in zip(ozel, ("red", "orange")):
        j = np.where(np.isclose(t, v, rtol=0, atol=zoom * 1e-9))[0]
        if len(j):
            ax2.get_xticklabels()[j[0]].set_color(c); ax2.get_xticklabels()[j[0]].set_fontweight("bold")
    # bilgi kutusu: ilk 31 sıradaki en büyük boşluk (makaledeki elbow ölçütü)
    if N >= 10:
        k = min(32, N); bos = np.diff(srt.values[:k]); m = int(bos.argmax())
        ax2.text(0.99, 0.98, f"Largest gap among ranks 1–{k}: between rank {m + 1} and {m + 2}\n"
                 f"(rank 8 = {srt.iloc[7]:.6f}%, rank 9 = {srt.iloc[8]:.6f}%)",
                 transform=ax2.transAxes, ha="right", va="top", fontsize=9,
                 bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=0.9))
    baslik(fig, kod, y=1.0)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    kaydet(fig, kl, "Fig4_S12_KDE_Elbow")


# ------------------------------------------------------------------ Fig. S11  (bigpie20590grafik6.py)
def figS11_pie(kl, kod, dv):
    plt.rcdefaults()
    N = len(dv); kalan = dv[8:]
    kes = np.quantile(kalan, [0.5, 0.75, 0.95]); say = np.histogram(kalan, [0, *kes, np.inf])[0]
    yuz = say / N * 100
    pT = 8 / N * 100
    draw = [5, *yuz]
    lbl_pct = [(f"{pT:.2f}%" if pT >= 0.01 else f"{pT:.4f}%"), f"{yuz[0]:.0f}%", f"{yuz[1]:.0f}%", f"{yuz[2]:.0f}%",
               f"{yuz[3]:.0f}% (Others)"]
    lo = [kalan.min(), *kes]
    legend = [f"Top 8 'Pearls' (Anomalies)\n(n=8) - [VISUALLY EXAGGERATED]",
              f"Group 1: {fmt(lo[0])}% - {fmt(kes[0])}% deviation\n(n={say[0]})",
              f"Group 2: {fmt(kes[0])}% - {fmt(kes[1])}% deviation\n(n={say[1]})",
              f"Group 3: {fmt(kes[1])}% - {fmt(kes[2])}% deviation\n(n={say[2]})",
              f"Group 4: > {fmt(kes[2])}% deviation\n(n={say[3]})"]
    colors = ["#B19CD9", "#C2E0C6", "#F7DC6F", "#FAD5A5", "#F1948A"]
    explode = [0.2, 0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(14, 10)); fig.patch.set_facecolor("white")
    wedges, texts, autot = ax.pie(draw, autopct="", startangle=90, colors=colors, explode=explode,
                                  wedgeprops={"edgecolor": "white", "linewidth": 1.2}, radius=1.1)
    for i, at in enumerate(autot):
        at.set_text(lbl_pct[i]); at.set_color("black"); at.set_fontweight("bold")
        w = wedges[i]; ang = (w.theta1 + w.theta2) / 2.0; rad = np.deg2rad(ang)
        if i == 0:
            r = explode[0] * 1.1 + 0.7 * 1.1; at.set_fontsize(13)
        else:
            r = w.r * (0.60 if i in (1, 2) else 0.65 if i == 3 else 0.78); at.set_fontsize(14)
        at.set_position((r * np.cos(rad), r * np.sin(rad))); at.set_ha("center"); at.set_va("center")
        if i == 4:
            at.set_rotation(ang); at.set_rotation_mode("anchor")
    ax.legend(wedges, legend, title=f"Match Group Distribution\n(Total {N:,})", title_fontsize="14",
              loc="center left", bbox_to_anchor=(0.90, 0, 0.5, 1), fontsize=12)
    ax.axis("equal")
    baslik(fig, kod, y=0.95)
    kaydet(fig, kl, "FigS11_Deviation_Groups_Pie", bbox_inches="tight")


# ------------------------------------------------------------------ Fig. S13  (historgram1bucuk.py)
def figS13_loglog(kl, kod, dv):
    plt.rcdefaults()
    N = len(dv); pos = dv[dv > 0]; pearls = np.sort(dv[:8])
    fig = plt.figure(figsize=(14, 8))
    logbins = np.logspace(np.log10(pos.min()), np.log10(pos.max()), 100)
    plt.hist(pos, bins=logbins, alpha=0.8, label=f"Other {N - 8:,} Matches (n={len(pos)})", color="#483D8B")
    plt.yscale("log"); plt.xscale("log")
    ytop = plt.ylim()[1]
    i, lab = 0, False
    while i < len(pearls):
        v = pearls[i]
        if v <= 0:
            i += 1; continue
        l = "k=1 Matched Objects (n=8)" if not lab else ""
        if i + 1 < len(pearls) and pearls[i + 1] / v < 1.001:      # çok yakın çift: yazarın 'yayma' yöntemi
            v2 = pearls[i + 1]
            plt.axvline(v * 0.995, color="#E24A33", linestyle="--", linewidth=2, label=l, alpha=0.8)
            plt.axvline(v2 * 1.005, color="#E24A33", linestyle="--", linewidth=2, alpha=0.8)
            ty = 10 ** (np.log10(ytop) * 0.9)
            plt.text(v * 0.995, ty, f"{v:.5f}", color="#E24A33", fontsize=8, ha="right", va="center", rotation=90)
            plt.text(v2 * 1.005, ty, f"{v2:.5f}", color="#E24A33", fontsize=8, ha="left", va="center", rotation=90)
            i += 2
        else:
            plt.axvline(v, color="#E24A33", linestyle="--", linewidth=2, label=l, alpha=0.8); i += 1
        lab = True
    plt.xlabel("% Percentage Deviation - Logarithmic Scale", fontsize=12)
    plt.ylabel("Object Formula Matched Number - Logarithmic Scale", fontsize=12)
    plt.legend(); plt.grid(True, which="both", ls="--", alpha=0.5)
    nz = int((dv <= 0).sum())
    if nz:
        plt.gcf().text(0.5, 0.005, f"Note: {nz} match(es) with exactly 0% deviation cannot be shown on a log axis.",
                       ha="center", fontsize=9, color="dimgray")
    baslik(fig, kod, y=0.99); plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    kaydet(fig, kl, "FigS13_LogLog_Histogram")


# ------------------------------------------------------------------ Fig. S14  (auatlama.py)
def figS14_profile(kl, kod, top):
    sns.set_theme(style="whitegrid")
    rows = []
    for _, r in top.iterrows():
        m = f"Match {int(r['#'])}"
        rows += [{"Match": m, "Object Type": "Earth (E)", "Distance": h2.E}, {"Match": m, "Object Type": "Q-Object", "Distance": r["Q AU"]},
                 {"Match": m, "Object Type": "U-Object", "Distance": r["U AU"]}, {"Match": m, "Object Type": "J-Object", "Distance": r["J AU"]}]
    d = pd.DataFrame(rows)
    pal = {"Earth (E)": "#D62728", "Q-Object": "#1F77B4", "U-Object": "#FF7F0E", "J-Object": "#2CA02C"}
    fig = plt.figure(figsize=(16, 9))
    ax = sns.stripplot(data=d, x="Match", y="Distance", hue="Object Type", dodge=True, jitter=0, s=8, marker="D", palette=pal)
    ax.set_xlabel("Match ID", fontsize=14); ax.set_ylabel("Distance (AU)", fontsize=14); ax.set_ylim(bottom=0)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.)
    ymax = d.Distance.max()
    big, small = (0.5, 0.1) if ymax <= 6 else (1, 0.2) if ymax <= 12 else (5, 1) if ymax <= 60 else (10, 2)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(big)); ax.yaxis.set_minor_locator(ticker.MultipleLocator(small))
    ax.yaxis.grid(True, which="major", linestyle="--", linewidth=0.7, color="gray", alpha=0.9)
    ax.yaxis.grid(True, which="minor", linestyle=":", linewidth=0.5, color="gray", alpha=0.5)
    ax.xaxis.grid(False)
    for p in [i + 0.5 for i in range(len(top) - 1)]:
        ax.axvline(p, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    baslik(fig, kod, y=0.99); plt.tight_layout(rect=[0, 0, 1, 0.96])
    kaydet(fig, kl, "FigS14_Heliocentric_Distance_Top8", bbox_inches="tight")


# ------------------------------------------------------------------ Fig. S15  (violingrafik.py)
PARAMS = ["Semi-major axis (AU)", "e (Eccentricity)", "i (Inclination °)", "T_J (Tisserand)", "object_dist (Distance)(AU)"]


def s15_filtre(df, p):
    d = df[df.parameter == p]
    if p in ("Semi-major axis (AU)", "object_dist (Distance)(AU)"):
        d = d[(d.value <= 10) & (d.value >= 0)]
    if p == "i (Inclination °)":
        d = d[(d.value <= 75) & (d.value >= 0)]
    return d


def figS15_violin(kl, kod, dv, ix):
    df, A, B, notlar, nA, nB = s15_veri(dv, ix)
    N = len(dv)
    sns.set_theme(style="whitegrid", rc={"axes.facecolor": (0.9, 0.9, 0.9)})
    params = PARAMS
    fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(14, 28), sharey=False)
    fig.suptitle(f"Group A (k=1) vs Group B (The Rest) Comparison\n{kod.replace('-mutlak', '-abs')}:  {YAZ[kod]}   [{DATE}]\n"
                 f"Group A = {len(A)} unique objects of the Top 8 incl. Earth ({nA} with elements); "
                 f"Group B = {len(B)} unique objects of the other {N - 8:,} matches ({nB} with elements)",
                 fontsize=17, y=1.03)
    _violin_eksenler(fig, axes, df, params, notlar)
    kaydet(fig, kl, "FigS15_GroupA_vs_GroupB_Violin", bbox_inches="tight")


def s15_veri(dv, ix):
    Q, U, J = h2.Qn[ix[:, 0]], h2.Un[ix[:, 1]], h2.Jn[ix[:, 2]]
    A = (set(Q[:8]) | set(U[:8]) | set(J[:8])) | {"Earth"}
    B = (set(Q[8:]) | set(U[8:]) | set(J[8:])) - A
    el = lambda x: EARTH_EL if x == "Earth" else h2.ELEM.get(x)
    rows = []
    for grp, S in (("Group A", A), ("Group B", B)):
        for x in S:
            e = el(x)
            if e:
                rows += [{"value": e["a"], "parameter": "Semi-major axis (AU)", "group": grp},
                         {"value": e["e"], "parameter": "e (Eccentricity)", "group": grp},
                         {"value": e["i"], "parameter": "i (Inclination °)", "group": grp},
                         {"value": e["Tj"], "parameter": "T_J (Tisserand)", "group": grp}]
    par = pd.DataFrame(rows)
    # uzaklık: yazarın kodundaki gibi her eşleşme satırındaki her cisim görünümü (Dünya her satırda Grup A'dadır)
    N = len(dv)
    nm = np.concatenate([Q, U, J]); di = np.concatenate([h2.Qd[ix[:, 0]], h2.Ud[ix[:, 1]], h2.Jd[ix[:, 2]]])
    inA = np.isin(nm, list(A))
    dA = np.r_[np.full(N, h2.E), di[inA]]; dB = di[~inA]
    rng = np.random.default_rng(0); notlar = []
    for ad in ("dA", "dB"):
        arr = dA if ad == "dA" else dB
        if len(arr) > MAX_VIOLIN:
            notlar.append(f"{'Group A' if ad == 'dA' else 'Group B'} distance: random subsample of {MAX_VIOLIN:,} of {len(arr):,} occurrences")
            arr = rng.choice(arr, MAX_VIOLIN, replace=False)
        if ad == "dA":
            dA = arr
        else:
            dB = arr
    dist = pd.DataFrame({"value": np.r_[dA, dB], "parameter": "object_dist (Distance)(AU)",
                         "group": ["Group A"] * len(dA) + ["Group B"] * len(dB)})
    df = pd.concat([par, dist], ignore_index=True)
    nA = len([x for x in A if el(x)]); nB = len([x for x in B if el(x)])
    return df, A, B, notlar, nA, nB


def _violin_eksenler(fig, axes, df, params, notlar, kucuk=False):
    fs = (9, 7) if kucuk else (16, 12)
    for i, p in enumerate(params):
        ax = axes[i]; d = s15_filtre(df, p)
        if d.empty or d.group.nunique() < 2:
            ax.set_title(f"{p} - NOT ENOUGH DATA", color="red", fontsize=fs[0]); continue
        sns.violinplot(data=d, x="parameter", y="value", hue="group", split=True, inner="quartile",
                       palette={"Group A": "#FF5733", "Group B": "#335BFF"}, hue_order=["Group A", "Group B"], ax=ax)
        if p == "T_J (Tisserand)":
            ax.axhline(y=3.0, color="red", linestyle="--", linewidth=1.2 if kucuk else 2, label="Main Belt Limit (T_J=3)")
            ax.axhline(y=2.0, color="green", linestyle="--", linewidth=1.2 if kucuk else 2, label="Centaur Limit (T_J=2)")
            if not kucuk:
                ax.legend(loc="upper right")
        ax.set_title(f"{p} Distribution", fontsize=fs[0]); ax.set_xlabel(""); ax.set_ylabel("Value", fontsize=fs[1])
        if kucuk:
            ax.set_xticklabels([]); ax.tick_params(labelsize=6)
        if i == 0 and not kucuk:
            ax.legend(title="Group", loc="upper right")
        elif (kucuk or p != "T_J (Tisserand)") and ax.get_legend():
            ax.get_legend().remove()
    if notlar and not kucuk:
        fig.text(0.5, -0.005, "Note: " + "; ".join(notlar) + " (fixed seed).", ha="center", fontsize=11, color="dimgray")
    if not kucuk:
        plt.tight_layout(rect=[0, 0, 1, 1])


# ------------------------------------------------------------------ karşılaştırma panelleri (21 eşitlik, İngilizce, makale stili)
PANEL = os.path.join(KOK, "cikti", "karsilastirma")
G_SPEC = [("red", "--"), ("orange", ":"), ("green", "--"), ("blue", ":"), ("purple", "--"), ("brown", ":")]


def _ptitle(ax, kod, N):
    ax.set_title(f"{kod.replace('-mutlak', '-abs')}: {YAZ[kod]}  (N={N:,})", fontsize=9)


def p_pie(ax, kod, dv):
    N = len(dv); kalan = dv[8:]; kes = np.quantile(kalan, [0.5, 0.75, 0.95])
    say = np.histogram(kalan, [0, *kes, np.inf])[0]; yuz = say / N * 100; pT = 8 / N * 100
    cols = ["#B19CD9", "#C2E0C6", "#F7DC6F", "#FAD5A5", "#F1948A"]
    w, _, at = ax.pie([5, *yuz], autopct="", startangle=90, colors=cols, explode=[0.2, 0, 0, 0, 0],
                      wedgeprops={"edgecolor": "white", "linewidth": 1}, radius=1.1)
    lab = [(f"{pT:.2f}%" if pT >= 0.01 else f"{pT:.4f}%"), *[f"{y:.0f}%" for y in yuz]]
    for i, a in enumerate(at):
        ang = np.deg2rad((w[i].theta1 + w[i].theta2) / 2); r = 1.0 if i == 0 else 0.62
        a.set_text(lab[i]); a.set_position((r * np.cos(ang), r * np.sin(ang))); a.set_fontsize(7); a.set_fontweight("bold")
        a.set_ha("center"); a.set_va("center")
    ax.legend(w, ["Top 8 (exaggerated)", f"G1 ≤ {fmt(kes[0])}%", f"G2 ≤ {fmt(kes[1])}%", f"G3 ≤ {fmt(kes[2])}%", f"G4 > {fmt(kes[2])}%"],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, fontsize=6, frameon=False)
    ax.axis("equal"); _ptitle(ax, kod, N)


def p_kde(ax, kod, dv):
    sns.kdeplot(pd.Series(dv), fill=True, ax=ax, color="blue", cut=0)
    ax.set_xlim(0, 1.5); ax.set_xlabel("Percentage Difference (%)", fontsize=7); ax.set_ylabel("Density", fontsize=7)
    ax.tick_params(labelsize=6); _ptitle(ax, kod, len(dv))


def p_elbow(ax, kod, dv):
    N = len(dv); n = min(48, N)
    sns.kdeplot(pd.Series(dv), fill=True, ax=ax, color="lightblue", cut=0)
    for k in range(n):
        c, s = G_SPEC[k // 8]; ax.axvline(dv[k], color=c, linestyle=s, linewidth=0.9)
    zoom = dv[n - 1] * 1.2 if dv[n - 1] > 0 else 1e-6
    ax.set_xlim(0, zoom); ax.set_xlabel("Percentage Difference (%)", fontsize=7); ax.set_ylabel("Density", fontsize=7)
    ax.ticklabel_format(axis="x", style="sci", scilimits=(-3, 3)); ax.tick_params(labelsize=6); ax.xaxis.get_offset_text().set_fontsize(6)
    k = min(32, N); m = int(np.diff(dv[:k]).argmax())
    ax.text(0.98, 0.97, f"Largest gap (ranks 1–{k}):\nbetween {m + 1} and {m + 2}", transform=ax.transAxes, ha="right", va="top",
            fontsize=7, color="darkred" if m + 1 == 8 else "black", bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=0.9))
    _ptitle(ax, kod, N)


def p_loglog(ax, kod, dv):
    pos = dv[dv > 0]
    b = np.logspace(np.log10(pos.min()), np.log10(pos.max()), 100)
    ax.hist(pos, bins=b, alpha=0.8, color="#483D8B")
    for v in dv[:8]:
        if v > 0:
            ax.axvline(v, color="#E24A33", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.set_xlabel("% Deviation (log)", fontsize=7); ax.set_ylabel("Matches (log)", fontsize=7); ax.tick_params(labelsize=6)
    _ptitle(ax, kod, len(dv))


def p_s14(ax, kod, ix):
    pal = [("Earth (E)", "#D62728", None), ("Q-Object", "#1F77B4", h2.Qd[ix[:8, 0]]),
           ("U-Object", "#FF7F0E", h2.Ud[ix[:8, 1]]), ("J-Object", "#2CA02C", h2.Jd[ix[:8, 2]])]
    x = np.arange(8)
    for j, (ad, c, v) in enumerate(pal):
        ax.scatter(x - 0.3 + 0.2 * j, np.full(8, h2.E) if v is None else v, marker="D", s=14, color=c, label=ad, zorder=3)
    for p_ in x[:-1] + 0.5:
        ax.axvline(p_, color="gray", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels([f"M{i + 1}" for i in x], fontsize=6); ax.set_ylim(bottom=0)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.7); ax.tick_params(labelsize=6)
    ax.set_xlabel("Match ID", fontsize=7); ax.set_ylabel("Distance (AU)", fontsize=7); _ptitle(ax, kod, len(ix))


def paneller():
    global MAX_VIOLIN
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    os.makedirs(PANEL, exist_ok=True)
    V = {}
    for k in h2.KODLAR:
        z = np.load(os.path.join(CACHE, f"{k}.npz")); V[k] = (z["dv"], z["ix"])
    tail = "21 equations, E = Earth, 1977-08-15 (Wow! epoch)"
    isler = (("figS11_gruplar", lambda ax, k: p_pie(ax, k, V[k][0]), "Fig. S11 — Distribution of Match Candidates by Deviation Magnitude"),
             ("fig4_S12_kde", lambda ax, k: p_kde(ax, k, V[k][0]), "Fig. 4 / S12 (upper panel) — KDE of Match Deviations: Overview (0% - 1.5%)"),
             ("fig4_S12_elbow_ilk48", lambda ax, k: p_elbow(ax, k, V[k][0]),
              "Fig. 4 / S12 (lower panel) — 'Elbow' Analysis, Zoom-in on Top 48 Points (red = Group 1 / Top 8)"),
             ("figS13_loglog", lambda ax, k: p_loglog(ax, k, V[k][0]), "Fig. S13 — Log-Log Frequency Distribution of Percentage Deviations"),
             ("figS14_profiller", lambda ax, k: p_s14(ax, k, V[k][1]), "Fig. S14 — Heliocentric Distance Composition of the Top 8 Candidate Matches"))
    for ad, fn, bas in isler:
        plt.rcdefaults()
        sns.set_theme(style="whitegrid" if ad == "figS14_profiller" else "ticks")
        fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
        for ax, k in zip(axs, h2.KODLAR):
            fn(ax, k)
        for ax in axs[len(h2.KODLAR):]:
            ax.axis("off")
        if ad == "fig4_S12_elbow_ilk48":
            axs[-1].legend([Line2D([], [], color=c, ls=s) for c, s in G_SPEC],
                           [f"Group {i + 1} ({'Top 8' if i == 0 else 'Next 8'})" for i in range(6)],
                           loc="center", fontsize=14, title="Ranks 1–48", title_fontsize=15)
        if ad == "figS14_profiller":
            h, l = axs[0].get_legend_handles_labels(); axs[-1].legend(h, l, loc="center", fontsize=14, markerscale=2.5)
        if ad == "figS13_loglog":
            axs[-1].legend([Patch(color="#483D8B", alpha=0.8), Line2D([], [], color="#E24A33", ls="--")],
                           ["All other matches", "Top 8 (k=1) matches"], loc="center", fontsize=14)
        fig.suptitle(f"{bas}\n{tail}", fontsize=18); fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(os.path.join(PANEL, f"panel_{ad}.png"), dpi=110, facecolor="white"); plt.close(fig)
        print("panel", ad, flush=True)
    # Fig. S15: 21 satır × 5 parametre bölünmüş violin
    MAX_VIOLIN = 100_000
    plt.rcdefaults(); sns.set_theme(style="whitegrid", rc={"axes.facecolor": (0.9, 0.9, 0.9)})
    fig, axs = plt.subplots(len(h2.KODLAR), 5, figsize=(22, 3.2 * len(h2.KODLAR)))
    for row, k in zip(axs, h2.KODLAR):
        df, A, B, notlar, nA, nB = s15_veri(*V[k])
        _violin_eksenler(fig, row, df, PARAMS, notlar, kucuk=True)
        row[0].set_ylabel(f"{k}\n{YAZ[k]}\nA={len(A)}, B={len(B)}", fontsize=8)
    fig.legend([Patch(color="#FF5733"), Patch(color="#335BFF")], ["Group A (Top 8 objects + Earth)", "Group B (the rest)"],
               loc="upper right", fontsize=14)
    fig.suptitle("Fig. S15 — Comparative Distribution of Orbital and Physical Parameters: Group A (Top 8) vs Group B (The Rest)\n"
                 f"{tail}; filters a ≤ 10 AU, i ≤ 75°, distance ≤ 10 AU; distance violins use ≤ 100,000-point random subsamples",
                 fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(os.path.join(PANEL, "panel_figS15_grupAB.png"), dpi=70, facecolor="white"); plt.close(fig)
    print("panel figS15_grupAB", flush=True)


# ------------------------------------------------------------------ ana akış
if __name__ == "__main__":
    if sys.argv[1:] == ["panel"]:
        paneller(); sys.exit()
    secim = sys.argv[1:] or h2.KODLAR
    for kod in secim:
        z = np.load(os.path.join(CACHE, f"{kod}.npz")); dv, ix = z["dv"], z["ix"]
        kl = os.path.join(FORM, kod); os.makedirs(kl, exist_ok=True)
        for f in ESKI:
            if os.path.exists(os.path.join(kl, f)):
                os.remove(os.path.join(kl, f))
        N = len(dv)
        if N >= 9:
            top = pd.DataFrame({"#": range(1, 9), "Q AU": h2.Qd[ix[:8, 0]], "U AU": h2.Ud[ix[:8, 1]], "J AU": h2.Jd[ix[:8, 2]]})
            fig4_kde_elbow(kl, kod, dv); figS11_pie(kl, kod, dv); figS13_loglog(kl, kod, dv)
            figS14_profile(kl, kod, top); figS15_violin(kl, kod, dv, ix)
        else:
            for ad, ne in (("Fig4_S12_KDE_Elbow", "Fig. 4 / S12"), ("FigS11_Deviation_Groups_Pie", "Fig. S11"),
                           ("FigS13_LogLog_Histogram", "Fig. S13"), ("FigS14_Heliocentric_Distance_Top8", "Fig. S14"),
                           ("FigS15_GroupA_vs_GroupB_Violin", "Fig. S15")):
                yetersiz(kl, ad, kod, N, ne)
        print(kod, N, "tamam", flush=True)
