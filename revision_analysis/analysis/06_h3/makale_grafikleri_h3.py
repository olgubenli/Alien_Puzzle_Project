# -*- coding: utf-8 -*-
"""Bölüm 3.3 (Hipotez 3) grafiklerinin 21 okuma için makaledeki (İngilizce) formatta yeniden çizimi.
Biçim yazarın orijinal kodlarından (Alien_Puzzle_Project/src):
  Fig. 5 / S16 → strestestison6.py   (iki panel: ana / ara kapı; Top 1–5 rota maliyeti k=1–7; k=1 Top 5 iç grafik)
  Fig. 6 / S17 → networkgrafikhat5.py (ağ: turuncu ana yol, yeşil ara yol, kesikli diğer yollar, maliyet etiketleri, yıldızlı kapılar)
  Fig. 7 / S18 → 3dgrafik31.py        (3B: Güneş, Dünya, rota cisimleri, yörüngeler, numaralı oklar, ortografik, görüş 30/45)
  Fig. S19     → dunyadanmesafe.py    (rota cisimleri arası 15.08.1977 Öklid mesafeleri, yatay çubuk)
  Fig. 8 / S20 → anasonkontrol.py     (Thereus rotaları: MT / FT / EFF üçlü çubuk, üç eksen, rota açıklama kutusu)
Hesap h3.py'deki analiz() ile birebir aynıdır (maliyet 1|Δa|+5|Δe|+10|Δi|+2|ΔTj|, Dijkstra, budama, k=1–7).
Çıktı: cikti/formuller/<kod>/ (PNG 300 dpi + PDF)."""
import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import networkx as nx

KOK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KOK)
import h3  # noqa: E402
from h3 import EARTH, THEREUS  # noqa: E402

warnings.filterwarnings("ignore")
FORM = os.path.join(KOK, "cikti", "formuller")
DATE = "1977-08-15 (Wow! epoch), E = Earth"
YAZ = {k: v.replace("(makale)", "(adopted reading)").strip() for k, v in h3.h2.YAZIM.items()}
ESKI = ["fig5_stres_testi.png", "fig6_ag_topolojisi.png", "fig7_3d.png", "fig8_uclu_karsilastirma.png"]
C_MAIN, C_SEC = "#FFC266", "#C1FFC1"


def kisa(x):
    return "Earth" if x == EARTH else x.split(" (")[0]


def baslik(fig, kod, y=0.995, fs=13):
    fig.suptitle(f"{kod.replace('-mutlak', '-abs')}:  {YAZ[kod]}    [{DATE}]", fontsize=fs, fontweight="bold", y=y)


def kaydet(fig, kl, ad, **kw):
    for u in ("png", "pdf"):
        fig.savefig(os.path.join(kl, f"{ad}.{u}"), dpi=300, facecolor="white", **kw)
    plt.close(fig)


def yok(kl, ad, kod, ne, neden):
    fig, ax = plt.subplots(figsize=(12, 4)); ax.axis("off")
    ax.text(0.5, 0.5, f"{ne}\nnot applicable for this reading: {neden}", ha="center", va="center", fontsize=13, wrap=True)
    baslik(fig, kod); kaydet(fig, kl, ad)


NEDEN_KAPI = ("no gateway candidate (numbered, dynamically stable asteroid with $T_J$ < 3)\n"
              "is present in the elbow group, so the main and secondary gateways of Hypothesis 3 are not defined")


# ------------------------------------------------------------------ Fig. 5 / S16
STY = {"Top 1": dict(color="#0072B2", ls="--", marker="o", zorder=10), "Top 2": dict(color="#E69F00", ls="--", marker="s", zorder=9),
       "Top 3": dict(color="#33BB55", ls=":", marker="^", zorder=8), "Top 4": dict(color="#CC79A7", ls=(0, (5, 5)), marker="D", zorder=7),
       "Top 5": dict(color="#D55E00", ls="--", marker="x", zorder=6)}


