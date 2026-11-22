# -*- coding: utf-8 -*-
"""Faz 3: 1001 formül (yazar + 1000 rastgele) × H1, H2, H3, zaman."""
import json, os, time
import numpy as np, pandas as pd
from scipy import stats
from concurrent.futures import ProcessPoolExecutor
os.environ["DITHER"] = "1"
import faz2_ortak as o, faz2_motor as m
from faz3_formuller import DOSYA, derle

CIKTI = os.path.join(o.KOK, "faz3_sonuclar")
G = {}


def baslat():
    tarihler = [o.WOW] + o.kontrol_tarihleri()
    # H1 verisi: her tarih için tüm benzersiz cisimler + E,U,J gezegenleri (ham veri)
    G["h1"] = {}
    for t in tarihler:
        v = o.tarih_yukle(t)
        isim = np.concatenate([v[h]["isim"] for h in o.HARFLER]); d = np.concatenate([v[h]["d"] for h in o.HARFLER])
        isim, k = np.unique(isim, return_index=True)
        G["h1"][t] = (isim, d[k], *(o.gezegen(v, g) for g in ["Earth", "Uranus", "Jupiter"]))
    # H2 verisi: yazarın verisi (titreşimli) ve sinyal anı (yazarın biçimi + Horizons farkı)
    v = o.tarih_yukle(o.WOW); vt = o.titret(v)
    G["isim"] = {h: v[h]["isim"] for h in "QUJ"}
    G["h2_yazar"] = (vt["_E"], vt["Q"]["d"], vt["U"]["d"], vt["J"]["d"])
    s = json.load(open(o.CACHE + "/horizons_iki_an.json", encoding="utf-8"))
    def sinyal(h): return np.array([d + s[f"{h}|{n}"]["r"][1] - s[f"{h}|{n}"]["r"][0] for n, d in zip(v[h]["isim"], v[h]["d"])])
    Er = s["E|Earth"]["r"]
    G["h2_sinyal"] = (o.gezegen(v, "Earth") + Er[1] - Er[0], sinyal("Q"), sinyal("U"), sinyal("J"))
    el = json.load(open(o.CACHE + "/sbdb_elemanlar.json", encoding="utf-8"))
    G["a"] = {k: float(x["a"]) for k, x in el.items() if "a" in x and x["a"]}


def h2(f, veri):
    r = m.tara(f, *veri)
    oz = o.ozet(r["kucuk"], r["n_esik"], r["n_yerel"])
    top8 = [(G["isim"]["Q"][qi], G["isim"]["U"][ui], G["isim"]["J"][ji]) for qi, ui, ji, _ in r["idx"][:8]]
    return oz, top8


def is_(fm):
    L, R = derle(fm["sol"]), derle(fm["sag"])
    f = lambda E, Q, U, J: (L(E, Q, U, J), R(E, Q, U, J))
    out = {"id": fm["id"], "formul": fm["sol"] + " = " + fm["sag"]}
    # ---- H1
    for t, (isim, Q, E, U, J) in G["h1"].items():
        with np.errstate(all="ignore"):
            d = np.abs(L(E, Q, U, J) - R(E, Q, U, J)) / np.abs(R(E, Q, U, J)) * 100
        d = np.broadcast_to(d, Q.shape); ok = np.nonzero(np.isfinite(d) & (d <= 1.0))[0]
        out[f"h1_{t}"] = len(ok)
        if t == o.WOW:
            out["h1_1977_isimler"] = "; ".join(isim[i] for i in ok[np.argsort(d[ok])][:5])
            out["h1_thereus"] = any("Thereus" in isim[i] for i in ok)
            out["h1_en_iyi_sapma"] = float(np.nanmin(np.where(np.isfinite(d), d, np.inf)))
    # ---- H2 (yazarın verisi) + zaman
    oz, top8 = h2(f, G["h2_yazar"])
    out.update({f"h2_{k}": v for k, v in oz.items()})
    oz_s, top8_s = h2(f, G["h2_sinyal"])
    out["h2s_sekizinci_norm"] = oz_s.get("sekizinci_norm"); out["h2s_max_bosluk"] = oz_s.get("max_bosluk")
    out["zaman_top8_korunan"] = len(set(top8) & set(top8_s))
    # ---- H3
    objs = {n for t in top8 for n in t}
    a = [G["a"][n] for n in objs if n in G["a"]]
    out["h3_truva"] = sum(5.05 <= x <= 5.35 for x in a); out["h3_hilda"] = sum(3.7 <= x <= 4.2 for x in a)
    out["h3_hikaye"] = out["h3_truva"] > 0 and out["h3_hilda"] > 0
    out["top8"] = " || ".join(" | ".join(t) for t in top8)
    return out


if __name__ == "__main__":
    t0 = time.time()
    fs = json.load(open(DOSYA, encoding="utf-8"))
    with ProcessPoolExecutor(6, initializer=baslat) as ex:
        res = list(ex.map(is_, fs, chunksize=8))
    df = pd.DataFrame(res); df.to_csv(CIKTI + "/faz3_ham.csv", index=False, encoding="utf-8-sig")
    print("süre %.0f s, formül %d" % (time.time() - t0, len(df)))
