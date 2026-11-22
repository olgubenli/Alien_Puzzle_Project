# -*- coding: utf-8 -*-
"""İŞ 2: yapılacak.txt'teki 10 formül, yazarın formülü gibi EŞİTLİK olarak (sol = sağ).
E=Dünya, U=Uranüs, J=Jüpiter sabit; Q bilinmeyen; 6 ve 5 sabit katsayı. Tarih 1977-08-15, gerçek AU verisi.
Her eşitlik iki biçimde: Normal ve Mutlak (farklar ve taraflar |…|).
Denklem Q için çözülür; negatif kök atılmaz, mutlak değeri hedef alınır. Katalogda ±%1 aranır.
Sağlama: bulunan cismin mesafesi denkleme geri konur, sol ve sağ karşılaştırılır."""
import numpy as np
import pandas as pd
import ortak as o

np.seterr(all="ignore")
df = o.veri_yukle()
P = o.gezegenler(df)
E, U, J = P["Earth"], P["Uranus"], P["Jupiter"]
a = np.abs
r30 = np.sqrt(6 * 5)

# (kod, normal yazım, mutlak yazım, sol(Q), sağ(Q), mutlak sol(Q), mutlak sağ(Q))
ESITLIKLER = [
    ("Ref", "6|E−Q| = 5|U−J| (makale)", "",
     lambda Q: 6 * a(E - Q), lambda Q: 5 * a(U - J) + 0 * Q, None, None),
    ("F1", "6+E+Q = U+J+5", "|6+E+Q| = |U+J+5|",
     lambda Q: 6 + E + Q, lambda Q: U + J + 5 + 0 * Q, lambda Q: a(6 + E + Q), lambda Q: a(U + J + 5) + 0 * Q),
    ("F2", "(6+E+Q+U+J+5)/6 = 5", "|(6+E+Q+U+J+5)/6| = 5",
     lambda Q: (6 + E + Q + U + J + 5) / 6, lambda Q: 5 + 0 * Q, lambda Q: a((6 + E + Q + U + J + 5) / 6), lambda Q: 5 + 0 * Q),
    ("F3", "(6+5)(Q−E) = U+J", "(6+5)|Q−E| = U+J",
     lambda Q: 11 * (Q - E), lambda Q: U + J + 0 * Q, lambda Q: 11 * a(Q - E), lambda Q: U + J + 0 * Q),
    ("F4", "√(6×5) = (Q−E)/(U−J)", "√(6×5) = |Q−E|/|U−J|",
     lambda Q: r30 + 0 * Q, lambda Q: (Q - E) / (U - J), lambda Q: r30 + 0 * Q, lambda Q: a(Q - E) / a(U - J)),
    ("F5", "Q×E = U+J", "|Q×E| = U+J",
     lambda Q: Q * E, lambda Q: U + J + 0 * Q, lambda Q: a(Q * E), lambda Q: U + J + 0 * Q),
    ("F6", "(U−6)+(E−5) = Q−J", "|U−6|+|E−5| = |Q−J|",
     lambda Q: (U - 6) + (E - 5) + 0 * Q, lambda Q: Q - J, lambda Q: a(U - 6) + a(E - 5) + 0 * Q, lambda Q: a(Q - J)),
    ("F7", "(6×J)/(U−Q) = E/5", "(6×J)/|U−Q| = E/5",
     lambda Q: 6 * J / (U - Q), lambda Q: E / 5 + 0 * Q, lambda Q: 6 * J / a(U - Q), lambda Q: E / 5 + 0 * Q),
    ("F8", "(U+6)/(Q−5) = E/J", "(U+6)/|Q−5| = E/J",
     lambda Q: (U + 6) / (Q - 5), lambda Q: E / J + 0 * Q, lambda Q: (U + 6) / a(Q - 5), lambda Q: E / J + 0 * Q),
    ("F9", "(Q+U)/(J+6) = 5", "|Q+U|/(J+6) = 5",
     lambda Q: (Q + U) / (J + 6), lambda Q: 5 + 0 * Q, lambda Q: a(Q + U) / (J + 6), lambda Q: 5 + 0 * Q),
    ("F10", "E×5 = (Q−U)/(J−6)", "E×5 = |Q−U|/|J−6|",
     lambda Q: E * 5 + 0 * Q, lambda Q: (Q - U) / (J - 6), lambda Q: E * 5 + 0 * Q, lambda Q: a(Q - U) / a(J - 6)),
]


