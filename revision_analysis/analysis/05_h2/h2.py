# -*- coding: utf-8 -*-
"""İŞ 5: Makale Bölüm 3.2 (Hipotez 2) analizlerinin 21 eşitlik için tekrarı.
E = Dünya (sabit); Q, U, J = adı o harfle başlayan cisimler (Wow! günü Excel'leri). Tüm Q×U×J kombinasyonları.
Sapma = |sol − sağ| / |sağ| × 100 (makaledeki tanım); eşleşme ölçütü ±%1,5. En küçük 8 sapma = Top 8.
Analizler (makale + Supplementary 4.2): Tablo 1, Fig. S11 (gruplar), Fig. 4/S12 (KDE elbow), Method A, Method B,
Fig. S13 (log-log histogram), Fig. S14 (dikey profiller), Fig. S15 (Grup A–B yörünge parametreleri)."""
import json, os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402

warnings.filterwarnings("ignore"); np.seterr(all="ignore")
KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti"); os.makedirs(CIKTI, exist_ok=True)
CACHE = os.path.join(KOK, "cache"); os.makedirs(CACHE, exist_ok=True)
ESIK = 1.5
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10})
a = np.abs
r30 = np.sqrt(30)

# kod, yazım, sol(E,Q,U,J), sağ(E,Q,U,J)   (Q skaler, U sütun, J satır olarak yayınlanır)
ESIT = [
    ("Ref", "6|E−Q| = 5|U−J| (makale)", lambda E, Q, U, J: 6 * a(E - Q) + 0 * U * J, lambda E, Q, U, J: 5 * a(U - J)),
    ("F1", "6+E+Q = U+J+5", lambda E, Q, U, J: 6 + E + Q + 0 * U * J, lambda E, Q, U, J: U + J + 5),
    ("F1-mutlak", "|6+E+Q| = |U+J+5|", lambda E, Q, U, J: a(6 + E + Q) + 0 * U * J, lambda E, Q, U, J: a(U + J + 5)),
    ("F2", "(6+E+Q+U+J+5)/6 = 5", lambda E, Q, U, J: (6 + E + Q + U + J + 5) / 6, lambda E, Q, U, J: 5 + 0 * U * J),
    ("F2-mutlak", "|(6+E+Q+U+J+5)/6| = 5", lambda E, Q, U, J: a((6 + E + Q + U + J + 5) / 6), lambda E, Q, U, J: 5 + 0 * U * J),
    ("F3", "(6+5)(Q−E) = U+J", lambda E, Q, U, J: 11 * (Q - E) + 0 * U * J, lambda E, Q, U, J: U + J),
    ("F3-mutlak", "(6+5)|Q−E| = U+J", lambda E, Q, U, J: 11 * a(Q - E) + 0 * U * J, lambda E, Q, U, J: U + J),
    ("F4", "√(6×5) = (Q−E)/(U−J)", lambda E, Q, U, J: r30 + 0 * U * J, lambda E, Q, U, J: (Q - E) / (U - J)),
    ("F4-mutlak", "√(6×5) = |Q−E|/|U−J|", lambda E, Q, U, J: r30 + 0 * U * J, lambda E, Q, U, J: a(Q - E) / a(U - J)),
    ("F5", "Q×E = U+J", lambda E, Q, U, J: Q * E + 0 * U * J, lambda E, Q, U, J: U + J),
    ("F5-mutlak", "|Q×E| = U+J", lambda E, Q, U, J: a(Q * E) + 0 * U * J, lambda E, Q, U, J: U + J),
    ("F6", "(U−6)+(E−5) = Q−J", lambda E, Q, U, J: (U - 6) + (E - 5) + 0 * J, lambda E, Q, U, J: Q - J + 0 * U),
    ("F6-mutlak", "|U−6|+|E−5| = |Q−J|", lambda E, Q, U, J: a(U - 6) + a(E - 5) + 0 * J, lambda E, Q, U, J: a(Q - J) + 0 * U),
    ("F7", "(6×J)/(U−Q) = E/5", lambda E, Q, U, J: 6 * J / (U - Q), lambda E, Q, U, J: E / 5 + 0 * U * J),
    ("F7-mutlak", "(6×J)/|U−Q| = E/5", lambda E, Q, U, J: 6 * J / a(U - Q), lambda E, Q, U, J: E / 5 + 0 * U * J),
    ("F8", "(U+6)/(Q−5) = E/J", lambda E, Q, U, J: (U + 6) / (Q - 5) + 0 * J, lambda E, Q, U, J: E / J + 0 * U),
    ("F8-mutlak", "(U+6)/|Q−5| = E/J", lambda E, Q, U, J: (U + 6) / a(Q - 5) + 0 * J, lambda E, Q, U, J: E / J + 0 * U),
    ("F9", "(Q+U)/(J+6) = 5", lambda E, Q, U, J: (Q + U) / (J + 6), lambda E, Q, U, J: 5 + 0 * U * J),
    ("F9-mutlak", "|Q+U|/(J+6) = 5", lambda E, Q, U, J: a(Q + U) / (J + 6), lambda E, Q, U, J: 5 + 0 * U * J),
    ("F10", "E×5 = (Q−U)/(J−6)", lambda E, Q, U, J: E * 5 + 0 * U * J, lambda E, Q, U, J: (Q - U) / (J - 6)),
    ("F10-mutlak", "E×5 = |Q−U|/|J−6|", lambda E, Q, U, J: E * 5 + 0 * U * J, lambda E, Q, U, J: a(Q - U) / a(J - 6)),
]
KODLAR = [e[0] for e in ESIT]; YAZIM = {e[0]: e[1] for e in ESIT}

