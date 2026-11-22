# -*- coding: utf-8 -*-
"""İŞ 7: Birleşik profil testi — yazarın formülü üç bölümün özelliklerini birlikte taşıyor mu ve bu ne kadar nadir?
Özellikler (Faz 3'teki 1.000 rastgele formül + yazarın formülü üzerinden):
  A (Bölüm 3.1 / H1): Wow! gününde ±%1 içinde tam 1 eşleşme
  B (Bölüm 3.2 / H2): ilk 31 sıradaki en büyük sapma boşluğu 8. sıradan sonra (Top 8'in 'elbow' ile ayrılması)
  C (Bölüm 3.3 / H3): Top 8'de hem Jüpiter Truvası (5,05 ≤ a ≤ 5,35) hem Hilda (3,7 ≤ a ≤ 4,2) bulunması
Profil = (H1 eşleşme sayısı: 0 / 1 / 2+, en büyük boşluğun sırası, Truva var mı, Hilda var mı).
Nadirlik = bileşenlerin marjinal sıklıklarının çarpımı (bağımsızlık varsayımı); her formülün kendi profili için hesaplanır.
İki zaman: 15.08.1977 00:00 UT (yazarın verisi) ve 16.08.1977 02:16 UT (sinyal anı).
Sinyal anında H1: 26.164 cismin her biri için 26 sa 16 dk'daki en büyük olası Güneş uzaklığı değişimi
δ = √(2,1·μ/r)·Δt (hızın fiziksel üst sınırı) ile eşleşme 'kesin içeride / kesin dışarıda / belirsiz' sınıflandırılır."""
import json, os, sys, time
import numpy as np
import pandas as pd

KOK = os.path.dirname(os.path.abspath(__file__))
ANALIZ = os.path.dirname(KOK)
sys.path.insert(0, ANALIZ)
import ortak as o  # noqa: E402