def kokler(g, sinir=1000.0, n=400001):
    """g(Q) = sol − sağ = 0 köklerini (−sinir, +sinir) aralığında bulur; kutupları ayıklar."""
    pos = np.geomspace(1e-6, sinir, n)
    x = np.concatenate([-pos[::-1], [0.0], pos])
    y = g(x)
    out = list(x[y == 0])
    s = np.sign(y)
    for i in np.nonzero(s[:-1] * s[1:] < 0)[0]:
        lo, hi = x[i], x[i + 1]
        glo = g(np.array([lo]))[0]
        for _ in range(200):
            m = 0.5 * (lo + hi); gm = g(np.array([m]))[0]
            if np.sign(gm) == np.sign(glo):
                lo, glo = m, gm
            else:
                hi = m
        r = 0.5 * (lo + hi); gr = g(np.array([r]))[0]
        if np.isfinite(gr) and abs(gr) <= 1e-8 * (1 + abs(y[i]) + abs(y[i + 1])):
            out.append(r)
    return sorted(set(round(v, 9) for v in out))


ozet, tum = [], []
for kod, yaz_n, yaz_m, soln, sagn, solm, sagm in ESITLIKLER:
    bicimler = [("Normal", yaz_n, soln, sagn)]
    if solm is not None:
        bicimler.append(("Mutlak", yaz_m, solm, sagm))
    for bicim, yazim, sol, sag in bicimler:
        kk = kokler(lambda q: sol(q) - sag(q))
        if not kk:
            ozet.append({"Formül": kod, "Biçim": bicim, "Eşitlik": yazim, "Q kökü (AU)": np.nan,
                         "Aranan Q = |kök| (AU)": np.nan, "Eşleşme sayısı (±%1)": 0,
                         "Bulunan cisimler": "Çözüm yok (denklemin kökü yok)", "Not": ""})
            continue
        gorulen = set()
        for r in kk:
            hedef = abs(r)
            if hedef == 0 or round(hedef, 7) in gorulen:
                continue  # aynı |kök| bu eşitlikte zaten arandı
            gorulen.add(round(hedef, 7))
            sap = np.abs(df.d.values - hedef) / hedef * 100
            ok = np.nonzero(sap <= o.TOLERANS)[0]; ok = ok[np.argsort(sap[ok])]
            not_ = []
            if r < 0:
                not_.append("Kök negatif → mutlak değeri arandı")
            for g in ("Earth", "Uranus", "Jupiter"):
                if abs(hedef - P[g]) / P[g] < 1e-7:
                    not_.append(f"Dejenere: kök = {o.GEZEGEN_TR[g]} (formülün kendi girdisi)")
            for i in ok:
                q = df.d.values[i]
                sl, sg = float(sol(np.array([q]))[0]), float(sag(np.array([q]))[0])
                tum.append({"Formül": kod, "Biçim": bicim, "Eşitlik": yazim, "Aranan Q (AU)": hedef,
                            "Cisim": df.isim.values[i], "Cisim mesafesi (AU)": q, "Sapma (%)": sap[i],
                            "Sağlama: sol": sl, "Sağlama: sağ": sg,
                            "Sağlama sapma |sol−sağ|/|sağ| (%)": abs(sl - sg) / abs(sg) * 100 if sg else np.nan})
            ozet.append({"Formül": kod, "Biçim": bicim, "Eşitlik": yazim, "Q kökü (AU)": r,
                         "Aranan Q = |kök| (AU)": hedef, "Eşleşme sayısı (±%1)": len(ok),
                         "Bulunan cisimler": ("; ".join(f"{df.isim.values[i]} (%{sap[i]:.3f})" for i in ok[:10])
                                              + (f" … (+{len(ok) - 10})" if len(ok) > 10 else ""))
                                             if len(ok) else "Yok",
                         "Not": "; ".join(not_)})
ozet = pd.DataFrame(ozet); tum = pd.DataFrame(tum)

# Kök başına en yakın 5 cisim
yakin = []
for _, s in ozet.dropna(subset=["Aranan Q = |kök| (AU)"]).iterrows():
    h = s["Aranan Q = |kök| (AU)"]
    y = df.assign(sap=(df.d - h).abs() / h * 100).nsmallest(5, "sap")
    for _, r in y.iterrows():
        yakin.append({"Formül": s["Formül"], "Biçim": s["Biçim"], "Aranan Q (AU)": h, "Cisim": r.isim,
                      "Mesafe (AU)": r.d, "Sapma (%)": r.sap, "±%1 içinde": r.sap <= o.TOLERANS})
yakin = pd.DataFrame(yakin)

# Cisim bazında adet
cisim = pd.DataFrame()
if len(tum):
    tum["etiket"] = tum["Formül"] + "-" + tum["Biçim"]
    cisim = (tum.groupby("Cisim").agg(**{"Adet": ("etiket", "size"),
                                          "Hangi formüllerde": ("etiket", lambda s: ", ".join(s)),
                                          "Mesafe (AU)": ("Cisim mesafesi (AU)", "first")})
             .reset_index().sort_values(["Adet", "Mesafe (AU)"], ascending=[False, True]))
    tum = tum.drop(columns="etiket")


