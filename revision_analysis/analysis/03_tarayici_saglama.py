# -*- coding: utf-8 -*-
"""İŞ 3: Tarayıcıdaki Claude tablosunun (tablosonuc.png) sağlaması.
Tarayıcı, harflere Big Ear sinyal değerlerini (S/N) koymuş: 6, E=14, Q=26, U=30, J=19, 5.
Çıkan sayıyı 'en yakın cisim' ile (en küçük yüzde sapma) karşılaştırmış. İlk satır ise AU ile hesaplanmış."""
import numpy as np
import pandas as pd
import ortak as o

np.seterr(all="ignore")
I = lambda x: x
SN = {"E": 14, "Q": 26, "U": 30, "J": 19}  # Big Ear: A=10 … Z=35

FORMULLER = [
    ("F1", "(6+E+Q)−(U+J+5)",    lambda E, Q, U, J: (6 + E + Q) - (U + J + 5)),
    ("F2", "(toplam/6)−5",       lambda E, Q, U, J: (6 + E + Q + U + J + 5) / 6 - 5),
    ("F3", "(6+5)×(Q−E)/(U+J)",  lambda E, Q, U, J: (6 + 5) * (Q - E) / (U + J)),
    ("F4", "√(6×5)+(Q−E)/(U−J)", lambda E, Q, U, J: np.sqrt(6 * 5) + (Q - E) / (U - J)),
    ("F5", "(Q×E)/(U+J)",        lambda E, Q, U, J: (Q * E) / (U + J)),
    ("F6", "(U−6)−(Q−J)+(E−5)",  lambda E, Q, U, J: (U - 6) - (Q - J) + (E - 5)),
    ("F7", "(6×J)/(U−Q)+E/5",    lambda E, Q, U, J: (6 * J) / (U - Q) + E / 5),
    ("F8", "(U+6)/(Q−5)×E/J",    lambda E, Q, U, J: (U + 6) / (Q - 5) * E / J),
    ("F9", "((Q+U)/(J+6))−5",    lambda E, Q, U, J: ((Q + U) / (J + 6)) - 5),
    ("F10", "(E×5)−(Q−U)/(J−6)", lambda E, Q, U, J: (E * 5) - (Q - U) / (J - 6)),
]
PNG = {  # tablosonuc.png: (değer, en yakın, sapma %)
    "F1": (8.0000, "Satürn", 12.85), "F2": (11.6667, "Thereus", 5.62), "F3": (2.6939, "Ana kuşak", 3.79),
    "F4": (6.5681, "Satürn", 28.45), "F5": (7.4286, "Satürn", 19.08), "F6": (26.0000, "Neptün", 14.17),
    "F7": (31.3000, "Neptün", 3.33), "F8": (1.2632, "Mars", 13.10), "F9": (-2.7600, "Neptün", 109.11),
    "F10": (70.3077, "Neptün", 132.10),
}

df = o.veri_yukle()
P = o.gezegenler(df)
gercek = {o.GEZEGEN_TR[g]: P[g] for g in o.GEZEGENLER}
# Tarayıcının referans listesi: png'de görünen değerler + görünmeyen gezegenler için gerçek değerler
tarayici_ref = dict(gercek)
tarayici_ref.update({"Mars": 1.4535, "Satürn": 9.1797, "Neptün": 30.2917, "Ana kuşak": 2.8, "Thereus": 12.3610})


def en_yakin(v, ref):
    s = {k: abs(v - d) / d * 100 for k, d in ref.items()}
    k = min(s, key=s.get)
    return k, ref[k], s[k]


# ---------------------------------------------------------------- 1) değerlerin sağlaması
rows, karsi = [], []
for kod, yazim, f in FORMULLER:
    v = float(f(SN["E"], SN["Q"], SN["U"], SN["J"]))
    pv, pk, ps = PNG[kod]
    # tarayıcı F1'de sonucu mutlak almış (−8 → 8); aynı kuralla karşılaştırma için ikisini de dene
    v_tar = abs(v) if (np.isclose(abs(v), pv, atol=5e-5) and not np.isclose(v, pv, atol=5e-5)) else v
    k, d, s = en_yakin(v_tar, tarayici_ref)
    kg, dg, sg = en_yakin(v_tar, gercek)
    rows.append({"Formül": kod, "İfade": yazim,
                 "Açık hesap (S/N)": yazim.replace("E", "14").replace("Q", "26").replace("U", "30").replace("J", "19")
                                         .replace("toplam", "(6+14+26+30+19+5)"),
                 "Hesaplanan değer": v, "PNG değeri": pv, "Değer tutuyor mu": bool(np.isclose(v_tar, pv, atol=5e-5)),
                 "Not": "Tarayıcı işareti atmış (−8 → 8)" if v_tar != v else "",
                 "En yakın (tarayıcı listesi)": f"{k} ({d:.4f})", "Sapma (%)": s,
                 "PNG en yakın / sapma": f"{pk} / %{ps:.2f}",
                 "Sapma tutuyor mu": bool(k == pk and abs(round(s, 2) - ps) < 0.006)})
    karsi.append({"Formül": kod, "Değer (S/N)": v_tar, "Gerçek 1977 gezegenine göre en yakın": f"{kg} ({dg:.6f} AU)",
                  "Sapma (%)": sg, "±%1 içinde": sg <= 1})
T1 = pd.DataFrame(rows); T3 = pd.DataFrame(karsi)