BUL = o.BULMACA
CIKTI = os.path.join(KOK, "cikti"); CACHE = os.path.join(KOK, "cache")
os.makedirs(CIKTI, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
MU = 2.9591220828559115e-04          # Güneş GM, AU^3/gün^2
DT = (26 * 60 + 16) / 1440.0         # 15.08 00:00 UT → 16.08 02:16 UT (gün)


# ------------------------------------------------------------------ profil ve nadirlik
def profil_tablosu(d, n1, sira, truva, hilda):
    """d: id sütunlu tablo; diğerleri seriler. Dönüş: profil, aynı profil sayısı, bağımsızlık nadirliği."""
    t = pd.DataFrame({"id": d["id"].values, "n1": n1.values, "sira": sira.values, "truva": truva.values, "hilda": hilda.values})
    t = t.dropna()
    t["n1k"] = t.n1.clip(upper=2).astype(int); t["sira"] = t.sira.astype(int)
    t["prof"] = list(zip(t.n1k, t.sira, t.truva.astype(bool), t.hilda.astype(bool)))
    say = t.prof.value_counts(); t["ayni_profil"] = t.prof.map(say) - 1
    pA = t.n1k.value_counts(normalize=True); pB = t.sira.value_counts(normalize=True)
    pT = t.truva.astype(bool).value_counts(normalize=True); pH = t.hilda.astype(bool).value_counts(normalize=True)
    t["nadirlik"] = [pA[a] * pB[b] * pT[x] * pH[y] for a, b, x, y in t.prof]
    return t


def ozet(t, etiket):
    y = t[t.id == "YAZAR"]; r = t[t.id != "YAZAR"]
    if not len(y):
        return {"Zaman": etiket, "Not": "Yazarın profili bu zamanda belirlenemedi"}
    y = y.iloc[0]
    A = r.n1k == 1; B = r.sira == 8; C = r.truva.astype(bool) & r.hilda.astype(bool)
    return {"Zaman": etiket, "Profili belirli rastgele formül": len(r),
            "Yazar: H1 eşleşme": int(y.n1), "Yazar: en büyük boşluk sırası": int(y.sira),
            "Yazar: Truva / Hilda": f"{bool(y.truva)} / {bool(y.hilda)}",
            "Yazar A / B / C": f"{y.n1k == 1} / {y.sira == 8} / {bool(y.truva and y.hilda)}",
            "A oranı (rastgele)": A.mean(), "B oranı": B.mean(), "C oranı": C.mean(),
            "A+B+C birlikte (rastgele sayı)": int((A & B & C).sum()),
            "Yazar profilini paylaşan rastgele": int(y.ayni_profil),
            "Yazarın nadirlik değeri": y.nadirlik,
            "Kendi profili yazarınki kadar/daha nadir rastgele oranı": float((r.nadirlik <= y.nadirlik).mean()),
            "Profili benzersiz rastgele oranı": float((r.ayni_profil == 0).mean())}


# ------------------------------------------------------------------ 00:00 UT (Faz 3 sonuçları)
def zaman_0000():
    d = pd.read_csv(os.path.join(BUL, "faz3_sonuclar", "faz3_ham.csv"))
    d = d[d.h2_guvenilir == True]
    return profil_tablosu(d, d["h1_1977-08-15"], d.h2_max_bosluk_sira, d.h3_truva > 0, d.h3_hilda > 0)


# ------------------------------------------------------------------ 02:16 UT (sinyal anı) — yeniden hesap
G = {}


def baslat():
    sys.path.insert(0, BUL)
    os.environ["DITHER"] = "1"
    import faz2_ortak as fo, faz2_motor as fm  # noqa
    G["fo"], G["fm"] = fo, fm
    v = fo.tarih_yukle(fo.WOW)
    s = json.load(open(os.path.join(BUL, "faz2_sonuclar", "cache", "horizons_iki_an.json"), encoding="utf-8"))
    fark = lambda h, n: s[f"{h}|{n}"]["r"][1] - s[f"{h}|{n}"]["r"][0]
    # H2 sinyal anı verisi: Excel mesafesi + Horizons farkı, 00:00 ile aynı titreşim (yuvarlama giderme)
    vs = {h: dict(v[h]) for h in fo.HARFLER}
    for h in "QUJ":
        vs[h]["d"] = np.array([dd + fark(h, n) for n, dd in zip(v[h]["isim"], v[h]["d"])])
    E_s = fo.gezegen(v, "Earth") + fark("E", "Earth")
    vt = fo.titret(vs); vt["_E"] = E_s + (vt["_E"] - fo.gezegen(v, "Earth"))
    G["h2"] = (vt["_E"], vt["Q"]["d"], vt["U"]["d"], vt["J"]["d"])
    G["isim"] = {h: v[h]["isim"] for h in "QUJ"}
    el = json.load(open(os.path.join(BUL, "faz2_sonuclar", "cache", "sbdb_elemanlar.json"), encoding="utf-8"))
    G["a"] = {k: float(x["a"]) for k, x in el.items() if "a" in x and x["a"]}
    # H1 sinyal anı: tüm cisimler (00:00 mesafesi) + üst sınır δ; gezegenler sinyal anında
    isim = np.concatenate([v[h]["isim"] for h in fo.HARFLER]); dd = np.concatenate([v[h]["d"] for h in fo.HARFLER])
    isim, k = np.unique(isim, return_index=True); dd = dd[k]
    G["h1"] = (dd, np.sqrt(2.1 * MU / dd) * DT, E_s, fo.gezegen(v, "Uranus") + fark("U", "Uranus"), fo.gezegen(v, "Jupiter") + fark("J", "Jupiter"))


def is_(fmx):
    sys.path.insert(0, BUL)
    from faz3_formuller import derle
    L, R = derle(fmx["sol"]), derle(fmx["sag"])
    out = {"id": fmx["id"]}
    Q, dl, E, U, J = G["h1"]
    with np.errstate(all="ignore"):
        dev = lambda q: np.broadcast_to(np.abs(L(E, q, U, J) - R(E, q, U, J)) / np.abs(R(E, q, U, J)) * 100, Q.shape)
        D = np.vstack([dev(Q), dev(Q - dl), dev(Q + dl)])
    D = np.where(np.isfinite(D), D, np.inf)
    kesin = int((D.max(0) <= 1).sum()); belirsiz = int(((D.min(0) <= 1) & (D.max(0) > 1)).sum())
    out["h1s_kesin"] = kesin; out["h1s_belirsiz"] = belirsiz
    out["h1s_n"] = kesin if (min(kesin, 2) == min(kesin + belirsiz, 2)) else np.nan  # kategori (0/1/2+) belirliyse
    f = lambda E_, Q_, U_, J_: (L(E_, Q_, U_, J_), R(E_, Q_, U_, J_))
    r = G["fm"].tara(f, *G["h2"])
    oz = G["fo"].ozet(r["kucuk"], r["n_esik"], r["n_yerel"])
    out["h2s_guvenilir"] = oz.get("guvenilir", False)
    out["h2s_sira"] = oz.get("max_bosluk_sira", np.nan); out["h2s_bosluk"] = oz.get("max_bosluk", np.nan)
    top8 = [(G["isim"]["Q"][qi], G["isim"]["U"][ui], G["isim"]["J"][ji]) for qi, ui, ji, _ in r["idx"][:8]]
    a = [G["a"][n] for n in {n for t in top8 for n in t} if n in G["a"]]
    out["h3s_truva"] = sum(5.05 <= x <= 5.35 for x in a); out["h3s_hilda"] = sum(3.7 <= x <= 4.2 for x in a)
    out["top8_sinyal"] = " || ".join(" | ".join(t) for t in top8)
    return out


def zaman_0216():
    cp = os.path.join(CACHE, "sinyal_ani.csv")
    if not os.path.exists(cp):
        from concurrent.futures import ProcessPoolExecutor
        fs = json.load(open(os.path.join(BUL, "faz3_sonuclar", "formuller.json"), encoding="utf-8"))
        t0 = time.time()
        with ProcessPoolExecutor(6, initializer=baslat) as ex:
            res = list(ex.map(is_, fs, chunksize=8))
        pd.DataFrame(res).to_csv(cp, index=False, encoding="utf-8-sig")
        print("sinyal anı hesabı %.0f s" % (time.time() - t0), flush=True)
    d = pd.read_csv(cp)
    d = d[d.h2s_guvenilir == True]
    return profil_tablosu(d, d.h1s_n, d.h2s_sira, d.h3s_truva > 0, d.h3s_hilda > 0), pd.read_csv(cp)


if __name__ == "__main__":
    asama = sys.argv[1] if len(sys.argv) > 1 else "0000"
    t0 = zaman_0000()
    sonuc = {"0000": (t0, ozet(t0, "15.08.1977 00:00 UT (yazarın verisi)"))}
    if asama == "hepsi":
        t1, ham = zaman_0216()
        sonuc["0216"] = (t1, ozet(t1, "16.08.1977 02:16 UT (sinyal anı)"), ham)
    pd.to_pickle(sonuc, os.path.join(CACHE, f"profil_{asama}.pkl"))
    for k, v in sonuc.items():
        print(k, json.dumps({a: (float(b) if isinstance(b, (np.floating, float)) else b) for a, b in v[1].items()}, ensure_ascii=False, indent=1, default=str))
