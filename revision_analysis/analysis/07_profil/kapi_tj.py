# -*- coding: utf-8 -*-
"""Üç şartın (A, B, C) yazarın Tj kapı kuralıyla yeniden sayımı — 1.000 rastgele formül (Faz 3) + 20 alternatif formül (İş 2/4/5).
A: Wow! günü (1977-08-15 00:00 UT) ±%1 içinde tam 1 eşleşme (Hipotez 1)
B: ilk 31 sıradaki en büyük sapma boşluğu 8. sıradan sonra (Hipotez 2)
C (Hipotez 3, makaledeki kapı kuralı), Top 8 cisimleri içinde:
   kapı adayı = numaralı, kararlı asteroit (kuyruklu yıldız, Centaur a > 5,5 AU, gezegen, uydu, uzay aracı değil), e < 1
   C_Tj     : ana kapı = Tj < 3 olan bir Jüpiter Truvası (5,05 ≤ a ≤ 5,35 AU) VE ara kapı = Tj < 3 olan ikinci bir kapı adayı
   C_Tj_H   : C_Tj + ara kapı ayrıca Hilda (3,7 ≤ a ≤ 4,2 AU)
   C_eski   : İş 7'deki tanım (Top 8'de a aralığına göre en az bir Truva ve bir Hilda; Tj'ye bakılmaz)
Yörünge elemanları: Faz 2 SBDB önbelleği + yazarın genişletilmiş asteroit dosyası (h2.py'deki ELEM ile aynı kaynaklar)."""
import json, os, re, sys
import numpy as np
import pandas as pd

KOK = os.path.dirname(os.path.abspath(__file__)); ANALIZ = os.path.dirname(KOK)
sys.path.insert(0, ANALIZ)
import ortak as o  # noqa: E402

BUL = o.BULMACA
CIKTI = os.path.join(KOK, "cikti"); os.makedirs(CIKTI, exist_ok=True)

ELEM = {}
for f, anah in ((os.path.join(BUL, "faz2_sonuclar", "cache", "sbdb_elemanlar.json"), "tj"),
                (os.path.join(os.path.dirname(BUL), "Alien_Puzzle_Project", "data", "genisletilmis_asteroid_db2.json"), "T_J")):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        try:
            ELEM[k] = {"a": float(v["a"]), "e": float(v["e"]), "Tj": float(v[anah])}
        except Exception:
            pass


def kapi_adayi(isim):
    e = ELEM.get(isim)
    if e is None or not re.match(r"^\d+ ", isim) or re.match(r"^\d+[PDI]/", isim):
        return None
    if not (e["e"] < 1 and e["a"] <= 5.5):
        return None
    return e


def C_degerlendir(isimler):
    """Top 8'in tekil cisimleri → (C_Tj, C_Tj_H, ana kapı, ara kapı, elemanı eksik cisim sayısı)"""
    tek = sorted(set(isimler))
    eksik = sum(1 for x in tek if x not in ELEM and re.match(r"^\d+ ", x))
    ad = [(x, kapi_adayi(x)) for x in tek]
    ad = [(x, e) for x, e in ad if e and e["Tj"] < 3]
    truva = [(x, e) for x, e in ad if 5.05 <= e["a"] <= 5.35]
    best = None; best_h = None
    for x, e in truva:
        digerleri = [(y, f) for y, f in ad if y != x]
        if digerleri and best is None:
            ara = max(digerleri, key=lambda t: t[1]["Tj"])            # Tj ≈ 3'e en yakın (3'ün altında)
            best = (x, ara[0])
        hil = [(y, f) for y, f in ad if y != x and 3.7 <= f["a"] <= 4.2]
        if hil and best_h is None:
            best_h = (x, max(hil, key=lambda t: t[1]["Tj"])[0])
    return (best is not None, best_h is not None, (best or best_h or ("", ""))[0], (best or ("", ""))[1], eksik)


# ------------------------------------------------------------------ 1.000 rastgele formül + yazar (Faz 3)
d = pd.read_csv(os.path.join(BUL, "faz3_sonuclar", "faz3_ham.csv"))
satir = []
for _, r in d.iterrows():
    isimler = [n.strip() for t in str(r.top8).split("||") for n in t.split("|")] if isinstance(r.top8, str) else []
    cT, cH, ana, ara, eks = C_degerlendir(isimler) if isimler else (False, False, "", "", 0)
    satir.append({"id": r.id, "formül": r.formul, "güvenilir": bool(r.h2_guvenilir),
                  "A": r["h1_1977-08-15"] == 1, "B": r.h2_max_bosluk_sira == 8,
                  "C_Tj": cT, "C_Tj_H": cH, "C_eski": (r.h3_truva > 0) and (r.h3_hilda > 0),
                  "ana kapı": ana, "ara kapı": ara, "Top8 elemanı eksik": eks,
                  "H1 Wow": r["h1_1977-08-15"], "boşluk sırası": r.h2_max_bosluk_sira})