# ---------------------------------------------------------------- 2) ilk satır (yazarın formülü, AU)
E, U, J = P["Earth"], P["Uranus"], P["Jupiter"]
qh = E + 5 / 6 * abs(U - J)
th = float(df[df.isim.str.contains("Thereus")].d.iloc[0])
T2 = pd.DataFrame([
    {"Kaynak": "Tarayıcı (kendi yaklaşık AU değerleri)", "Q hedef (AU)": 12.2645, "Thereus (AU)": 12.3610,
     "Sapma (%)": abs(12.3610 - 12.2645) / 12.2645 * 100, "PNG sapma": "%0,78"},
    {"Kaynak": "Gerçek Excel verisi (İş 1)", "Q hedef (AU)": qh, "Thereus (AU)": th,
     "Sapma (%)": abs(th - qh) / qh * 100, "PNG sapma": "—"},
])

# ---------------------------------------------------------------- 3) aynı formül, iki farklı girdi
is2 = pd.read_excel(o.os.path.join(o.CIKTI, "02_formul_testi.xlsx"), sheet_name="Özet")
is2 = is2[is2["Biçim"] == "Normal"]
T4 = []
for kod, yazim, _ in FORMULLER:
    s2 = is2[is2["Formül"] == kod]
    T4.append({"Formül": kod, "İfade": yazim,
               "Tarayıcı: harf = S/N sayısı → değer": T1.set_index("Formül").loc[kod, "Hesaplanan değer"],
               "Tarayıcı: en yakın": T1.set_index("Formül").loc[kod, "En yakın (tarayıcı listesi)"],
               "Gerçek (İş 2): eşitlik": s2["Eşitlik"].iloc[0],
               "Gerçek: Q kökü (AU)": "; ".join(f"{v:.4f}" for v in s2["Q kökü (AU)"].dropna()),
               "Gerçek: eşleşme sayısı": int(s2["Eşleşme sayısı (±%1)"].sum()),
               "Gerçek: bulunan cisimler": "; ".join(str(v) for v in s2["Bulunan cisimler"])[:200]})
T4 = pd.DataFrame(T4)

# ---------------------------------------------------------------- rapor
R = o.Rapor("İş 3 — Tarayıcı Tablosunun (tablosonuc.png) Sağlaması")
R.p("Tarayıcıdaki Claude, alternatif 10 formülde harflere Big Ear sinyal değerlerini koymuştur: "
    "6, E = 14, Q = 26, U = 30, J = 19, 5 (Big Ear kodu: A = 10 … Z = 35; birimsiz S/N, σ cinsinden). "
    "'toplam' = 6 + 14 + 26 + 30 + 19 + 5 = 100. Çıkan sayı, bir referans listesindeki cisimlerle "
    "en küçük yüzde sapmaya göre eşleştirilmiştir. Bu çalışma aynı hesabı tekrarlar ve PNG'deki her sayıyı kontrol eder.")
R.h("1. Değer ve sapma sağlaması")
R.p("Tarayıcının referans listesi PNG'de görünen değerlerden alındı (Mars 1,4535; Ana kuşak 2,8; Satürn 9,1797; "
    "Thereus 12,3610; Neptün 30,2917). Görünmeyen gezegenler için gerçek 1977 değerleri kullanıldı.")
R.t("Sağlama", T1)
n_d, n_s = int(T1["Değer tutuyor mu"].sum()), int(T1["Sapma tutuyor mu"].sum())
R.p(f"Sonuç: 10 değerin {n_d}'i ve 10 'en yakın / sapma' sonucunun {n_s}'i PNG ile birebir aynı. "
    "Yani tarayıcı tablosu, harflere sinyal sayıları konarak üretilmiştir; Q bilinmeyen değildir ve gerçek mesafe "
    "kullanılmamıştır.")
R.p("Tutarsızlık: F1'in gerçek sonucu −8'dir; tarayıcı bunu 8 olarak yazmış (işareti atmış). F9'da ise negatif "
    "sonucu (−2,76) olduğu gibi bırakmış. Aynı tabloda iki farklı kural uygulanmış.")
R.h("2. İlk satır: yazarın formülü (AU ile)")
R.t("İlk satır", T2)
R.p("İlk satır diğerlerinden farklı olarak AU ile hesaplanmıştır. %0,78 ile %0,83 arasındaki fark, tarayıcının "
    "yaklaşık gezegen değerleri kullanmasından gelir.")
R.h("3. Aynı S/N değerleri, yalnızca gerçek 1977 gezegenlerine göre")
R.t("Gerçek gezegenlerle", T3)
R.h("4. Neden karşılaştırılamaz? Aynı formül, iki farklı girdi")
R.t("S/N vs AU", T4)
R.p("Tarayıcı tablosunda ilk satırın girdisi AU (fiziksel mesafe), diğer 10 satırın girdisi birimsiz sinyal "
    "sayılarıdır (σ). Birimsiz bir sayıyı AU cinsinden bir mesafeyle karşılaştırmanın fiziksel anlamı yoktur; "
    "bu yüzden '%0,78'i diğer satırlardaki '%3,33 … %132' ile karşılaştırarak yazarın formülünün üstün olduğu "
    "sonucu çıkarılamaz. Doğru karşılaştırma İş 2'dedir: aynı girdiyle (AU), Q bilinmeyen, formüller eşitlik olarak çözülmüştür.")
R.kaydet("03_tarayici_saglama")

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 45)
print(T1[["Formül", "Hesaplanan değer", "PNG değeri", "Değer tutuyor mu", "En yakın (tarayıcı listesi)", "Sapma (%)",
          "PNG en yakın / sapma", "Sapma tutuyor mu", "Not"]].to_string())
print(T2.to_string()); print(T3.to_string())