def fig5(kl, kod, R):
    st = R["stres"]
    paneller = [(ad, g) for ad, g in (("Primary", R["ana"]), ("Secondary", R["ara"])) if g]
    fig, axs = plt.subplots(1, 2, figsize=(22, 10)); ks = list(range(1, 8))
    for ax, (tip, g) in zip(axs, paneller):
        s = st[st["Kapı"].str.startswith("Ana" if tip == "Primary" else "Ara")].set_index("k")
        ax.set_title(f"{tip} Gateway ({kisa(g)})", fontsize=16)
        ax.set_xlabel("Number of Match Groups (k)", fontsize=14); ax.set_ylabel("Cost to Target", fontsize=14)
        vals = []
        for j, (rt, sty) in enumerate(STY.items()):
            y = s[rt].reindex(ks).values.astype(float); vals += list(y[np.isfinite(y)])
            ax.plot(np.array(ks) + (j - 2) * 0.2 / 3, y, label=f"{rt} Route", color=sty["color"], linestyle=sty["ls"],
                    marker=sty["marker"], zorder=sty["zorder"], alpha=0.8)
        lo, hi = min(vals), max(vals); pad = max((hi - lo) * 0.15, 0.1)
        ax.set_ylim(lo - pad, hi + pad); ax.set_xticks(ks); ax.legend(loc="upper right", fontsize=12)
        ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7); ax.set_axisbelow(True)
        for k in ks:
            ax.axvline(k, color="grey", linestyle="--", alpha=0.7, linewidth=0.8)
        # k=1 Top 5 iç grafik
        y1 = [s.loc[1, rt] if 1 in s.index else np.nan for rt in STY]
        bb = ax.get_position()
        ins = fig.add_axes([bb.x0 + bb.width * 0.55, bb.y0 + bb.height * 0.35, bb.width * 0.38, bb.height * 0.32])
        f1 = [v for v in y1 if np.isfinite(v)]
        if f1:
            l1, h1 = min(f1), max(f1); p1 = max((h1 - l1) * 0.25, 0.1)
            for i, (rt, v) in enumerate(zip(STY, y1)):
                if np.isfinite(v):
                    ins.scatter(i, v, color=STY[rt]["color"], marker=STY[rt]["marker"], s=50)
                    if i <= 3:
                        ins.text(i + 0.1, v + p1 * 0.1, f"{v:.4f}", rotation=45, ha="left", va="bottom", fontsize=7, fontweight="bold")
                    else:
                        ins.text(i - 0.15, v, f"{v:.4f}", ha="right", va="center", fontsize=7, fontweight="bold")
            ins.set_ylim(l1 - p1, h1 + p1 * 1.6); ins.set_xlim(-0.5, 4.5)
        ins.set_title("k=1 Top 5 Routes", fontsize=10)
        ins.tick_params(axis="x", which="both", bottom=False, labelbottom=False); ins.grid(True, linestyle=":", alpha=0.5)
        for sp in ins.spines.values():
            sp.set_linewidth(2)
    if len(paneller) == 1:
        axs[1].axis("off"); axs[1].text(0.5, 0.5, "No secondary gateway\n(no second candidate with $T_J$ ≤ 3 in the elbow group)",
                                        ha="center", va="center", fontsize=14, transform=axs[1].transAxes)
    fig.text(0.5, 0.925, "Network Resiliency Stress Test: Top 5 Routes", ha="center", fontsize=22, fontweight="bold")
    baslik(fig, kod, y=0.99)
    plt.subplots_adjust(left=0.05, right=0.97, top=0.86, bottom=0.08, wspace=0.25)
    # iç grafikler subplots_adjust'tan sonra yeniden konumlansın
    for ax, ins in zip(axs, [a for a in fig.axes if a not in axs]):
        bb = ax.get_position(); ins.set_position([bb.x0 + bb.width * 0.55, bb.y0 + bb.height * 0.35, bb.width * 0.38, bb.height * 0.32])
    kaydet(fig, kl, "Fig5_S16_Stress_Test")


