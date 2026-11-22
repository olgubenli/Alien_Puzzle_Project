# -*- coding: utf-8 -*-
"""Formül 6|E−Q| = 5|U−J| hangi tarihlerde yine 32532 Thereus'u verir?
Her gün (00:00 UT) Q hedefi = E + (5/6)|U − J| (makaledeki pozitif kök) hesaplanır; Thereus'un Güneş'e uzaklığı
hedefin ±%1 içindeyse o gün 'Thereus eşleşmesi' sayılır. Uzaklıklar: JPL Horizons gözlemci tablosu, 'r' (heliosentrik
uzaklık, ışık zamanı düzeltmeli; Wow! günü Excel'leriyle aynı nicelik). Yalnız Thereus kontrol edilir; o gün başka
cisimlerin de eşleşip eşleşmediğine (tekillik) bakılmaz."""
import io, os, sys
import numpy as np
import pandas as pd
import requests

KOK = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(KOK, "cache")
API = "https://ssd.jpl.nasa.gov/api/horizons.api"
CISIM = {"E": "399", "J": "599", "U": "799", "T": "32532;"}   # gezegen merkezleri; Thereus küçük cisim
BAS, SON = "1950-01-01", "2100-12-31"


def r_cek(kod, ad):
    yol = os.path.join(CACHE, f"{ad}.csv")
    if os.path.exists(yol):
        return pd.read_csv(yol, parse_dates=["t"])
    parcalar = []
    for y0 in range(1950, 2101, 25):                       # parça parça (satır sınırı)
        y1 = min(y0 + 24, 2100)
        p = {"format": "text", "COMMAND": f"'{kod}'", "EPHEM_TYPE": "OBSERVER", "CENTER": "'500@399'",
             "START_TIME": f"'{y0}-01-01'", "STOP_TIME": f"'{y1}-12-31'", "STEP_SIZE": "'1 d'",
             "QUANTITIES": "'19'", "CSV_FORMAT": "YES", "MAKE_EPHEM": "YES", "OBJ_DATA": "NO"}
        if ad == "E":                                      # Dünya'nın Güneş'e uzaklığı: Güneş'ten Dünya vektörü
            p.update({"EPHEM_TYPE": "VECTORS", "CENTER": "'500@10'", "VEC_TABLE": "'4'", "OUT_UNITS": "'AU-D'", "QUANTITIES": None})
        t = requests.get(API, params={k: v for k, v in p.items() if v is not None}, timeout=120).text
        g = t[t.index("$$SOE") + 5:t.index("$$EOE")].strip().splitlines()
        for s in g:
            a = [x.strip() for x in s.split(",")]
            if ad == "E":   # JDTDB, takvim, X, Y, Z, LT, RG (uzaklık), RR
                parcalar.append((a[1].replace("A.D. ", "")[:11], float(a[6])))
            else:           # tarih, _, _, r, rdot
                parcalar.append((a[0][:11], float(a[3])))
        print(ad, y0, len(g), flush=True)
    d = pd.DataFrame(parcalar, columns=["t", "r"])
    d["t"] = pd.to_datetime(d.t, format="%Y-%b-%d")
    d.to_csv(yol, index=False)
    return d


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    R = None
    for h, k in CISIM.items():
        d = r_cek(k, h).rename(columns={"r": h})
        R = d if R is None else R.merge(d, on="t")
    R["Qhedef"] = R.E + 5 / 6 * (R.U - R.J).abs()
    R["sapma"] = (R["T"] - R.Qhedef).abs() / R.Qhedef * 100
    R["esles"] = R.sapma <= 1.0
    R.to_csv(os.path.join(KOK, "gunluk.csv"), index=False)
    w = R[R.t == "1977-08-15"].iloc[0]
    print("SAĞLAMA 1977-08-15: E %.5f U %.5f J %.5f Qhedef %.6f Thereus %.6f sapma %.3f%%" % (w.E, w.U, w.J, w.Qhedef, w["T"], w.sapma))
    # ardışık eşleşme günlerini pencerelere topla
    e = R[R.esles].copy()
    e["grup"] = (e.t.diff().dt.days != 1).cumsum()
    P = e.groupby("grup").agg(bas=("t", "min"), son=("t", "max"), gun=("t", "size"),
                              en_iyi=("sapma", "min"), en_iyi_gun=("sapma", lambda s: e.loc[s.idxmin(), "t"]))
    P.to_csv(os.path.join(KOK, "pencereler.csv"), index=False)
    pd.set_option("display.width", 200)
    print(P.to_string(index=False))
    print("Toplam eşleşme günü:", int(R.esles.sum()), "/", len(R))