# ------------------------------------------------------------------ veri
df = o.veri_yukle()
E = float(df.loc[df.isim == "Earth", "d"].iloc[0])
HAV = {h: df[df.harf == h].reset_index(drop=True) for h in "QUJ"}
Qd, Ud, Jd = (HAV[h].d.values for h in "QUJ")
Qn, Un, Jn = (HAV[h].isim.values for h in "QUJ")
NKOMB = len(Qd) * len(Ud) * len(Jd)

ELEM = {}
for f, anah in ((os.path.join(o.BULMACA, "faz2_sonuclar", "cache", "sbdb_elemanlar.json"), "tj"),
                (os.path.join(os.path.dirname(o.BULMACA), "Alien_Puzzle_Project", "data", "genisletilmis_asteroid_db2.json"), "T_J")):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        try:
            ELEM[k] = {"a": float(v["a"]), "e": float(v["e"]), "i": float(v["i"]), "Tj": float(v[anah])}
        except Exception:
            pass  # yazarın tam hassasiyetli dosyası sonra okunduğu için onun değerleri geçerli olur
MES = dict(zip(df.isim, df.d))


def tara(sol, sag):
    devs, ix = [], []
    U2, J2 = Ud[:, None], Jd[None, :]
    for qi, q in enumerate(Qd):
        s, g = sol(E, q, U2, J2), sag(E, q, U2, J2)
        d = np.broadcast_to(np.abs(s - g) / np.abs(g) * 100, (len(Ud), len(Jd)))
        ui, ji = np.nonzero(np.isfinite(d) & (d <= ESIK))
        devs.append(d[ui, ji]); ix.append(np.c_[np.full(len(ui), qi), ui, ji])
    dv = np.concatenate(devs); ix = np.concatenate(ix) if ix else np.empty((0, 3), int)
    o_ = np.argsort(dv, kind="stable")
    return dv[o_], ix[o_]


