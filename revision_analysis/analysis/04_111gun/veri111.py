# -*- coding: utf-8 -*-
"""111 tarihin (Wow! + 10 + 100) Excel verisini salt okunur yükler ve önbelleğe alır.
Her tarih: DataFrame(isim, d) (mesafesi olan benzersiz cisimler) + gezegen mesafeleri."""
import glob, os, re, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402

KOK = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(KOK, "cache")
os.makedirs(CACHE, exist_ok=True)
ATLA = {"Asteroids (MPC)", "Asteroids (SBDB)"}  # Unique sayfasının alt kümeleri


def tarih_dosyalari():
    """{tarih: (pencere, [26 dosya])}"""
    out = {o.TARIH: (1, sorted(glob.glob(os.path.join(o.VERI_KLASOR, "?_objects_with_RADEC_*.xlsx"))))}
    for d in glob.glob(os.path.join(o.BULMACA, "*farklı tarih *")):
        t = re.search(r"(\d{4}-\d{2}-\d{2})$", d).group(1)
        out[t] = (10, sorted(glob.glob(os.path.join(d, "?_*.xlsx"))))
    yuz = {}
    for f in glob.glob(os.path.join(o.BULMACA, "100 farklı tarih", "*", "AstroData*", "?_solar_system_objects_*.xlsx")):
        t = re.search(r"(\d{4}-\d{2}-\d{2})\.xlsx$", f).group(1)
        yuz.setdefault(t, []).append(f)
    for t, fs in yuz.items():
        out[t] = (100, sorted(fs))
    for t, (w, fs) in out.items():
        assert len(fs) == 26 and len({os.path.basename(f)[0] for f in fs}) == 26, (t, len(fs))
    assert sum(1 for v in out.values() if v[0] == 10) == 10 and sum(1 for v in out.values() if v[0] == 100) == 100
    return out


def _yukle(args):
    t, fs = args
    cp = os.path.join(CACHE, f"{t}.pkl")
    if os.path.exists(cp):
        return t
    isim, mes, sayfa = [], [], []
    for f in fs:
        x = pd.ExcelFile(f)
        for s in x.sheet_names:
            if s in ATLA:
                continue
            d = x.parse(s)
            col = [c for c in d.columns if str(c).startswith("Instant_Sun_Dist")]
            if not col or "Object" not in d.columns:
                continue
            v = pd.to_numeric(d[col[0]], errors="coerce")
            ok = v.notna() & np.isfinite(v)
            isim += d.loc[ok, "Object"].astype(str).tolist(); mes += v[ok].tolist(); sayfa += [s] * int(ok.sum())
    df = pd.DataFrame({"isim": isim, "d": mes, "sayfa": sayfa}).drop_duplicates("isim").reset_index(drop=True)
    df.to_pickle(cp)
    return t


def db_tamamlama():
    """bigdata.db (makaledeki analizin kaynağı): Excel'de boş kalan mesafeler için. Salt okunur."""
    import sqlite3, pathlib
    cp = os.path.join(CACHE, "bigdata_db.pkl")
    if os.path.exists(cp):
        return pd.read_pickle(cp)
    c = sqlite3.connect(pathlib.Path(o.BIGDATA_DB).as_uri() + "?mode=ro", uri=True)
    db = pd.read_sql_query('select "Object ID" isim, Date, "Instant_Sun_Dist_AU" d from solar_objects', c)
    c.close()
    db["d"] = pd.to_numeric(db.d, errors="coerce")
    db = db.dropna(subset=["d"]).drop_duplicates(["isim", "Date"])
    db.to_pickle(cp)
    return db


def hepsini_yukle(paralel=8, tamamla=True):
    tf = tarih_dosyalari()
    eksik = [(t, fs) for t, (w, fs) in tf.items() if not os.path.exists(os.path.join(CACHE, f"{t}.pkl"))]
    if eksik:
        t0 = time.time()
        with ProcessPoolExecutor(paralel) as ex:
            for i, t in enumerate(ex.map(_yukle, eksik), 1):
                print(f"[{i}/{len(eksik)}] {t}  ({time.time()-t0:.0f} s)", flush=True)
    veri = {}
    db = db_tamamlama() if tamamla else None
    for t, (w, _) in sorted(tf.items()):
        df = pd.read_pickle(os.path.join(CACHE, f"{t}.pkl"))
        if db is not None:
            ek = db[(db.Date == t) & ~db.isim.isin(df.isim)]
            ek = ek.assign(sayfa=np.where(ek.isim.isin(o.GEZEGENLER), "Planets", "bigdata.db"))[["isim", "d", "sayfa"]]
            df = pd.concat([df, ek], ignore_index=True)
        p = df[df.sayfa == "Planets"].set_index("isim")["d"]
        veri[t] = {"pencere": w, "df": df, "P": {g: float(p[g]) for g in o.GEZEGENLER if g in p},
                   "db_eklenen": len(ek) if db is not None else 0}
    return veri


if __name__ == "__main__":
    v = hepsini_yukle()
    for t, x in v.items():
        print(t, x["pencere"], len(x["df"]), "E=%.5f J=%.5f U=%.5f" % (x["P"]["Earth"], x["P"]["Jupiter"], x["P"]["Uranus"]))
