# -*- coding: utf-8 -*-
"""Thereus pencereleri grafiği — makaledeki şekillerin biçiminde (yazarın yenigrafik49.py stili: 15×7, başlık 14 pt, ':' ızgara,
lejant 9 pt, 300 dpi PNG + PDF). Veri: gunluk.csv ve pencereler.csv (thereus_tarihleri.py çıktısı, JPL Horizons 00:00 UT günlük mesafeler).
Çıktı: thereus_pencereleri.(png|pdf) (eski dosyanın yerine)."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

KOK = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"figure.dpi": 100, "savefig.dpi": 300, "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                     "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9})
BUGUN = pd.Timestamp("2026-10-29")
WOW = pd.Timestamp("1977-08-15")

G = pd.read_csv(os.path.join(KOK, "gunluk.csv"), parse_dates=["t"])
P = pd.read_csv(os.path.join(KOK, "pencereler.csv"), parse_dates=["bas", "son", "en_iyi_gun"])

fig, ax = plt.subplots(figsize=(15, 9.5))
ax.fill_between(G.t, G.Qhedef * 0.99, G.Qhedef * 1.01, color="#6baed6", alpha=0.30, zorder=2)
ax.plot(G.t, G.Qhedef, color="#08519c", linewidth=1.4, zorder=3)
ax.plot(G.t, G["T"], color="#D55E00", linewidth=2.5, zorder=4)
ymin, ymax = 8.0, 14.6
satir = []
for n_, (_, r) in enumerate(P.iterrows(), 1):
    ax.axvspan(r.bas, r.son + pd.Timedelta(days=1), color="gold", alpha=0.45, zorder=1, linewidth=0)
    kismi = r.bas <= G.t.min()
    xm = r.bas + (r.son - r.bas) / 2
    ax.annotate(str(n_), xy=(xm, ymax), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10,
                fontweight="bold", color="#5a4a00", annotation_clip=False,
                bbox=dict(boxstyle="circle,pad=0.25", facecolor="gold", alpha=0.8, edgecolor="#5a4a00"))
    satir.append(f"{n_}: {r.bas:%d %b %Y} – {r.son:%d %b %Y} ({int(r.gun)} days{'; begins before 1950' if kismi else ''}); "
                 f"closest match {r.en_iyi_gun:%d %b %Y} ({r.en_iyi:.4f}%)")
ax.axvline(WOW, color="black", linestyle="--", linewidth=1.5, zorder=5)
ax.text(WOW - pd.Timedelta(days=150), ymin + 0.15, "Wow! signal\n(1977-08-15)", ha="right", va="bottom", fontsize=9, fontweight="bold")
ax.axvline(BUGUN, color="grey", linestyle=":", linewidth=1.5, zorder=5)
ax.text(BUGUN + pd.Timedelta(days=150), ymin + 0.15, f"today\n({BUGUN:%Y-%m-%d})", ha="left", va="bottom", fontsize=9, color="dimgrey")
ax.set_xlim(G.t.min(), G.t.max()); ax.set_ylim(ymin, ymax)
ax.xaxis.set_major_locator(mdates.YearLocator(10)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.YearLocator(2))
ax.set_xlabel("Date (00:00 UT)"); ax.set_ylabel("Heliocentric Distance (AU)")
ax.set_title("Epochs at which 6|E−Q| = 5|U−J| (±1%) returns 32532 Thereus, 1950–2100", fontsize=14, pad=24)
ax.grid(True, linestyle=":", alpha=0.7)
hs = [Patch(facecolor="#6baed6", alpha=0.30, label="Formula target distance Q(t) ± 1%"),
      Line2D([0], [0], color="#08519c", linewidth=1.4, label="Q(t) = E + (5/6)|U − J|  (E, U, J: heliocentric distances of Earth, Uranus, Jupiter)"),
      Line2D([0], [0], color="#D55E00", linewidth=2.5, label="32532 Thereus heliocentric distance"),
      Patch(facecolor="gold", alpha=0.45, label=f"Match windows (Thereus within ±1% of Q(t)); total {int(P.gun.sum())} days")]
ax.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2, fontsize=9, frameon=True)
ax.text(0.5, -0.26, "Match windows:\n" + "\n".join(satir), transform=ax.transAxes, ha="center", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#F0F0F0", alpha=0.9, edgecolor="grey"))
ax.text(0.5, -0.52, "Daily heliocentric distances from JPL Horizons (00:00 UT). Window 2 contains the Wow! epoch used in the paper; "
        "windows 4 and 5 can be fixed in advance for targeted observations.", transform=ax.transAxes, ha="center", va="top", fontsize=8, color="#333333")
fig.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.36)
for u in ("png", "pdf"):
    fig.savefig(os.path.join(KOK, f"thereus_pencereleri.{u}"), dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(P.to_string(index=False))