# ------------------------------------------------------------------ analiz
def analiz(kod, dv, ix):
    N = len(dv); r = {"Formül": kod, "Eşitlik": YAZIM[kod], "Kombinasyon": NKOMB, "Eşleşme (±%1,5)": N}
    if N < 9:
        r["Not"] = "Yetersiz eşleşme (< 9)"; return r, None, None
    top = pd.DataFrame({"#": range(1, 9), "Q": Qn[ix[:8, 0]], "Q AU": Qd[ix[:8, 0]], "U": Un[ix[:8, 1]], "U AU": Ud[ix[:8, 1]],
                        "J": Jn[ix[:8, 2]], "J AU": Jd[ix[:8, 2]], "Sapma (%)": dv[:8]})
    r["Top 8 sapma aralığı (%)"] = f"{dv[0]:.6f} – {dv[7]:.6f}"
    r["Top 8 payı (%)"] = 8 / N * 100
    # Fig. S11: yazarın grupları = %50 / %25 / %20 / %5 yüzdelik dilimler (Top 8 hariç)
    kalan = dv[8:]
    kes = np.quantile(kalan, [0.5, 0.75, 0.95])
    r["S11 kesimler (%)"] = " / ".join(f"{k:.3f}" for k in kes)
    r["S11 kesimler, düzgün dağılım beklentisi (%)"] = " / ".join(f"{q * ESIK:.3f}" for q in (0.5, 0.75, 0.95))
    r["S11 grup sayıları"] = " / ".join(str(int(x)) for x in np.histogram(kalan, [0, *kes, np.inf])[0])
    # KDE / düzgünlük
    r["Ortalama sapma (%)"] = dv.mean(); r["Düzgün dağılım beklentisi (%)"] = ESIK / 2
    r["KS testi p (düzgün 0–1,5)"] = stats.kstest(dv / ESIK, "uniform").pvalue
    # Elbow: yerel ortalama aralık ile normalize edilmiş boşluklar (Faz 2 yöntemi)
    n_yerel = int((dv <= 0.15).sum())
    aralik = 0.15 / n_yerel if n_yerel else np.nan
    bos = np.diff(np.r_[0.0, dv[:32]]) / aralik
    r["8.–9. arası boşluk (ort. aralık cinsinden)"] = (dv[8] - dv[7]) / aralik
    r["İlk 31'deki en büyük boşluk"] = bos[1:].max() if len(bos) > 1 else np.nan
    r["En büyük boşluğun yeri (… sıradan sonra)"] = int(bos[1:].argmax() + 1) if len(bos) > 1 else np.nan
    # Method A / B (Supplementary Denklem 1–3)
    pA = 8 / N; nB = N / 8; pB = 1 / nB
    r["Method A P = 8/N"] = pA; r["Method A: α(0,001)/P"] = 0.001 / pA
    r["Method A Z (p₀=0,5)"] = (pA - 0.5) / np.sqrt(0.25 / N)
    r["Method B grup sayısı N/8"] = nB; r["Method B P = 1/(N/8)"] = pB
    r["Method B Z (p₀=0,5)"] = (pB - 0.5) / np.sqrt(0.25 / nB)
    r["Method A/B: H0 red (α=0,001)?"] = "Evet" if pA < 0.001 else "Hayır"
    # Ek kontrol: düzgün dağılımda ≤ 8. sapma beklenen sayı
    bek = N * dv[7] / ESIK
    r["Ek: ≤ 8. sapma, beklenen sayı"] = bek
    r["Ek: P(≥8 | şans)"] = stats.poisson.sf(7, bek)
    # Fig. S15: Grup A (Top 8 cisimleri + Dünya) – Grup B (diğer eşleşmelerin cisimleri)
    def cisimler(sec):
        return set(Qn[sec[:, 0]]) | set(Un[sec[:, 1]]) | set(Jn[sec[:, 2]])
    A = cisimler(ix[:8]) | {"Earth"}; B = cisimler(ix[8:]) - A
    r["Grup A cisim (Dünya dahil)"] = len(A); r["Grup B cisim"] = len(B)
    ga = pd.DataFrame([{"isim": x, "AU": MES.get(x), **ELEM.get(x, {})} for x in A])
    gb = pd.DataFrame([{"isim": x, "AU": MES.get(x), **ELEM.get(x, {})} for x in B])
    for c in ("a", "e", "i", "Tj"):
        if c not in ga:
            ga[c] = np.nan
        if c not in gb:
            gb[c] = np.nan
    r["A medyan e"] = ga.e.median(); r["B medyan e"] = gb.e.median()
    r["A: e < 0,02 payı"] = (ga.e < 0.02).mean() if ga.e.notna().any() else np.nan
    r["A medyan i (°)"] = ga.i.median(); r["B medyan i (°)"] = gb.i.median()
    r["A: |Tj−3|<0,15 sayısı"] = int((ga.Tj.sub(3).abs() < 0.15).sum()); r["A medyan Tj"] = ga.Tj.median()
    # Ek kontrol: rastgele 8'li grupların (20.000) yörünge ölçütleri
    rng = np.random.default_rng(0)
    tj_say, e_ort = [], []
    for _ in range(2000 if N > 8 else 0):
        sec = ix[rng.choice(N, 8, replace=False)]
        g = [ELEM.get(x) for x in cisimler(sec)]; g = [x for x in g if x]
        tj_say.append(sum(abs(x["Tj"] - 3) < 0.15 for x in g)); e_ort.append(np.mean([x["e"] for x in g]) if g else np.nan)
    gA = [ELEM.get(x) for x in A - {"Earth"}]; gA = [x for x in gA if x]
    tjA = sum(abs(x["Tj"] - 3) < 0.15 for x in gA); eA = np.mean([x["e"] for x in gA]) if gA else np.nan
    r["Ek: rastgele 8'li ≥ A (|Tj−3|<0,15) olasılığı"] = np.mean(np.array(tj_say) >= tjA) if tj_say else np.nan
    r["Ek: rastgele 8'li ort. e ≤ A olasılığı"] = np.nanmean(np.array(e_ort) <= eA) if e_ort else np.nan
    r["A ortalama e"] = eA
    return r, top, (ga, gb)


