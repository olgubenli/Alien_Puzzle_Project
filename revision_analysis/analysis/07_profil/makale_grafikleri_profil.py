# -*- coding: utf-8 -*-
"""Bölüm 4.6 / Supplementary S2 şekli: benimsenen okumanın üç özelliğinin (A, B, C) 1.000 rastgele okumada ve 20 alternatif okumada
ne sıklıkla görüldüğü. Sayılar makaledeki 4.6 metniyle aynı kaynaktan gelir: kapi_tj.py (makaledeki Tj kapı kuralı).
  A: Wow! epoch (1977-08-15 00:00 UT) ±1% içinde tek eşleşme (Hipotez 1)
  B: ilk 31 sıradaki en büyük sapma boşluğu 8. sıradan sonra (Hipotez 2)
  C: Top 8'de Tj < 3 Jüpiter Truvası ana kapı + Tj < 3 ikinci kapı (Hipotez 3)
Biçim: yazarın yenigrafik49.py şekilleri (14 pt başlık, ':' ızgara, 300 dpi PNG + PDF, beyaz zemin).
Çıktı: cikti/Joint_Features_ABC_Random_and_Alternative_Readings.(png|pdf)"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti"); CACHE = os.path.join(KOK, "cache")
plt.rcParams.update({"figure.dpi": 100, "savefig.dpi": 300, "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                     "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9})
AD = "Joint_Features_ABC_Random_and_Alternative_Readings"


def ciz():
    K = pd.read_pickle(os.path.join(CACHE, "kapi_tj.pkl"))
    s = K["sonuc"]["Tüm 1.000"]["C_Tj"]; N = s["N"]
    alt = K["alt"]; alt = alt[alt["Formül"] != "Ref"]
    # sayıları ham tablodan da doğrula (yazar hariç)
    h = K["ham"]; r = h[h.id != "YAZAR"]
    assert (int(r.A.sum()), int(r.B.sum()), int(r.C_Tj.sum())) == (s["A"], s["B"], s["C"]) and len(r) == N
    pA, pB, pC = s["A"] / N, s["B"] / N, s["C"] / N; beklenen = pA * pB * pC

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.8), gridspec_kw={"width_ratios": [1.55, 1]})
    et = ["A", "B", "C", "A + B", "A + C", "B + C", "A + B + C"]
    v = [s["A"], s["B"], s["C"], s["A+B"], s["A+C"], s["B+C"], s["A+B+C"]]
    renk = ["#0072B2"] * 3 + ["#56B4E9"] * 3 + ["#D55E00"]
    b = ax1.bar(range(len(v)), v, color=renk, edgecolor="black", linewidth=0.6)
    for i, (rc, val) in enumerate(zip(b, v)):
        ax1.annotate(f"{val}\n({100 * val / N:.1f}%)" if val else "0", xy=(rc.get_x() + rc.get_width() / 2, val), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax1.set_xticks(range(len(v))); ax1.set_xticklabels(et, fontsize=10, fontweight="bold")
    ax1.set_ylabel(f"Number of random readings (of {N:,})"); ax1.set_ylim(0, max(v) * 1.28)
    ax1.set_title(f"Features of the adopted reading among {N:,} random readings", fontsize=14)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.7)
    ax1.text(0.98, 0.97,
             f"Adopted reading 6|E−Q| = 5|U−J|: A, B and C all satisfied\n"
             f"Random readings with A, B and C together: 0 of {N:,}\n"
             f"Expected joint frequency if independent: {pA:.3f} × {pB:.3f} × {pC:.3f} ≈ {beklenen:.1e} (about 1 in {round(1 / beklenen, -3):,.0f})\n"
             f"95% upper bound for 0 of {N:,}: {3 / N:.1%}",
             transform=ax1.transAxes, ha="right", va="top", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9, edgecolor="black"))

    say = alt["Şart sayısı (C_Tj)"].value_counts().reindex([3, 2, 1, 0], fill_value=0)
    isim = {k: [f.replace("-mutlak", "-abs") for f in alt.loc[alt["Şart sayısı (C_Tj)"] == k, "Formül"]] for k in (3, 2, 1, 0)}
    ax2.barh(range(4), say.values, color=["#D55E00", "#E69F00", "#56B4E9", "#BBBBBB"], edgecolor="black", linewidth=0.6)
    ax2.set_yticks(range(4)); ax2.set_yticklabels(["3 of 3", "2 of 3", "1 of 3", "0 of 3"], fontsize=10, fontweight="bold")
    ax2.invert_yaxis(); ax2.set_xlim(0, max(say.values) * 2.6)
    ax2.set_xlabel(f"Number of alternative readings (of {len(alt)})")
    ax2.set_title(f"Features satisfied by the {len(alt)} alternative readings", fontsize=14)
    for i, k in enumerate((3, 2, 1, 0)):
        lst = isim[k]; txt = ", ".join(lst) if len(lst) <= 6 else ", ".join(lst[:6]) + f", … (+{len(lst) - 6})"
        ax2.text(say[k] + 0.2, i, f"{say[k]}" + (f":  {txt}" if lst else ""), va="center", fontsize=8.5)
    ax2.grid(True, axis="x", linestyle=":", alpha=0.7)

    fig.text(0.5, 0.005, "A: a single match within ±1% on the Wow! epoch (Hypothesis 1); B: largest deviation gap among the first 31 ranks "
             "after rank 8 (Hypothesis 2);\nC: a Jupiter Trojan main gateway with $T_J$ < 3 and a second gateway with $T_J$ < 3 in the top octet "
             "(Hypothesis 3). Epoch 1977-08-15 00:00 UT. Random readings: the six characters used once each,\nin random order, with a random "
             "position of the equality sign and random arithmetic operators (seed 2026).", ha="center", va="bottom", fontsize=8.5, color="#333333")
    fig.tight_layout(rect=[0, 0.09, 1, 1])
    for u in ("png", "pdf"):
        fig.savefig(os.path.join(CIKTI, f"{AD}.{u}"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"A {pA:.1%}  B {pB:.1%}  C {pC:.1%}  A+B+C {s['A+B+C']}  beklenen {beklenen:.2e}")


if __name__ == "__main__":
    ciz()
    # eski a-aralığı kuralına dayanan nadirlik histogramları makaledeki 4.6 ile tutarsız olduğu için kaldırılır
    for eski in ("Profile_Rarity_19770815_0000UT", "Profile_Rarity_19770816_0216UT", "nadirlik_0000", "nadirlik_0216"):
        for u in ("png", "pdf"):
            p = os.path.join(CIKTI, f"{eski}.{u}")
            if os.path.exists(p):
                os.remove(p)
