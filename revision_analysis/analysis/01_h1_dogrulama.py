# -*- coding: utf-8 -*-
"""İŞ 1: Hipotez 1 doğrulaması. 6|E−Q| = 5|U−J|, E=Dünya, U=Uranüs, J=Jüpiter, Q bilinmeyen.
Veri: uzaylı bulmaca/orjinal tarihler dosyalar/wow tarihi (1977-08-15), salt okunur."""
import os, sqlite3, pathlib
import numpy as np
import pandas as pd
import ortak as o

df = o.veri_yukle()
P = o.gezegenler(df)
E, U, J = P["Earth"], P["Uranus"], P["Jupiter"]
tol = o.TOLERANS / 100

# 1) Formülü Q için çöz: |E−Q| = (5/6)|U−J|  →  Q = E ± S
S = 5 / 6 * abs(U - J)
Q1, Q2 = E - S, E + S
hedefler = [q for q in (Q1, Q2) if q > 0]

# 2) Katalog taraması (±%1, orijinal sondogru.py mantığı)
satirlar = []
for qh in hedefler:
    m = df[(df.d >= qh * (1 - tol)) & (df.d <= qh * (1 + tol))]
    for _, r in m.iterrows():
        sol, sag = 6 * abs(E - r.d), 5 * abs(U - J)
        satirlar.append({"Cisim": r.isim, "Harf dosyası": r.harf, "Sayfa": r.sayfa,
                         "Q mesafesi (AU)": r.d, "Q hedef (AU)": qh,
                         "Sapma: |Q−Qhedef|/Qhedef (%)": abs(r.d - qh) / qh * 100,
                         "Sol 6|E−Q|": sol, "Sağ 5|U−J|": sag,
                         "Sapma: |sol−sağ|/sağ (%)": abs(sol - sag) / sag * 100})
es = pd.DataFrame(satirlar)

# 3) Hedefe en yakın 10 cisim (Thereus'un ne kadar yalnız olduğunu göstermek için)
yakin = df.assign(fark=(df.d - Q2).abs()).nsmallest(10, "fark")
yakin = pd.DataFrame({"Cisim": yakin.isim, "Mesafe (AU)": yakin.d,
                      "Hedeften sapma (%)": (yakin.d - Q2).abs() / Q2 * 100,
                      "±%1 içinde": (yakin.d - Q2).abs() / Q2 <= tol})
bant = pd.DataFrame({"Aralık (AU)": ["10–15", "12,0–12,9", f"±%1 ({Q2*(1-tol):.3f}–{Q2*(1+tol):.3f})"],
                     "Cisim sayısı": [int(((df.d >= 10) & (df.d <= 15)).sum()),
                                      int(((df.d >= 12.0) & (df.d <= 12.9)).sum()),
                                      int(((df.d >= Q2*(1-tol)) & (df.d <= Q2*(1+tol))).sum())]})

# 4) SAĞLAMA A: Thereus değerini formüle geri koy
th = df[df.isim.str.contains("Thereus")].iloc[0]
sol, sag = 6 * abs(E - th.d), 5 * abs(U - J)
saglama_a = pd.DataFrame([
    ["E (Dünya)", E], ["U (Uranüs)", U], ["J (Jüpiter)", J], ["Q (Thereus)", th.d],
    ["|U−J|", abs(U - J)], ["S = (5/6)|U−J|", S], ["Q1 = E − S (negatif; mutlak değeri bölüm 7de denendi)", Q1], ["Q2 = E + S (hedef)", Q2],
    ["Sol: 6·|E−Q|", sol], ["Sağ: 5·|U−J|", sag], ["Sol − Sağ", sol - sag],
    ["Sapma |sol−sağ|/sağ (%)", abs(sol - sag) / sag * 100],
    ["Sapma |Q−Q2|/Q2 (%)", abs(th.d - Q2) / Q2 * 100],
    ["Thereus için formülün 'gerektirdiği' katsayı oranı |U−J|/|E−Q| (6/5=1,2 olmalı)", abs(U - J) / abs(E - th.d)],
], columns=["Büyüklük", "Değer"])

# 5) SAĞLAMA B: aynı hesap bigdata.db üzerinde (makaledeki 26.576 cisimlik veri, MPC/SBDB tekrarları dahil)
uri = pathlib.Path(o.BIGDATA_DB).as_uri() + "?mode=ro"
c = sqlite3.connect(uri, uri=True)
db = pd.read_sql_query('select "Object ID" as isim, "Instant_Sun_Dist_AU" as d, "Object_Type" as tip '
                       'from solar_objects where Date=?', c, params=(o.TARIH,))