# ------------------------------------------------------------------ grafikler (ax tabanlı)
def _bos(ax, kod, n=None):
    ax.text(0.5, 0.5, "Yetersiz eşleşme" + (f" (N={n})" if n is not None else ""), ha="center", va="center", transform=ax.transAxes, color="grey")
    ax.set_title(kod)


def g_pasta(ax, kod, dv):
    if len(dv) < 9:
        return _bos(ax, kod, len(dv))
    kalan = dv[8:]; kes = np.quantile(kalan, [0.5, 0.75, 0.95]); say = np.histogram(kalan, [0, *kes, np.inf])[0]
    lab = ["Top 8", f"G1 ≤{kes[0]:.3f}%", f"G2 ≤{kes[1]:.3f}%", f"G3 ≤{kes[2]:.3f}%", "G4 kalan"]
    ax.pie([max(8, len(dv) * 0.01), *say], labels=lab, textprops={"fontsize": 6}, startangle=90)
    ax.set_title(f"{kod} (N={len(dv)})")


def g_kde(ax, kod, dv):
    if len(dv) < 9:
        return _bos(ax, kod, len(dv))
    x = np.linspace(0, ESIK, 400)
    ax.fill_between(x, stats.gaussian_kde(dv)(x), alpha=0.4); ax.axhline(1 / ESIK, color="k", ls="--", lw=1, label="Düzgün beklenti")
    ax.set_xlim(0, ESIK); ax.set_title(f"{kod} (N={len(dv)})"); ax.set_xlabel("Sapma (%)"); ax.legend(fontsize=6)


