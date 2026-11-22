# -*- coding: utf-8 -*-
"""Türkçe ek panellerin İngilizce, makale biçimindeki sürümleri (yazarın stili: ':' ızgara, 14 pt başlık, 300 dpi PNG + PDF).
  04_111gun: Panel_Deviation_Distribution, Panel_Daily_Best_Deviation   (eski: panel_sapma_dagilimi, panel_gunluk_en_iyi_sapma)
  06_h3:     Panel_EFF_vs_MT, Panel_Gateway_Formulas_Thereus_Routes     (eski: panel_eff_mt, kapi4_karsilastirma)"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KOK = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"figure.dpi": 100, "savefig.dpi": 300, "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
                     "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9})


def ad(k):
    return {"Ref-makale": "Ref (adopted reading)", "Ref": "Ref (adopted reading)"}.get(k, k.replace("-mutlak", "-abs"))


def kaydet(fig, yol):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    for u in ("png", "pdf"):
        fig.savefig(f"{yol}.{u}", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def h1_panelleri():
    sys.path.insert(0, os.path.join(KOK, "04_111gun"))
    from tarama import KODLAR
    M = pd.read_pickle(os.path.join(KOK, "04_111gun", "cache", "eslesmeler.pkl")); W = pd.Timestamp("1977-08-15")
    out = os.path.join(KOK, "04_111gun", "cikti", "karsilastirma_EN")
    fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
    for ax, k in zip(axs, KODLAR):
        d = M[M.formul == k]; best = d.groupby("day").sapma.min(); wb = best.get(W, np.nan)
        ax.hist(d.sapma, bins=20, range=(0, 1), density=True, color="#0072B2", alpha=0.55, edgecolor="white")
        ax.axhline(1.0, color="black", ls="--", lw=1.2, label="Uniform expectation within ±1%")
        if np.isfinite(wb):
            ax.axvline(wb, color="#D55E00", lw=2.5, label=f"Best match on Wow! epoch: {wb:.3f}%")
        ax.set_title(f"{ad(k)}  (n={len(d)}, mean {d.sapma.mean():.3f}%)", fontsize=11)
        ax.set_xlabel("Percentage deviation (%)"); ax.set_ylabel("Density"); ax.legend(fontsize=7); ax.grid(True, linestyle=":", alpha=0.7)
    for ax in axs[len(KODLAR):]:
        ax.axis("off")
    fig.suptitle("Hypothesis 1 — Distribution of percentage deviations of all matches (111 epochs, ±1%), all readings", fontsize=18)
    fig.tight_layout(rect=[0, 0, 1, 0.97]); kaydet(fig, os.path.join(out, "Panel_Deviation_Distribution"))
    fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
    for ax, k in zip(axs, KODLAR):
        best = M[M.formul == k].groupby("day").sapma.min()
        ax.scatter(best.index, best.values, s=12, c="#0072B2", edgecolor="black", linewidth=0.3)
        if W in best.index:
            ax.scatter([W], [best[W]], s=160, c="#D55E00", marker="*", edgecolor="black", zorder=5, label="Wow! epoch (1977-08-15)")
            ax.legend(fontsize=7)
        ax.set_ylim(0, 1); ax.set_title(ad(k), fontsize=11); ax.set_xlabel("Date"); ax.set_ylabel("Best deviation of the epoch (%)")
        ax.grid(True, linestyle=":", alpha=0.7)
    for ax in axs[len(KODLAR):]:
        ax.axis("off")
    fig.suptitle("Hypothesis 1 — Smallest percentage deviation on each epoch (red star: Wow! epoch), all readings", fontsize=18)
    fig.tight_layout(rect=[0, 0, 1, 0.97]); kaydet(fig, os.path.join(out, "Panel_Daily_Best_Deviation"))


def h3_panelleri():
    oz, SON, _ = pd.read_pickle(os.path.join(KOK, "06_h3", "cache", "h3_sonuc.pkl"))
    TH = "32532 Thereus (2001 PT13)"; FL = oz["Formül"].tolist()
    out = os.path.join(KOK, "06_h3", "cikti", "karsilastirma_EN")
    fig, axs = plt.subplots(5, 3, figsize=(20, 22)); axs = axs.ravel()
    for ax, k in zip(axs, FL):
        s = SON[k]["S15"]; s = s[s["Hedef"] == TH] if len(s) else s
        if len(s):
            sc = ax.scatter(s["MT (AU)"], s["EFF = FT/MT"], c=s["FT (toplam maliyet)"], cmap="viridis", s=60, edgecolor="black", linewidth=0.5)
            fig.colorbar(sc, ax=ax, label="FT (total formula cost)")
            ax.set_xlabel("MT: physical distance (AU)"); ax.set_ylabel("EFF = FT / MT")
        else:
            ax.text(0.5, 0.5, "no route to 32532 Thereus\n(no $T_J$ < 3 gateway)", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(ad(k), fontsize=12); ax.grid(True, linestyle=":", alpha=0.7)
    for ax in axs[len(FL):]:
        ax.axis("off")
    fig.suptitle("Hypothesis 3 — EFF versus physical route length (MT) for routes to 32532 Thereus (colour: total cost FT), all readings", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.97]); kaydet(fig, os.path.join(out, "Panel_EFF_vs_MT"))
    # kapısı olan formüller
    K4 = [k for k in ("Ref", "F2", "F3", "F8") if k in SON]
    etk, ft_, mt_, ef_, rk = ["Paper\nUkalegon", "Paper\nJean-Claude"], [233.12, 221.24], [26.29, 22.67], [8.87, 9.76], ["grey", "grey"]
    renk = {"Ref": "#D55E00", "F2": "#0072B2", "F3": "#009E73", "F8": "#CC79A7"}
    for k in K4:
        th = SON[k]["S15"]; th = th[(th["Hedef türü"] == "Thereus") & th["Kapı grupta mı"]]
        for _, x in th.iterrows():
            etk.append(f"{'Ref' if k == 'Ref' else k}\n{x['Kapı'].split(' (')[0].split(' ', 1)[-1]}")
            ft_.append(x["FT (toplam maliyet)"]); mt_.append(x["MT (AU)"]); ef_.append(x["EFF = FT/MT"]); rk.append(renk[k])
    fig, axs = plt.subplots(1, 3, figsize=(18, 6.5))
    for ax, v, t in zip(axs, (ft_, mt_, ef_), ("FT: total formula cost", "MT: physical distance (AU)", "EFF = FT/MT (lower = 'more efficient')")):
        ax.bar(range(len(v)), v, color=rk, edgecolor="black", linewidth=0.6)
        ax.set_xticks(range(len(v))); ax.set_xticklabels(etk, fontsize=8, rotation=45, ha="right"); ax.set_title(t, fontsize=12)
        ax.grid(True, axis="y", linestyle=":", alpha=0.7)
        for i, val in enumerate(v):
            ax.text(i, val, f"{val:.2f}", ha="center", va="bottom", fontsize=7, fontweight="bold")
    fig.suptitle("Readings with gateways: routes to 32532 Thereus via the gateways of the elbow group (grey: values reported in the paper)", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.94]); kaydet(fig, os.path.join(out, "Panel_Gateway_Formulas_Thereus_Routes"))


if __name__ == "__main__":
    h1_panelleri(); h3_panelleri(); print("ek paneller yazıldı")