c.close()
n_isim = db.isim.nunique()
db["d"] = pd.to_numeric(db.d, errors="coerce")
db = db.dropna(subset=["d"])
dbP = db[db.isim.isin(["Earth", "Uranus", "Jupiter"])].groupby("isim").d.first()
Q2db = dbP["Earth"] + 5 / 6 * abs(dbP["Uranus"] - dbP["Jupiter"])
mdb = db[(db.d >= Q2db * (1 - tol)) & (db.d <= Q2db * (1 + tol))]
saglama_b = pd.DataFrame([
    ["Excel (wow tarihi) — benzersiz cisim (mesafeli)", len(df), Q2, ", ".join(es["Cisim"].unique())],
    ["bigdata.db — satır (mesafeli) / benzersiz isim", f"{len(db)} / {n_isim}", Q2db,
     ", ".join(sorted(set(mdb.isim))) + f"  ({len(mdb)} satır: " + ", ".join(mdb.tip) + ")"],
], columns=["Kaynak", "Cisim sayısı", "Q hedef (AU)", "±%1 eşleşme"])

# 6) SAĞLAMA C: eski çıktı dosyası
eski = pd.read_csv(o.ESKI_H1_CSV, sep=";")
saglama_c = pd.DataFrame({"Eski dosya (wow_signal_19770815_matches.csv)": eski["Object ID"],
                          "Eski mesafe": eski["Instant_Sun_Dist_AU"],
                          "Yeni hesapla aynı mı": [(n in set(es["Cisim"])) and
                                                    np.isclose(d, df.set_index("isim").d[n]) for n, d in
                                                    zip(eski["Object ID"], eski["Instant_Sun_Dist_AU"])]})

# ------------------------------------------------------------------ rapor
R = o.Rapor("İş 1 — Hipotez 1 Doğrulaması: 6·|E−Q| = 5·|U−J|")
R.p(f"Tarih: {o.TARIH} (Horizons verisi, 00:00 UT). Veri: `uzaylı bulmaca/orjinal tarihler dosyalar/wow tarihi` "
    f"(26 harf Excel'i, salt okunur). Mesafesi olan benzersiz cisim sayısı: **{len(df):,}**. "
    f"E = Dünya, U = Uranüs, J = Jüpiter; Q bilinmeyen. Tolerans ±%{o.TOLERANS:g} (makaledeki Hipotez 1 ile aynı).")
R.h("1. Formülün çözümü")
R.p(f"|E−Q| = (5/6)·|U−J|  ⇒  Q = E ± (5/6)·|U−J|.\n"
    f"S = (5/6)·|{U:.6f} − {J:.6f}| = {S:.6f} AU.\n"
    f"Q1 = E − S = {Q1:.6f} AU (negatif, fiziksel değil; mutlak değeri |Q1| bölüm 7de ayrıca denendi).\n"
    f"Q2 = E + S = **{Q2:.6f} AU** (hedef). Arama aralığı: {Q2*(1-tol):.6f} – {Q2*(1+tol):.6f} AU.")
R.h("2. Sonuç")
R.p(f"±%1 içinde **{len(es)}** eşleşme: **{', '.join(es['Cisim'])}**. Makaledeki sonuçla aynı (tek çözüm 32532 Thereus).")
R.t("Eşleşme", es)
R.h("3. Sağlama A — Thereus'u formüle geri koyma")
R.t("Sağlama A", saglama_a)
R.p("İki sapma tanımı vardır: hedefe göre (|Q−Q2|/Q2, orijinal kodun ve makalenin kullandığı) ve eşitliğin iki "
    "tarafına göre (|6|E−Q| − 5|U−J||/5|U−J|). İkisi de ±%1 içinde. Tarayıcıdaki Claude'un %0,78 değeri kendi "
    "yaklaşık gezegen değerleriyle hesaplanmıştı (Q hedef 12,2645, Thereus 12,3610); gerçek veriyle %0,83.")
R.h("4. Sağlama B — Aynı hesap bigdata.db üzerinde")
R.t("Sağlama B", saglama_b)
R.p(f"bigdata.db'de 1977-08-15 için {n_isim:,} benzersiz isim var; makaledeki \"26,576 objects\" sayısı buradan "
    "geliyor (MPC/SBDB tekrar sayfaları dahil). Sonuç değişmiyor: yine yalnızca Thereus.")