def g_elbow(ax, kod, dv):
    if len(dv) < 9:
        return _bos(ax, kod, len(dv))
    renk = ["red", "orange", "gold", "green", "blue", "purple"]
    for k in range(min(48, len(dv))):
        ax.axvline(dv[k], color=renk[k // 8], lw=1.2 if k < 8 else 0.8, ls="-" if k < 8 else "--")
    ax.set_xlim(0, dv[min(47, len(dv) - 1)] * 1.05); ax.set_yticks([])
    ax.set_title(f"{kod}: ilk 48 (kırmızı = Top 8)"); ax.set_xlabel("Sapma (%)")


def g_loglog(ax, kod, dv):
    if len(dv) < 9:
        return _bos(ax, kod, len(dv))
    b = np.logspace(np.log10(max(dv[0] / 2, 1e-8)), np.log10(ESIK), 50)
    ax.hist(dv[8:], bins=b, color="tab:blue", alpha=0.7)
    for v in dv[:8]:
        ax.axvline(v, color="r", ls="--", lw=0.8)
    xs = np.sqrt(b[:-1] * b[1:]); ax.plot(xs, len(dv) * np.diff(b) / ESIK, "k:", lw=1, label="Düzgün beklenti")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{kod} (N={len(dv)})"); ax.legend(fontsize=6); ax.set_xlabel("Sapma (%)")


def g_profil(ax, kod, top):
    if top is None:
        return _bos(ax, kod)
    for h, c in (("Q AU", "tab:blue"), ("U AU", "tab:green"), ("J AU", "tab:orange")):
        ax.plot(top["#"], top[h], "o-", color=c, label=h[0], ms=4)
    ax.axhline(E, color="k", ls="--", lw=1, label="E (Dünya)"); ax.set_xlabel("Top 8 eşleşme no"); ax.set_ylabel("AU")
    ax.set_title(kod); ax.legend(fontsize=6)


def g_grupAB(axs, kod, gr):
    for ax, c in zip(axs, ("a", "e", "i", "Tj", "AU")):
        if gr is None:
            _bos(ax, kod); continue
        ga, gb = gr
        for g, renk, ad in ((gb, "tab:blue", "B"), (ga, "tab:red", "A")):
            v = g[c].dropna().values
            if len(v) >= 2 and np.ptp(v) > 0:
                x = np.linspace(min(ga[c].min(), gb[c].min()), max(ga[c].max(), gb[c].max()), 200)
                ax.plot(x, stats.gaussian_kde(v)(x), color=renk, label=f"Grup {ad} (n={len(v)})")
            for vv in (v if ad == "A" else []):
                ax.axvline(vv, color=renk, alpha=0.3, lw=0.8)
        ax.set_title(f"{kod}: {c}", fontsize=8); ax.legend(fontsize=5)


# ------------------------------------------------------------------ ana akış
if __name__ == "__main__":
    sonuc, ozet, imza = {}, [], {}
    for kod, _, sol, sag in ESIT:
        cp = os.path.join(CACHE, f"{kod}.npz")
        if os.path.exists(cp):
            z = np.load(cp); dv, ix = z["dv"], z["ix"]
        else:
            dv, ix = tara(sol, sag); np.savez_compressed(cp, dv=dv, ix=ix)
        r, top, gr = analiz(kod, dv, ix)
        h = (len(dv), round(float(dv[:50].sum()), 9) if len(dv) else 0)
        r["Not"] = r.get("Not", "") or next((f"{k} ile aynı sonuç" for k, v in imza.items() if v == h), "")
        imza[kod] = h
        sonuc[kod] = (r, top, gr, dv); ozet.append(r)
        kl = os.path.join(CIKTI, "formuller", kod); os.makedirs(kl, exist_ok=True)
        klTR = os.path.join(CACHE, "tr_grafik", kod); os.makedirs(klTR, exist_ok=True)   # Türkçe çalışma grafikleri (teslim edilmez; İngilizceleri makale_grafikleri*.py)
        for ad, fn in (("figS11_gruplar", g_pasta), ("fig4_S12_kde", g_kde), ("fig4_S12_elbow_ilk48", g_elbow), ("figS13_loglog", g_loglog)):
            fig, ax = plt.subplots(figsize=(9, 5.5)); fn(ax, kod, dv); ax.set_title(f"{kod}: {YAZIM[kod]} — {ad}")
            fig.tight_layout(); fig.savefig(os.path.join(klTR, ad + ".png"), dpi=120); plt.close(fig)
        fig, ax = plt.subplots(figsize=(9, 5.5)); g_profil(ax, kod, top); ax.set_title(f"{kod}: {YAZIM[kod]} — Fig. S14 dikey profiller")
        fig.tight_layout(); fig.savefig(os.path.join(klTR, "figS14_profiller.png"), dpi=120); plt.close(fig)
        fig, axs = plt.subplots(1, 5, figsize=(20, 4)); g_grupAB(axs, kod, gr); fig.suptitle(f"{kod}: Fig. S15 Grup A (Top 8) – Grup B")
        fig.tight_layout(); fig.savefig(os.path.join(klTR, "figS15_grupAB.png"), dpi=110); plt.close(fig)
        with pd.ExcelWriter(os.path.join(kl, f"{kod}_veri.xlsx")) as w:
            pd.DataFrame([r]).T.reset_index().rename(columns={"index": "Ölçüt", 0: "Değer"}).to_excel(w, "Özet", index=False)
            if top is not None:
                top.to_excel(w, "Top 8", index=False)
            n = min(len(dv), 1000)
            pd.DataFrame({"Sıra": range(1, n + 1), "Q": Qn[ix[:n, 0]], "U": Un[ix[:n, 1]], "J": Jn[ix[:n, 2]], "Sapma (%)": dv[:n]}).to_excel(w, "İlk 1000 eşleşme", index=False)
            if gr is not None:
                gr[0].to_excel(w, "Grup A", index=False); gr[1].to_excel(w, "Grup B", index=False)
        print(kod, len(dv), r.get("Top 8 sapma aralığı (%)", ""), flush=True)
    ozet = pd.DataFrame(ozet)
    # karşılaştırma panelleri
    pk = os.path.join(CACHE, "tr_paneller"); os.makedirs(pk, exist_ok=True)   # Türkçe çalışma panelleri
    for ad, fn, bas in (("figS11_gruplar", g_pasta, "Fig. S11 — Sapma grupları (Top 8 + %50/%25/%20/%5)"),
                        ("fig4_S12_kde", g_kde, "Fig. 4 / S12 üst — Sapma yoğunluğu (KDE)"),
                        ("fig4_S12_elbow_ilk48", g_elbow, "Fig. 4 / S12 alt — İlk 48 eşleşme (Elbow)"),
                        ("figS13_loglog", g_loglog, "Fig. S13 — Log-log sapma histogramı"),
                        ("figS14_profiller", None, "Fig. S14 — Top 8 dikey profilleri")):
        fig, axs = plt.subplots(5, 5, figsize=(26, 22)); axs = axs.ravel()
        for ax, kod in zip(axs, KODLAR):
            r, top, gr, dv = sonuc[kod]
            g_profil(ax, kod, top) if fn is None else fn(ax, kod, dv)
            if ax.get_legend():
                ax.get_legend().remove()
        for ax in axs[len(KODLAR):]:
            ax.axis("off")
        fig.suptitle(bas + " — 21 eşitlik", fontsize=16); fig.tight_layout(rect=[0, 0, 1, 0.97])
        fig.savefig(os.path.join(pk, f"panel_{ad}.png"), dpi=90); plt.close(fig)
    fig, axs = plt.subplots(len(KODLAR), 5, figsize=(20, 3 * len(KODLAR)))
    for row, kod in zip(axs, KODLAR):
        g_grupAB(row, kod, sonuc[kod][2])
    fig.suptitle("Fig. S15 — Grup A (Top 8 + Dünya) ve Grup B yörünge parametreleri — 21 eşitlik", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.99]); fig.savefig(os.path.join(pk, "panel_figS15_grupAB.png"), dpi=60); plt.close(fig)
    tops = {k: v[1] for k, v in sonuc.items()}
    pd.to_pickle((ozet, tops), os.path.join(CACHE, "ozet.pkl"))
    pd.set_option("display.width", 250)
    print(ozet[["Formül", "Eşleşme (±%1,5)", "Top 8 sapma aralığı (%)", "Method A P = 8/N", "Method B Z (p₀=0,5)",
                "8.–9. arası boşluk (ort. aralık cinsinden)", "İlk 31'deki en büyük boşluk", "Ek: P(≥8 | şans)", "Not"]].to_string())