F3 = pd.DataFrame(satir)
Y = F3[F3.id == "YAZAR"].iloc[0]; R = F3[F3.id != "YAZAR"]


def say(T):
    out = {}
    for ad, c in (("C_Tj", "C_Tj"), ("C_Tj_H", "C_Tj_H"), ("C_eski", "C_eski")):
        out[ad] = {"A": int(T.A.sum()), "B": int(T.B.sum()), "C": int(T[c].sum()),
                   "A+B": int((T.A & T.B).sum()), "A+C": int((T.A & T[c]).sum()), "B+C": int((T.B & T[c]).sum()),
                   "A+B+C": int((T.A & T.B & T[c]).sum()), "N": len(T)}
    return out


sonuc = {"Tüm 1.000": say(R), "H2 güvenilir": say(R[R.güvenilir])}
print("YAZAR:", dict(A=Y.A, B=Y.B, C_Tj=Y.C_Tj, C_Tj_H=Y.C_Tj_H, C_eski=Y.C_eski, ana=Y["ana kapı"], ara=Y["ara kapı"]))
for k, v in sonuc.items():
    print("\n==", k)
    print(pd.DataFrame(v).T.to_string())
print("\nTop 8'de elemanı eksik numaralı cisim içeren formül:", int((R["Top8 elemanı eksik"] > 0).sum()))
for c in ("C_Tj", "C_Tj_H"):
    print(f"\n{c} sağlayan rastgele formüller (ilk 15):")
    print(R[R[c]][["id", "formül", "A", "B", "H1 Wow", "boşluk sırası", "ana kapı", "ara kapı"]].head(15).to_string(index=False))
iki = R[(R.A & R.B) | (R.A & R.C_Tj) | (R.B & R.C_Tj)]
print("\nÜç şarttan ikisini (C_Tj ile) sağlayan rastgele formüller:", len(iki))
print(iki[["id", "formül", "A", "B", "C_Tj", "H1 Wow", "boşluk sırası", "ana kapı", "ara kapı"]].to_string(index=False))

# ------------------------------------------------------------------ 20 alternatif formül (İş 4 / İş 5)
sys.path.insert(0, os.path.join(ANALIZ, "05_h2"))
import h2  # noqa: E402
oz, tops = pd.read_pickle(os.path.join(ANALIZ, "05_h2", "cache", "ozet.pkl"))
es = pd.read_excel(os.path.join(ANALIZ, "04_111gun", "cikti", "04_111gun_karsilastirma.xlsx"), "Eşleşme sayıları")
wow = dict(zip(es.Formül.replace({"Ref-makale": "Ref"}), es["1 gün"]))
alt = []
for kod in h2.KODLAR:
    z = np.load(os.path.join(ANALIZ, "05_h2", "cache", f"{kod}.npz")); ix = z["ix"]
    isim = list(h2.Qn[ix[:8, 0]]) + list(h2.Un[ix[:8, 1]]) + list(h2.Jn[ix[:8, 2]])
    cT, cH, ana, ara, eks = C_degerlendir(isim)
    sira = oz.loc[oz.Formül == kod, "En büyük boşluğun yeri (… sıradan sonra)"].iloc[0]
    alt.append({"Formül": kod, "Eşitlik": h2.YAZIM[kod], "Wow! günü eşleşme": wow.get(kod), "A": wow.get(kod) == 1,
                "Boşluk sırası": sira, "B": sira == 8, "C_Tj": cT, "C_Tj_H": cH, "ana kapı": ana, "ara kapı": ara,
                "Top8 elemanı eksik": eks})
ALT = pd.DataFrame(alt); ALT["Şart sayısı (C_Tj)"] = ALT[["A", "B", "C_Tj"]].sum(1)
print("\n== 20 alternatif + Ref")
print(ALT.drop(columns=["Eşitlik"]).to_string(index=False))

with pd.ExcelWriter(os.path.join(CIKTI, "kapi_tj_uc_sart.xlsx")) as w:
    pd.DataFrame([{"Tanım": __doc__}]).to_excel(w, "Açıklama", index=False)
    for k, v in sonuc.items():
        pd.DataFrame(v).T.to_excel(w, k[:30])
    ALT.to_excel(w, "20 alternatif", index=False)
    F3.to_excel(w, "1000 rastgele (ham)", index=False)
pd.to_pickle({"sonuc": sonuc, "alt": ALT, "ham": F3}, os.path.join(KOK, "cache", "kapi_tj.pkl"))