R.h("5. Sağlama C — Eski çıktı dosyasıyla karşılaştırma")
R.t("Sağlama C", saglama_c)
R.h("6. Thereus neden tek? (hedefe en yakın 10 cisim)")
R.t("En yakın 10", yakin)
R.t("Aralık yoğunluğu", bant)
R.p("1977 kataloğunda 12,0–12,9 AU arasında yalnızca Thereus bulunuyor. Bu yüzden hedefi 12–13 AU civarına düşen "
    "her formül Thereus'u 'tek eşleşme' olarak bulur. Bu durum İş 2'deki formül karşılaştırmasında önemlidir.")
# ------------------------------------------------------------------ 7) Q1'in mutlak değeri
Q1m = abs(Q1)
m1 = df[(df.d >= Q1m * (1 - tol)) & (df.d <= Q1m * (1 + tol))].copy()
m1["sap"] = (m1.d - Q1m).abs() / Q1m * 100
m1 = m1.sort_values("sap")
q1_es = pd.DataFrame({"Cisim": m1.isim, "Sayfa": m1.sayfa, "Q mesafesi (AU)": m1.d,
                      "Sapma: |Q−|Q1||/|Q1| (%)": m1.sap,
                      "Sol 6|E−Q|": 6 * (E - m1.d).abs(), "Sağ 5|U−J|": 5 * abs(U - J),
                      "Sapma: |sol−sağ|/sağ (%)": (6 * (E - m1.d).abs() - 5 * abs(U - J)).abs() / (5 * abs(U - J)) * 100})
y1 = df.assign(fark=(df.d - Q1m).abs()).nsmallest(10, "fark")
q1_yakin = pd.DataFrame({"Cisim": y1.isim, "Mesafe (AU)": y1.d, "Sapma (%)": (y1.d - Q1m).abs() / Q1m * 100,
                         "±%1 içinde": (y1.d - Q1m).abs() / Q1m <= tol})
q1_sag = pd.DataFrame([
    ["Q1 = E − S", Q1], ["|Q1| (yeni hedef)", Q1m],
    ["Arama aralığı ±%1", f"{Q1m*(1-tol):.6f} – {Q1m*(1+tol):.6f}"],
    ["Eşleşme sayısı", len(q1_es)],
    ["Sağlama: Q = |Q1| iken 6|E−Q|", 6 * abs(E - Q1m)], ["Sağ: 5|U−J|", 5 * abs(U - J)],
    ["Sapma |sol−sağ|/sağ (%)", abs(6 * abs(E - Q1m) - 5 * abs(U - J)) / (5 * abs(U - J)) * 100],
], columns=["Büyüklük", "Değer"])

R.h("7. Ek: Q1'in mutlak değeri |E − S| ile arama")
R.p(f"Q1 = E − S = {Q1:.6f} AU negatif çıktığı için ana hesapta atılmıştı. Burada mutlak değeri "
    f"|Q1| = {Q1m:.6f} AU hedef alınarak katalog ±%1 ile yeniden tarandı: **{len(q1_es)} eşleşme**"
    + (f" ({', '.join(q1_es.Cisim.head(5))}{' …' if len(q1_es) > 5 else ''})." if len(q1_es) else "."))
R.t("|Q1| sağlama", q1_sag)
if len(q1_es):
    R.t("|Q1| eşleşmeler", q1_es)
R.t("|Q1| en yakın 10", q1_yakin)
R.p("Sağlama uyarısı: |Q1| değeri 6|E−Q| = 5|U−J| denklemini sağlamaz. Q = 10,234 AU konunca sol taraf "
    f"6×|{E:.5f} − {Q1m:.5f}| = {6*abs(E-Q1m):.4f}, sağ taraf {5*abs(U-J):.4f} çıkıyor (sapma "
    f"%{abs(6*abs(E-Q1m)-5*abs(U-J))/(5*abs(U-J))*100:.1f}). Çünkü denklemin çözümü Q = E ± S'dir; E − S'nin "
    "işaretini değiştirmek (S − E) denklemin çözümü değildir. Mesafe negatif olamayacağı için denklemin tek fiziksel "
    "çözümü Q2 = E + S'dir. Bu bölüm yalnızca 'mutlak değer alınsaydı ne çıkardı' sorusunu cevaplamak için verildi.")

R.kaydet("01_H1_dogrulama")
print("\n|Q1| =", Q1m); print(q1_sag.to_string()); print(q1_es.to_string()); print(q1_yakin.to_string())

print(f"E={E} U={U} J={J}  S={S:.6f}  Q1={Q1:.6f}  Q2={Q2:.6f}")
print(es[["Cisim", "Q mesafesi (AU)", "Sapma: |Q−Qhedef|/Qhedef (%)", "Sapma: |sol−sağ|/sağ (%)"]].to_string())
print(saglama_b.to_string()); print(saglama_c.to_string()); print(bant.to_string())