# ------------------------------------------------------------------ Fig. 6 / S17
def fig6(kl, kod, R):
    ag = R["ag7"]; rot = R["rot7"]
    yollar = {r["Kapı"]: r["_yol"] for _, r in rot.iterrows() if r["_yol"]}
    ana, ara = R["ana"], R["ara"]
    main, sec = yollar.get("Ana", []), yollar.get("Ara", [])
    diger = set()
    for g in (ana, ara):
        if g:
            for c, y in R.get("top5_7", {}).get(g, ag.top5(g))[1:]:
                for i in range(len(y) - 1):
                    e = tuple(sorted((y[i], y[i + 1])))
                    diger.add(e)
    ana_e = {tuple(sorted((main[i], main[i + 1]))) for i in range(len(main) - 1)}
    sec_e = {tuple(sorted((sec[i], sec[i + 1]))) for i in range(len(sec) - 1)}
    diger -= ana_e | sec_e
    G = nx.Graph()
    for e in ana_e | sec_e | diger:
        G.add_edge(*e)
    lab = {x: ("Earth" if x == EARTH else f"{kisa(x)} ({ag.ilk_sira.get(x, '-')})") for x in G.nodes}
    # yerleşim: Dünya sol alt, ana kapı sağ üst, ara kapı sağ alt; rota durakları aradaki çizgi boyunca
    sabit = {EARTH: (0, 0)}
    if ana:
        sabit[ana] = (10, 10)
    if ara:
        sabit[ara] = (10, 2) if ana else (10, 6)
    for yol, (dx, dy) in ((main, (1.2, 1.6)), (sec, (1.2, -0.6))):
        n = len(yol) - 1
        for i, x in enumerate(yol[1:-1], 1):
            if x not in sabit:
                p0, p1 = np.array(sabit[EARTH]), np.array(sabit[yol[-1]])
                sabit[x] = tuple(p0 + (p1 - p0) * i / n + np.array([-dx, dy]) * np.sin(np.pi * i / n))
    ser = [x for x in G.nodes if x not in sabit]
    pos = nx.spring_layout(G, pos={**sabit, **{x: (5 + np.cos(i), 6 + np.sin(i)) for i, x in enumerate(ser)}},
                           fixed=list(sabit), seed=1, k=3.0) if ser else dict(sabit)
    fig, ax = plt.subplots(figsize=(16, 10))
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=["gold" if x in (ana, ara) else "#ADD8E6" for x in G.nodes],
                           edgecolors="black", ax=ax)
    ortak = ana_e & sec_e                                  # iki rotanın ortak yolu: turuncu üstünde ince yeşil
    nx.draw_networkx_edges(G, pos, edgelist=list(ana_e), width=7 if ortak else 4, edge_color=C_MAIN, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=list(sec_e - ortak), width=4, edge_color=C_SEC, ax=ax)
    if ortak:
        nx.draw_networkx_edges(G, pos, edgelist=list(ortak), width=3, edge_color="#5FD35F", ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=list(diger), width=1, edge_color="black", style="dashed", alpha=0.5, ax=ax)
    el = {e: (f"{h3.ymaliyet(*e):.2f}" if e in ana_e | sec_e else f"{h3.ymaliyet(*e):.4f}") for e in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=el, font_size=9, ax=ax)
    for x, (px, py) in pos.items():
        if x == EARTH:
            ax.text(px, py, "Earth", ha="center", va="center", fontsize=10, fontweight="bold")
        else:
            ax.text(px, py + (0.75 if py >= pos[EARTH][1] + 4 else -0.75), lab[x], ha="center", va="center", fontsize=10, fontweight="bold")
    for g, c, t, dy in ((ana, C_MAIN, "Main Gate", 1.35), (ara, C_SEC, "Secondary Gate", -1.35)):
        if g:
            px, py = pos[g]
            ax.plot(px, py + dy, marker="*", markersize=20, markerfacecolor=c, markeredgecolor="black")
            ax.text(px, py + dy + (0.45 if dy > 0 else -0.5), t, fontweight="bold", ha="center", fontsize=10)
    ax.axis("off")
    ax.legend(handles=[Line2D([0], [0], color=C_MAIN, lw=4, label="Main network connection road"),
                       Line2D([0], [0], color=C_SEC, lw=4, label="Secondary network connection road"),
                       Line2D([0], [0], color="black", lw=1, ls="dashed", label="Other network connection roads (Top 2–5 routes, k=7)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, frameon=False, fontsize=12)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1.5, max(xs) + 1.5); ax.set_ylim(min(ys) - 2.2, max(ys) + 2.2)
    baslik(fig, kod); fig.tight_layout(rect=[0, 0, 1, 0.97])
    kaydet(fig, kl, "Fig6_S17_Network_Topology", bbox_inches="tight")


# ------------------------------------------------------------------ Fig. 7 / S18
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *a, **k):
        super().__init__((0, 0), (0, 0), *a, **k); self._v = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs, ys, zs = proj3d.proj_transform(*self._v, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return np.min(zs)


def yorunge(el):
    if not el or el.get("EC", 1) >= 1 or el.get("A", 0) <= 0:
        return None
    a, e = el["A"], el["EC"]; i, Om, w = np.radians([el["IN"], el["OM"], el["W"]])
    nu = np.linspace(0, 2 * np.pi, 360); r = a * (1 - e * e) / (1 + e * np.cos(nu)); xp, yp = r * np.cos(nu), r * np.sin(nu)
    x = xp * (np.cos(w) * np.cos(Om) - np.sin(w) * np.cos(i) * np.sin(Om)) - yp * (np.sin(w) * np.cos(Om) + np.cos(w) * np.cos(i) * np.sin(Om))
    y = xp * (np.cos(w) * np.sin(Om) + np.sin(w) * np.cos(i) * np.cos(Om)) + yp * (np.cos(w) * np.cos(i) * np.cos(Om) - np.sin(w) * np.sin(Om))
    z = xp * np.sin(w) * np.sin(i) + yp * np.cos(w) * np.sin(i)
    return x, y, z


def fig7(kl, kod, R):
    rot = R["rot7"]; yollar = {r["Kapı"]: r["_yol"] for _, r in rot.iterrows() if r["_yol"]}
    main, sec = yollar.get("Ana", []), yollar.get("Ara", [])
    fig = plt.figure(figsize=(12, 10)); ax = fig.add_subplot(1, 1, 1, projection="3d")
    P = {x: h3.xyz(x) for x in set(main) | set(sec)}
    lim = max(5, np.ceil(max(np.nanmax(np.abs(p)) for p in P.values()) + 0.5))
    for yol, c1, c2, ls2, lab in ((main, "purple", "orange", "--", "Main Connection Network Route"),
                                  (sec, "green", "lime", ":", "Secondary Connection Network Route")):
        if len(yol) > 1:
            C = np.array([P[x] for x in yol])
            ax.plot(*C.T, color=c1, linestyle=ls2, linewidth=2)
            ax.plot(*C.T, color=c2, linestyle="-", linewidth=2.5, label=lab)
            for i in range(len(C) - 1):
                m = 0.5 * (C[i] + C[i + 1]); u = (C[i + 1] - C[i]) / np.linalg.norm(C[i + 1] - C[i]) * 0.25
                ar = Arrow3D(*zip(m - u, m + u), mutation_scale=10, lw=1.5, arrowstyle="-|>", color="black", zorder=19)
                ax.add_artist(ar)
                ax.text(*(m + [0, 0, 0.2]), str(i + 1), color="white", fontsize=10, fontweight="bold", ha="center", va="center",
                        path_effects=[pe.withStroke(linewidth=2.5, foreground="black")], zorder=20)
    ax.scatter(0, 0, 0, color="yellow", s=600, alpha=0.3); ax.scatter(0, 0, 0, color="yellow", s=150, edgecolors="black", label="Sun")
    renk = ["magenta", "black", "green", "teal", "brown", "navy"]; ri = 0
    for x in list(dict.fromkeys(main + sec)):
        p = P[x]
        if x == EARTH:
            sty = dict(marker="o", color="blue", s=70, label="Earth")
        elif x == R["ana"]:
            sty = dict(marker="*", color="goldenrod", s=160, label=f"{kisa(x)} (Main Gate)")
        elif x == R["ara"]:
            sty = dict(marker="*", color="red", s=160, label=f"{kisa(x)} (Secondary Gate)")
        else:
            sty = dict(marker="o", color=renk[ri % len(renk)], s=30, label=kisa(x)); ri += 1
        ax.scatter(*p, s=sty["s"] * 3, color=sty["color"], alpha=0.15, marker=sty["marker"])
        ax.scatter(*p, edgecolors="black", **sty)
        ax.text(p[0], p[1], p[2] + (0.6 if x != EARTH else -0.8), sty["label"] if x != EARTH else "Earth",
                color="red" if x in (R["ana"], R["ara"]) else ("blue" if x == EARTH else "black"), ha="center", fontsize=9,
                path_effects=[pe.withStroke(linewidth=2.2, foreground="white")], zorder=10)
        o = yorunge(h3.HOR.get(x, {}).get("el")) if x != EARTH else None
        if x == EARTH:
            nu = np.linspace(0, 2 * np.pi, 200); o = (np.cos(nu), np.sin(nu), 0 * nu)
        if o is not None:
            ax.plot(*o, color=sty["color"], linestyle="--", linewidth=1, alpha=0.6,
                    label=(f"{kisa(x)}'s Orbit" if x not in (EARTH, R["ana"], R["ara"]) else None))
    ax.set_xlabel("X Axis (AU)"); ax.set_ylabel("Y Axis (AU)"); ax.set_zlabel("Z Axis (AU)")
    ax.set_xlim([-lim, lim]); ax.set_ylim([-lim, lim]); ax.set_zlim([-lim, lim]); ax.set_box_aspect([1, 1, 1]); ax.view_init(30, 45)
    try:
        ax.set_proj_type("ortho")
    except Exception:
        pass
    h, l = ax.get_legend_handles_labels(); d = dict(zip(l, h))
    ax.legend(d.values(), d.keys(), loc="upper left", facecolor="white", framealpha=0.7, fontsize=9)
    baslik(fig, kod, y=0.97, fs=12)
    kaydet(fig, kl, "Fig7_S18_3D_Illustration", bbox_inches="tight")


# ------------------------------------------------------------------ Fig. S19
def figS19(kl, kod, R):
    rot = R["rot7"]; yollar = [r["_yol"] for _, r in rot.iterrows() if r["_yol"]]
    ciftler = []
    for y in yollar:
        ciftler += [(y[i], y[i + 1]) for i in range(len(y) - 1)]           # rota adımları
        ciftler += [(EARTH, x) for x in y[2:]]                                # Dünya → sonraki duraklar
        if len(y) > 3:
            ciftler += [(y[i], y[-1]) for i in range(1, len(y) - 2)]          # ara durak → kapı
    ciftler = list(dict.fromkeys(ciftler))
    d = sorted(((f"{kisa(a)} - {kisa(b)}", float(np.linalg.norm(h3.xyz(a) - h3.xyz(b)))) for a, b in ciftler), key=lambda t: t[1])
    fig, ax = plt.subplots(figsize=(12, max(4, 0.55 * len(d) + 2)))
    bars = ax.barh([a for a, _ in d], [b for _, b in d], color="#FA8072", alpha=0.8, edgecolor="black")
    ax.set_xlabel("Actual Distance (AU) on 1977-08-15", fontsize=12, fontweight="bold")
    ax.set_title("Inter-Body Distances (1977 Configuration)", fontsize=14, fontweight="bold")
    ax.set_xlim(0, max(b for _, b in d) * 1.15)
    for b in bars:
        ax.text(b.get_width() + 0.1, b.get_y() + b.get_height() / 2, f"{b.get_width():.3f} AU", va="center", ha="left",
                fontsize=10, fontweight="bold")
    baslik(fig, kod, y=1.0, fs=11); fig.tight_layout(rect=[0, 0, 1, 0.96])
    kaydet(fig, kl, "FigS19_Inter_Body_Distances", bbox_inches="tight")


# ------------------------------------------------------------------ Fig. 8 / S20
def fig8(kl, kod, R):
    s = R["S15"]
    s = s[s["Hedef"] == THEREUS].reset_index(drop=True) if len(s) else s
    if not len(s):
        return yok(kl, "Fig8_S20_Triple_Comparison", kod, "Fig. 8 / S20", "no route to 32532 Thereus via a $T_J$ < 3 gateway")
    if kod == "Ref":   # makaledeki Tablo 4 / Fig. 8 rota sırası
        sira = ["25869 Jacoby", "5254 Ulysses", "84011 Jean-Claude", "306001 Joanllaneras", "55701 Ukalegon", "169509 Jeffreyrobbins"]
        s["_s"] = s["Kapı"].map(lambda g: next((i for i, a in enumerate(sira) if g.startswith(a)), 99))
        s = s.sort_values(["_s", "FT (toplam maliyet)"]).head(10).reset_index(drop=True)
    else:
        s = s.sort_values("FT (toplam maliyet)").head(10).reset_index(drop=True)
    x = np.arange(len(s)); w = 0.25
    fig, ax1 = plt.subplots(figsize=(max(15, 2.3 * len(s)), 9))
    r1 = ax1.bar(x - w, s["MT (AU)"], w, label="MT: Distance (AU)", color="#FFB7B2", hatch="//", edgecolor="#555555")
    ax1.set_xlabel("Routes", fontsize=12, fontweight="bold"); ax1.set_ylabel("Physical Distance (AU)", fontsize=12, fontweight="bold", color="#B22222")
    ax1.tick_params(axis="y", labelcolor="#B22222"); ax1.set_ylim(0, s["MT (AU)"].max() * 1.33)
    ax2 = ax1.twinx()
    r2 = ax2.bar(x, s["FT (toplam maliyet)"], w, label="FT: Formula Cost", color="#C7CEEA", hatch="xx", edgecolor="#555555")
    ax2.set_ylabel("Total Formula Cost", fontsize=12, fontweight="bold", color="#483D8B"); ax2.tick_params(axis="y", labelcolor="#483D8B")
    ax2.set_ylim(0, s["FT (toplam maliyet)"].max() * 1.17)
    ax3 = ax1.twinx(); ax3.spines["right"].set_position(("axes", 1.08))
    r3 = ax3.bar(x + w, s["EFF = FT/MT"], w, label="EFF: Cost per AU (FT/MT)", color="#B5EAD7", hatch="..", edgecolor="#555555")
    ax3.set_ylabel("Efficiency (Cost / AU)", fontsize=12, fontweight="bold", color="#2E8B57"); ax3.tick_params(axis="y", labelcolor="#2E8B57")
    ax3.set_ylim(0, s["EFF = FT/MT"].max() * 1.6)
    plt.title("Triple Comparison: Distance vs Cost vs Efficiency (Lower EFF is Better)", fontsize=14, fontweight="bold", pad=20)
    hs = sum((a.get_legend_handles_labels()[0] for a in (ax1, ax2, ax3)), []); ls = sum((a.get_legend_handles_labels()[1] for a in (ax1, ax2, ax3)), [])
    ax1.legend(hs, ls, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=10)
    ax1.set_xticks(x); ax1.set_xticklabels([f"Route {i + 1}" for i in x], fontsize=11, fontweight="bold")
    for rects, a in ((r1, ax1), (r2, ax2), (r3, ax3)):
        for rc in rects:
            a.annotate(f"{rc.get_height():.2f}", xy=(rc.get_x() + rc.get_width() / 2, rc.get_height()), xytext=(0, 3),
                       textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
    det = []
    for i, rw in s.iterrows():
        y = [kisa(z) for z in rw["_yol"]]
        det.append(f"{i + 1}: " + " -> ".join(y) + ("" if rw["Kapı grupta mı"] else "   (gateway outside the elbow group)"))
    plt.figtext(0.15, 0.02, "Route Details:\n" + "\n".join(det), fontsize=9, bbox={"facecolor": "#F0F0F0", "alpha": 0.8, "pad": 10})
    baslik(fig, kod, y=0.995, fs=12)
    fig.tight_layout(); plt.subplots_adjust(bottom=0.18 + 0.022 * len(s), right=0.85, top=0.88)
    kaydet(fig, kl, "Fig8_S20_Triple_Comparison")


# ------------------------------------------------------------------ ana akış
if __name__ == "__main__":
    h3.eksikleri_tamamla()
    secim = sys.argv[1:] or list(h3.h2.KODLAR)
    for kod in secim:
        kl = os.path.join(FORM, kod); os.makedirs(kl, exist_ok=True)
        r, R = h3.analiz(kod)
        for f in ESKI:
            if os.path.exists(os.path.join(kl, f)):
                os.remove(os.path.join(kl, f))
        if R["ana"] or R["ara"]:
            fig5(kl, kod, R); fig6(kl, kod, R); fig7(kl, kod, R); figS19(kl, kod, R)
        else:
            for ad, ne in (("Fig5_S16_Stress_Test", "Fig. 5 / S16 (stress test)"), ("Fig6_S17_Network_Topology", "Fig. 6 / S17 (network topology)"),
                           ("Fig7_S18_3D_Illustration", "Fig. 7 / S18 (3D illustration)"), ("FigS19_Inter_Body_Distances", "Fig. S19 (inter-body distances)")):
                yok(kl, ad, kod, ne, NEDEN_KAPI)
        fig8(kl, kod, R)
        print(kod, "ana:", R["ana"], "ara:", R["ara"], flush=True)