# Sapmalı özet tablo: her kök için bulunan cisimler ve sapmaları yan yana
def kisa(isim):
    return isim.split(" (")[0] if not isim.startswith(("C/", "P/")) else isim
sapmali = []
for _, s_ in ozet.iterrows():
    h = s_["Aranan Q = |kök| (AU)"]
    q_yazi = "—" if pd.isna(h) else (f"|{s_['Q kökü (AU)']:.2f}|" if s_["Q kökü (AU)"] < 0 else f"{h:.2f}")
    g = tum[(tum["Formül"] == s_["Formül"]) & (tum["Biçim"] == s_["Biçim"]) & np.isclose(tum["Aranan Q (AU)"], h)]         if not pd.isna(h) and len(tum) else pd.DataFrame()
    if len(g):
        g = g.sort_values("Sapma (%)"); n = len(g); ilk = g.head(5)
        cis = f"{n}: " + " / ".join(kisa(c) for c in ilk["Cisim"]) + (" …" if n > 5 else "")
        sap = " / ".join(f"{v:.3f}" for v in ilk["Sapma (%)"]) + (
            f" … (aralık {g['Sapma (%)'].min():.3f}–{g['Sapma (%)'].max():.3f})" if n > 5 else "")
    else:
        cis = "0" if not pd.isna(h) else "Çözüm yok"; sap = "—"
    sapmali.append({"Formül": s_["Formül"] + ("" if s_["Biçim"] == "Normal" else " mutlak"),
                    "Eşitlik": s_["Eşitlik"], "Q (AU)": q_yazi, "Bulunan cisim": cis, "Sapma (%)": sap})
sapmali = pd.DataFrame(sapmali)

# ------------------------------------------------------------------ rapor
R = o.Rapor("İş 2 — 10 Formül Eşitlik Olarak, Q Bilinmeyen, Gerçek Veri (1977-08-15)")
R.p(f"Veri: `wow tarihi` Excel'leri, {len(df):,} cisim. E = Dünya {E:.6f} AU, U = Uranüs {U:.6f} AU, "
    f"J = Jüpiter {J:.6f} AU. 6 ve 5 sabit katsayı. Q bilinmeyen. Tolerans ±%{o.TOLERANS:g}.")
R.p("Yöntem (Hipotez 1 ile aynı): yapılacak.txt'teki her ifade, yazarın 6|E−Q| = 5|U−J| formülü gibi ana "
    "işlemden ikiye bölünerek bir eşitliğe çevrildi (sol = sağ). Her eşitlik iki biçimde çözüldü: Normal ve "
    "Mutlak (farklar ve gerekirse taraflar |…|). Denklem Q için çözüldü; negatif kök atılmadı, mutlak değeri "
    "aranan mesafe olarak alındı. Katalogda bu mesafeye ±%1 yakın cisimler arandı. Sapma = |cisim − Q|/Q × 100.")
R.p("Sağlama: Bulunan her cismin mesafesi denkleme geri konup sol ve sağ taraf hesaplandı.")
R.h("1. Sonuç tablosu: bulunan cisimler ve sapma oranları")
R.p("Sapma = |cisim mesafesi − Q| / Q × 100. |…| ile yazılan Q, negatif kökün mutlak değeridir. "
    "Çok eşleşme olan satırlarda en yakın 5 cisim ve sapma aralığı verilmiştir; tam liste 'Tüm eşleşmeler' sayfasında.")
R.t("Sonuç tablosu (sapmalı)", sapmali)
R.h("2. Ayrıntılı özet: her eşitlik için kök ve bulunan cisimler")
R.t("Özet", ozet)
R.h("3. Bulunan cisimler ve adetleri")
if len(cisim):
    R.t("Cisim adetleri", cisim)
R.h("4. Tüm eşleşmeler ve sağlama")
if len(tum):
    R.t("Tüm eşleşmeler", tum)
R.h("5. Her kök için en yakın 5 cisim")
R.t("En yakın 5", yakin, sadece_excel=True)
R.p("Not: Negatif kökün mutlak değeri denklemin kendi çözümü değildir; bu Q değeri denkleme geri konunca iki "
    "taraf eşit çıkmaz (sağlama sütununda görülür). İsteğe uygun olarak yine de aranmıştır.")
R.kaydet("02_formul_testi")

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(ozet[["Formül", "Biçim", "Eşitlik", "Q kökü (AU)", "Eşleşme sayısı (±%1)", "Bulunan cisimler", "Not"]].to_string())
print(cisim.to_string() if len(cisim) else "eşleşme yok")
if len(tum):
    print(tum[["Formül", "Biçim", "Cisim", "Sapma (%)", "Sağlama: sol", "Sağlama: sağ",
               "Sağlama sapma |sol−sağ|/|sağ| (%)"]].to_string())
