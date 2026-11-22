# -*- coding: utf-8 -*-
"""Faz 2 ortak araçlar: veri yükleme (salt okunur), önbellek, sapma metrikleri."""
import glob, os, pickle, re
import numpy as np
import pandas as pd

KOK = os.path.dirname(os.path.abspath(__file__))
SONUC = os.path.join(KOK, "faz2_sonuclar")
CACHE = os.path.join(SONUC, "cache")
os.makedirs(CACHE, exist_ok=True)

WOW = "1977-08-15"
KONTROL_KLASOR = os.path.join(KOK, "orjinal tarihler dosyalar", "10 farklı gün")

# Yazarın veritabanına giren kategorilerle aynı sayfalar
SAYFALAR = ["Asteroids (Unique)", "Planets", "Natural Satellites",
            "Dwarf Planets", "Artificial Satellites"]
HARFLER = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def tarih_dosyalari(tarih):
    """{harf: xlsx yolu} döndürür."""
    if tarih == WOW:
        files = glob.glob(os.path.join(KOK, "?_solar_system_objects*.xlsx"))
    else:
        d = [p for p in glob.glob(os.path.join(KONTROL_KLASOR, "*")) if p.endswith(tarih)]
        assert len(d) == 1, (tarih, d)
        files = glob.glob(os.path.join(d[0], "?_*.xlsx"))
    out = {os.path.basename(f)[0]: f for f in files}
    assert sorted(out) == HARFLER, (tarih, sorted(out))
    return out


def kontrol_tarihleri():
    t = []
    for p in glob.glob(os.path.join(KONTROL_KLASOR, "*")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})$", p)
        if m:
            t.append(m.group(1))
    return sorted(t)


def harf_yukle(path):
    """Bir harf dosyasından (isim, sayfa, mesafe) listesi; mesafesi olmayanlar atılır."""
    x = pd.ExcelFile(path)
    isim, sayfa, mes = [], [], []
    for s in SAYFALAR:
        if s not in x.sheet_names:
            continue
        d = x.parse(s)
        col = [c for c in d.columns if str(c).startswith("Instant_Sun_Dist")]
        if not col:
            continue
        v = pd.to_numeric(d[col[0]], errors="coerce")
        ok = v.notna() & np.isfinite(v)
        isim += d.loc[ok, "Object"].astype(str).tolist()
        sayfa += [s] * int(ok.sum())
        mes += v[ok].astype(float).tolist()
    return {"isim": np.array(isim, dtype=object), "sayfa": np.array(sayfa, dtype=object),
            "d": np.array(mes, dtype=float)}


def tarih_yukle(tarih):
    """Bir tarihin 26 harfini önbellekli yükler."""
    cp = os.path.join(CACHE, f"veri_{tarih}.pkl")
    if os.path.exists(cp):
        with open(cp, "rb") as f:
            return pickle.load(f)
    veri = {h: harf_yukle(p) for h, p in tarih_dosyalari(tarih).items()}
    with open(cp, "wb") as f:
        pickle.dump(veri, f)
    return veri


DITHER = os.environ.get("DITHER") == "1"


def titret(v):
    """6 ondalık yuvarlamayı gidermek için her mesafeye +-0,5e-6 AU düzgün gürültü (harf başına sabit tohum).
    Dünya ayrıca v["_E"] olarak döner."""
    E = gezegen(v, "Earth")
    if not DITHER:
        v = dict(v); v["_E"] = E; return v
    out = {}
    for i, h in enumerate(HARFLER):
        rng = np.random.default_rng(1000 + i)
        out[h] = dict(v[h]); out[h]["d"] = v[h]["d"] + rng.uniform(-5e-7, 5e-7, len(v[h]["d"]))
    out["_E"] = E + np.random.default_rng(999).uniform(-5e-7, 5e-7)
    return out


def gezegen(veri, ad):
    for h in HARFLER:
        v = veri[h]
        m = (v["sayfa"] == "Planets") & (v["isim"] == ad)
        if m.any():
            return float(v["d"][m][0])
    raise KeyError(ad)


GEZEGENLER = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]


# ---------------------------------------------------------------- metrikler
ESIK = 1.5          # makaledeki H2 eşiği (%)
YEREL = 0.15        # yerel yoğunluk penceresi (%), eşiğin onda biri
K_ILK = 30          # "uçurum" aranan ilk sıra sayısı


def metrikler(devs_kucuk, n_esik):
    """devs_kucuk: en küçük (en az K_ILK+1) sapmalar (%) sıralı; n_esik: <=%1,5 sayısı.
    Ortalama aralık yerel yoğunluktan (<=%0,15) hesaplanır."""
    s = np.sort(np.asarray(devs_kucuk, float))
    n_yerel = int((s <= YEREL).sum()) if len(s) and s[-1] > YEREL else None
    return s, n_yerel


def ozet(s_tum_kucuk, n_esik, n_yerel):
    """s_tum_kucuk: en küçük sapmalar (sıralı, en az 31 adet ideal)."""
    s = np.sort(np.asarray(s_tum_kucuk, float))
    r = {"n_esik": int(n_esik), "n_yerel": int(n_yerel)}
    if n_yerel < 30 or len(s) < 9:
        r["guvenilir"] = False
        return r
    aralik = YEREL / n_yerel                     # ortalama aralık (%)
    r["guvenilir"] = True
    r["ort_aralik"] = aralik
    r["min"] = s[0]
    r["sekizinci"] = s[7]
    r["min_norm"] = s[0] / aralik                # beklenen ~1
    r["sekizinci_norm"] = s[7] / aralik          # beklenen ~8
    r["n_0001"] = int((s <= 0.001).sum()) if s[-1] > 0.001 else None
    r["n_0001_beklenen"] = 0.001 / aralik
    k = min(K_ILK, len(s) - 1)
    bosluk = np.diff(np.concatenate([[0.0], s[:k + 1]])) / aralik
    r["max_bosluk"] = float(bosluk.max())
    r["max_bosluk_sira"] = int(bosluk.argmax())  # bu sıradan sonra boşluk (0 = sıfırdan ilk değere)
    r["bosluk_8_9"] = float((s[8] - s[7]) / aralik)
    return r
