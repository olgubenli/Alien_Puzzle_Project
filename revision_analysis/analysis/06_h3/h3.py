# -*- coding: utf-8 -*-
"""İŞ 6: Makale Bölüm 3.3 (Hipotez 3) analizlerinin 15 formülün kendi elbow grupları üzerinde tekrarı.
Yazarın kodlarıyla aynı mantık (yenimatrisgunceldb.py, k7top5icin.py, thereushedef6maliyet.py):
  - Maliyet = 1|Δa| + 5|Δe| + 10|Δi(°)| + 2|ΔTj|   (normalizasyon yok, kodda olduğu gibi)
  - Ağ: Dünya(399) → her eşleşmenin Q cismi; eşleşme içinde Q→U→J (tek yönlü);
        farklı eşleşmelerdeki cisimler arasında çift yönlü 'serbest uçuş'. Elemanı eksik cisim içeren eşleşme atlanır.
  - Top 5: Dijkstra + budama (her turda rotanın ilk durağı silinir)
  - Stres testi: k = 1…7 grup; grup büyüklüğü = formülün elbow sayısı (yazarın formülünde 8)
  - Kapılar (elbow grubundan): ana = Tj<3 içinde Jüpiter Truvası (5,05≤a≤5,35) varsa Tj'si en küçük olan, yoksa Tj en küçük;
        ara = kalan Tj≤3 cisimler içinde Tj'si 3'e en yakın
  - Tablo S14: formülün tüm eşleşmelerinde Tj<3 olan yeni cisimler
  - Tablo S15 / Fig. 8: her Tj<3 kapı için rota = ağda Dünya→kapı en ucuz yol + kapı→hedef doğrudan maliyet;
        MT = 15.08.1977 konumları arasındaki Öklid mesafeleri toplamı (Horizons), FT = toplam maliyet, EFF = FT/MT"""
import json, os, sys, warnings, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

warnings.filterwarnings("ignore"); np.seterr(all="ignore")
KOK = os.path.dirname(os.path.abspath(__file__))
ANALIZ = os.path.dirname(KOK)
sys.path.insert(0, ANALIZ); sys.path.insert(0, os.path.join(ANALIZ, "05_h2"))
import ortak as o  # noqa: E402
import h2  # noqa: E402  (Q/U/J havuzu, yörünge elemanları, eşitlikler)

CIKTI = os.path.join(KOK, "cikti"); CACHE = os.path.join(KOK, "cache")
os.makedirs(CIKTI, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
W = np.array([1.0, 5.0, 10.0, 2.0])
EARTH = "399"
EL = dict(h2.ELEM)
EL[EARTH] = {"a": 1.0, "e": 0.0167, "i": 0.0, "Tj": 6.138}                   # yazarın kodundaki değerler
THEREUS = "32532 Thereus (2001 PT13)"
EL[THEREUS] = {"a": 10.63837380077479, "e": 0.1975930743332117, "i": 20.36740974623941, "Tj": 3.117}
def _tj(a, e, i):
    aJ = 5.2026
    return aJ / a + 2 * np.cos(np.radians(i)) * np.sqrt(abs(a * (1 - e * e)) / aJ)


# Havuzda elemanı eksik 11 cisim: gezegenler (JPL ortalama elemanlar), uydular (ait oldukları gezegen), diğerleri SBDB
GEZ = {"Jupiter": (5.2026, 0.0484, 1.303), "Uranus": (19.1913, 0.0472, 0.773), "Saturn": (9.5371, 0.0539, 2.485)}
UYDU = {"Umbriel": "Uranus", "Janus": "Saturn", "Jarnsaxa": "Saturn"}
EKSIK_NOT = {}


def eksikleri_tamamla():
    for h in "QUJ":
        for x in h2.HAV[h].isim:
            if x in EL:
                continue
            if x in GEZ or x in UYDU:
                a, e, i = GEZ[UYDU.get(x, x)]
                EL[x] = {"a": a, "e": e, "i": i, "Tj": _tj(a, e, i)}
                EKSIK_NOT[x] = "Gezegen ortalama elemanları" if x in GEZ else f"Uydu: {UYDU[x]} yörüngesi"
            else:
                try:
                    EL[x] = {k: v for k, v in sbdb_hedef(x).items() if k in ("a", "e", "i", "Tj")}; EKSIK_NOT[x] = "SBDB"
                except Exception as ex:
                    EKSIK_NOT[x] = f"Bulunamadı: {ex}"[:80]


def kapi_adayi(x):
    """Makale: kapılar kararlı yörüngeli asteroitlerden seçilir (kuyruklu yıldız / Centaur / gezegen / uydu değil)."""
    return x != EARTH and x.split(" ")[0].isdigit() and "/" not in x and EL[x]["e"] < 1 and EL[x]["a"] <= 5.5


FORMULLER = ["Ref", "F1", "F2", "F3", "F4", "F4-mutlak", "F5", "F6", "F6-mutlak", "F7", "F7-mutlak", "F8", "F9", "F10", "F10-mutlak"]
OZ5, _ = pd.read_pickle(os.path.join(ANALIZ, "05_h2", "cache", "ozet.pkl"))
ELBOW = dict(zip(OZ5["Formül"], OZ5["En büyük boşluğun yeri (… sıradan sonra)"].astype(int)))
# Formülün kendi H1 hedefi (İş 4, Wow! günü tek doğal cisim)
KENDI_HEDEF = {"Ref": THEREUS, "F5": "C/1968 N1 (Honda)", "F7": "C/1877 G2 (Swift)", "F7-mutlak": "C/1877 G2 (Swift)",
               "F8": "C/1863 T1 (Baeker)", "F10": "C/1973 A1 (Heck-Sause)"}
plt.rcParams.update({"font.size": 9})


def sv(x):
    return np.array([EL[x]["a"], EL[x]["e"], EL[x]["i"], EL[x]["Tj"]])


def maliyet(x, y):
    return float(np.sum(W * np.abs(sv(x) - sv(y))))


# ------------------------------------------------------------------ SBDB: kendi hedefler (kuyruklu yıldızlar)
def sbdb_hedef(ad):
    cp = os.path.join(CACHE, "sbdb_hedef.json")
    c = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    if ad not in c:
        d = requests.get("https://ssd-api.jpl.nasa.gov/sbdb.api", params={"sstr": ad.split(" ")[0] if ad.split(" ")[0].isdigit() else ad.split(" (")[0]}, timeout=60).json()
        el = {e["name"]: e["value"] for e in d["orbit"]["elements"]}
        a, e, i, q = float(el["a"]), float(el["e"]), float(el["i"]), float(el["q"])
        tj = d["orbit"].get("t_jup")
        p = q * (1 + e); aJ = 5.2026
        tj_h = aJ / a + 2 * np.cos(np.radians(i)) * np.sqrt(p / aJ)       # Tisserand (a<0 için de tanımlı)
        c[ad] = {"a": a, "e": e, "i": i, "Tj": float(tj) if tj else tj_h, "Tj_kaynak": "SBDB" if tj else "hesaplandı", "q": q}
        json.dump(c, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return c[ad]


# ------------------------------------------------------------------ Horizons: 15.08.1977 konum + elemanlar
HCP = os.path.join(CACHE, "horizons.json")
HOR = json.load(open(HCP, encoding="utf-8")) if os.path.exists(HCP) else {}


def _komut(ad):
    if ad == EARTH:
        return "399"
    bas = ad.split(" ")[0]
    if bas.isdigit():
        return f"{bas};"
    if ad.startswith(("C/", "P/")):
        return f"DES={ad.split(' (')[0]};CAP;"
    return ad.split(" (")[0]


def _hor(ad):
    base = {"format": "json", "COMMAND": f"'{_komut(ad)}'", "CENTER": "'500@10'", "START_TIME": "'1977-08-15'",
            "STOP_TIME": "'1977-08-16'", "STEP_SIZE": "'1d'", "REF_PLANE": "'ECLIPTIC'", "OUT_UNITS": "'AU-D'", "OBJ_DATA": "'NO'"}
    out = {}
    for tip in ("VECTORS", "ELEMENTS"):
        for deneme in range(3):
            try:
                r = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params={**base, "EPHEM_TYPE": tip, "VEC_TABLE": "'1'"}, timeout=90).json()
                txt = r.get("result", ""); blok = txt.split("$$SOE")[1].split("$$EOE")[0]
                if tip == "VECTORS":
                    sat = blok.split("\n")
                    xyz = [l for l in sat if " X =" in l or l.strip().startswith("X =")][0]
                    v = xyz.replace("X =", "").replace("Y =", "").replace("Z =", "").split()
                    out["xyz"] = [float(v[0]), float(v[1]), float(v[2])]
                else:
                    import re
                    g = {k: float(re.search(rf"\b{k}\s*=\s*([-\d.E+]+)", blok).group(1)) for k in ("EC", "IN", "OM", "W", "A", "MA")}
                    out["el"] = g
                break
            except Exception as ex:
                out[f"hata_{tip}"] = str(ex)[:120]; time.sleep(2)
    return ad, out


def horizons(adlar):
    eksik = [a for a in set(adlar) if a not in HOR or "xyz" not in HOR[a]]
    if eksik:
        print(f"Horizons: {len(eksik)} cisim çekiliyor...", flush=True)
        for tur in range(4):
            with ThreadPoolExecutor(2) as ex:
                for ad, out in ex.map(_hor, eksik):
                    if "xyz" in out or ad not in HOR:
                        HOR[ad] = out
            eksik = [a for a in eksik if "xyz" not in HOR.get(a, {})]
            if not eksik:
                break
            time.sleep(10)
        json.dump(HOR, open(HCP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def xyz(ad):
    return np.array(HOR.get(ad, {}).get("xyz", [np.nan] * 3))


def mt(yol):
    p = [xyz(x) for x in yol]
    return float(sum(np.linalg.norm(p[i + 1] - p[i]) for i in range(len(p) - 1)))


# ------------------------------------------------------------------ ağ
class Ag:
    def __init__(self, ix):
        """ix: (m,3) Q,U,J indeksleri (h2 havuzu); elemanı eksik cisim içeren eşleşmeler atlanır."""
        Qn, Un, Jn = h2.Qn, h2.Un, h2.Jn
        isim = np.c_[Qn[ix[:, 0]], Un[ix[:, 1]], Jn[ix[:, 2]]]
        ok = np.array([all(x in EL for x in r) for r in isim]) if len(isim) else np.zeros(0, bool)
        self.atlanan = int((~ok).sum()); isim = isim[ok]; self.ix = ix[ok]; self.m = len(isim)
        self.isim = isim
        nodes = [EARTH] + sorted(set(isim.ravel()))
        self.nodes = nodes; self.id = {x: k for k, x in enumerate(nodes)}; n = len(nodes)
        P = np.array([sv(x) for x in nodes]); self.C = (np.abs(P[:, None, :] - P[None, :, :]) * W).sum(-1)
        # üyelik: her cismin kaç eşleşmede olduğu ve tek ise hangisi
        say = np.zeros(n, int); tek = np.full(n, -1)
        for mi, r in enumerate(isim):
            for x in set(r):
                j = self.id[x]; say[j] += 1; tek[j] = mi if say[j] == 1 else -2
        A = np.ones((n, n), bool)
        ayni = (say[:, None] == 1) & (say[None, :] == 1) & (tek[:, None] == tek[None, :])
        A &= ~ayni; A[0, :] = False; A[:, 0] = False; np.fill_diagonal(A, False)
        for r in isim:
            q, u, j = (self.id[x] for x in r)
            A[0, q] = True; A[q, u] = True; A[u, j] = True
        self.A = A
        self.ilk_sira = {}
        for mi, r in enumerate(isim):
            for x in r:
                self.ilk_sira.setdefault(x, mi + 1)

    def _dij(self, A):
        G = np.where(A, self.C + 1e-12, 0.0)
        d, pr = dijkstra(csr_matrix(G), indices=0, return_predecessors=True)
        return d, pr

    @staticmethod
    def _yol(pr, t):
        y = [t]
        while pr[y[-1]] >= 0:
            y.append(pr[y[-1]])
        return y[::-1]

    def en_iyi(self, hedef):
        if hedef not in self.id:
            return np.inf, []
        d, pr = self._dij(self.A); t = self.id[hedef]
        if not np.isfinite(d[t]):
            return np.inf, []
        return float(d[t]), [self.nodes[k] for k in self._yol(pr, t)]

    def top5(self, hedef):
        out = []
        if hedef not in self.id:
            return out
        A = self.A.copy(); t = self.id[hedef]
        for _ in range(5):
            d, pr = self._dij(A)
            if not np.isfinite(d[t]):
                break
            y = self._yol(pr, t)
            out.append((float(d[t]), [self.nodes[k] for k in y]))
            if len(y) < 2:
                break
            h = y[1]; A[h, :] = False; A[:, h] = False
        return out


# ------------------------------------------------------------------ yazarın rota motoru (k7top5icin.py ile birebir)
# Eşit maliyetli rotalar arasında hangisinin seçileceği yazarın algoritmasına bağlıdır: elemanlar 4 ondalığa (Tj 3) yuvarlanır,
# grafik sözlüğü eşleşme sırasıyla kurulur (önce eşleşme içi Dünya→Q→U→J, sonra eşleşmeler arası serbest geçiş),
# heapq tabanlı Dijkstra ve katı '<' güncellemesi kullanılır. Böylece makaledeki rotalar (Fig. 6, Tablo 4) yeniden üretilir.
def _yv(x):
    e = EL[x]
    return np.array([round(e["a"], 4), round(e["e"], 4), round(e["i"], 4), round(e["Tj"], 3)])


def ymaliyet(x, y):
    return float(np.sum(W * np.abs(_yv(x) - _yv(y))))


def yazar_graf(eslesmeler):
    """eslesmeler: [[Q, U, J], ...] (yalnız elemanları bilinen cisimler)."""
    import heapq  # noqa: F401
    G = {EARTH: {}}
    for m in eslesmeler:
        for a in m:
            G.setdefault(a, {})
    for m in eslesmeler:
        p = [EARTH] + list(m)
        for i in range(len(p) - 1):
            G[p[i]][p[i + 1]] = ymaliyet(p[i], p[i + 1])
    for i in range(len(eslesmeler)):
        for j in range(i + 1, len(eslesmeler)):
            for a in eslesmeler[i]:
                for b in eslesmeler[j]:
                    c = ymaliyet(a, b)
                    if b not in G[a] or c < G[a][b]:
                        G[a][b] = c; G[b][a] = c
    return G


def yazar_dij(G, s=EARTH):
    import heapq
    D = {n: float("inf") for n in G}; D[s] = 0.0; P = {n: None for n in G}; pq = [(0.0, s)]
    while pq:
        dd, u = heapq.heappop(pq)
        if dd > D[u]:
            continue
        for v, w in G[u].items():
            nd = dd + w
            if nd < D[v]:
                D[v] = nd; P[v] = u; heapq.heappush(pq, (nd, v))
    return D, P


def _yazar_yol(P, t):
    y, n = [], t
    while n:
        y.append(n); n = P.get(n)
    return y[::-1]


def yazar_en_iyi(G, hedef):
    if hedef not in G:
        return np.inf, []
    D, P = yazar_dij(G)
    return (float(D[hedef]), _yazar_yol(P, hedef)) if np.isfinite(D[hedef]) else (np.inf, [])


def yazar_top5(G, hedef):
    """Yazarın budama yöntemi: her turda rotanın ilk durağı (Dünya'dan sonraki) silinir."""
    import copy
    G = copy.deepcopy(G); out = []
    for _ in range(5):
        if hedef not in G:
            break
        D, P = yazar_dij(G)
        if not np.isfinite(D[hedef]) or not P.get(hedef):
            break
        y = _yazar_yol(P, hedef); out.append((float(D[hedef]), y))
        if len(y) < 2:
            break
        h = y[1]
        if h in G:
            del G[h]
            for k in G:
                G[k].pop(h, None)
        else:
            break
    return out


def eslesme_listesi(ix):
    Qn, Un, Jn = h2.Qn, h2.Un, h2.Jn
    out = []
    for q, u, j in ix:
        m = [Qn[q], Un[u], Jn[j]]
        if all(x in EL for x in m):
            out.append(m)
    return out


def yazar_sirasi(ix):
    """Ref için eşleşmeleri yazarın kendi sıralı dosyasındaki sıraya koyar (eslesme_sonuclari 20590.txt).
    Excel'deki 6 ondalıklı mesafeler 10⁻⁶ ölçeğindeki sıralamayı biraz değiştirdiği için makaledeki eşleşme numaraları
    (ör. Jeffreyrobbins 438) ancak bu sırayla korunur."""
    yol = os.path.join(os.path.dirname(o.BULMACA), "Alien_Puzzle_Project", "data", "eslesme_sonuclari 20590.txt")
    if not os.path.exists(yol):
        return ix
    duz = {"5254 Ulysses (1986 V61)": "5254 Ulysses (1986 VG1)"}
    yaz = [[duz.get(x, x) for x in list(v.values())[0][1:]] for v in json.load(open(yol, encoding="utf-8")).values()]
    Qi = {x: k for k, x in enumerate(h2.Qn)}; Ui = {x: k for k, x in enumerate(h2.Un)}; Ji = {x: k for k, x in enumerate(h2.Jn)}
    try:
        yeni = np.array([[Qi[q], Ui[u], Ji[j]] for q, u, j in yaz])
    except KeyError:
        return ix
    if len(yeni) != len(ix) or set(map(tuple, yeni)) != set(map(tuple, ix)):
        return ix
    return yeni


# Ref, Route 6 (Jeffreyrobbins): 8 eşit maliyetli tek duraklı yol var (maliyetler son basamağa kadar aynı); makaledeki durak korunur.
YAZAR_DURAK = {("Ref", "169509 Jeffreyrobbins (2002 CV269)"): "755 Quintilla (A908 GC)"}


def etiket(ag, yol):
    return " → ".join("Dünya" if x == EARTH else f"{x.split(' (')[0]} ({ag.ilk_sira.get(x, '-')})" for x in yol)


# ------------------------------------------------------------------ kapı seçimi
def kapilar(nesneler):
    adaylar = [x for x in nesneler if kapi_adayi(x) and EL[x]["Tj"] < 3]
    truva = [x for x in adaylar if 5.05 <= EL[x]["a"] <= 5.35]
    ana = min(truva or adaylar, key=lambda x: EL[x]["Tj"]) if adaylar else None
    kalan = [x for x in nesneler if kapi_adayi(x) and x != ana and EL[x]["Tj"] <= 3]
    ara = min(kalan, key=lambda x: abs(EL[x]["Tj"] - 3)) if kalan else None
    return ana, ara


def sinif(x):
    if x in GEZ:
        return "Gezegen"
    if x in UYDU:
        return f"Uydu ({UYDU[x]})"
    if "/" in x:
        return "Kuyruklu yıldız"
    a, tj = EL[x]["a"], EL[x]["Tj"]
    if 5.05 <= a <= 5.35:
        return "Jüpiter Truvası (1:1)"
    if 3.7 <= a <= 4.2:
        return "Hilda (3:2) / dış kuşak"
    if a > 5.5:
        return "Kentaur / dış"
    return "Ana kuşak"


# ------------------------------------------------------------------ formül başına analiz
def analiz(kod):
    z = np.load(os.path.join(ANALIZ, "05_h2", "cache", f"{kod}.npz")); dv, ix = z["dv"], z["ix"]
    if kod == "Ref":
        ix = yazar_sirasi(ix)          # makaledeki eşleşme numaraları için yazarın sıralaması
    n = ELBOW[kod]
    r = {"Formül": kod, "Eşitlik": h2.YAZIM[kod], "Elbow grubu (eşleşme)": n, "Toplam eşleşme": len(dv)}
    ag1 = Ag(ix[:n])
    grup = [x for x in ag1.nodes]
    r["Elbow grubu cisim (Dünya dahil)"] = len(grup); r["Elemanı eksik atlanan eşleşme (grup)"] = ag1.atlanan
    S11 = pd.DataFrame([{"Cisim": "399 Earth" if x == EARTH else x, "Tj": EL[x]["Tj"], "a (AU)": EL[x]["a"], "e": EL[x]["e"],
                         "i (°)": EL[x]["i"], "Sınıf": "Gezegen" if x == EARTH else sinif(x), "Tj<3": EL[x]["Tj"] < 3} for x in grup]).sort_values("Tj")
    ana, ara = kapilar(grup)
    # Ek kontrol: aynı büyüklükte rastgele gruplarda (formülün tüm eşleşmelerinden) Tj<3 asteroit sayısı
    Qn, Un, Jn = h2.Qn, h2.Un, h2.Jn
    uygun = {x for x in set(Qn) | set(Un) | set(Jn) if x in EL and kapi_adayi(x) and EL[x]["Tj"] < 3}
    gozlenen = len([x for x in grup if x in uygun])
    rng = np.random.default_rng(0); say = []
    for _ in range(2000):
        sec = ix[rng.choice(len(ix), min(n, len(ix)), replace=False)]
        say.append(len(set(Qn[sec[:, 0]]) & uygun | set(Un[sec[:, 1]]) & uygun | set(Jn[sec[:, 2]]) & uygun))
    say = np.array(say)
    r["Ek: rastgele grupta ≥1 Tj<3 asteroit olasılığı"] = float((say >= 1).mean())
    r["Ek: rastgele grupta ≥ gözlenen sayı olasılığı"] = float((say >= gozlenen).mean())
    r["Ek: rastgele grup Tj<3 ortalaması"] = float(say.mean())
    r["Ana kapı"] = ana or "Yok (grupta Tj<3 yok)"; r["Ara kapı"] = ara or "Yok"
    r["Ana kapı Tj / sınıf"] = f"{EL[ana]['Tj']:.3f} / {sinif(ana)}" if ana else "—"
    r["Ara kapı Tj / sınıf"] = f"{EL[ara]['Tj']:.3f} / {sinif(ara)}" if ara else "—"
    # stres testi k=1..7
    stres, ag7 = [], None
    for k in range(1, 8):
        agk = Ag(ix[:k * n])
        if k == 7:
            ag7 = agk
        for ad, g in (("Ana", ana), ("Ara", ara)):
            if not g:
                continue
            t5 = agk.top5(g)
            stres.append({"k": k, "Kapı": f"{ad}: {g.split(' (')[0]}", **{f"Top {i+1}": (t5[i][0] if i < len(t5) else np.nan) for i in range(5)},
                          "Doğrudan Dünya→kapı": maliyet(EARTH, g)})
    stres = pd.DataFrame(stres)
    # k=7 en iyi rotalar
    rot7 = []
    G7 = yazar_graf(eslesme_listesi(ix[:7 * n]))
    top5_7 = {g: yazar_top5(G7, g) for g in (ana, ara) if g}
    for ad, g in (("Ana", ana), ("Ara", ara)):
        if g:
            c, y = yazar_en_iyi(G7, g)
            if y:
                horizons(y)
            rot7.append({"Kapı": ad, "Hedef": g, "Rota (k=7)": etiket(ag7, y) if y else "Bulunamadı", "Maliyet": c,
                         "Doğrudan Dünya→kapı maliyeti": maliyet(EARTH, g), "Eğim terimi payı (%)": 100 * 10 * EL[g]["i"] / maliyet(EARTH, g),
                         "Adım maliyetleri": " + ".join(f"{maliyet(y[i], y[i+1]):.2f}" for i in range(len(y) - 1)) if y else "",
                         "MT (AU)": mt(y) if y else np.nan, "Doğrudan Öklid Dünya→kapı (AU)": mt([EARTH, g]) if y else np.nan, "_yol": y})
    rot7 = pd.DataFrame(rot7)
    if len(stres):
        for ad in ("Ana", "Ara"):
            s = stres[stres["Kapı"].str.startswith(ad)]
            if len(s):
                fl = s["Doğrudan Dünya→kapı"].iloc[0]
                hit = s[np.isclose(s["Top 1"], fl, atol=1e-6)]
                r[f"{ad} kapı: k=1 Top1 / doğrudan"] = f"{s['Top 1'].iloc[0]:.4f} / {fl:.4f}"
                r[f"{ad} kapı: Top1 doğrudana eşit mi (k=1)"] = bool(np.isclose(s["Top 1"].iloc[0], fl, atol=1e-6))
    # S14: tüm eşleşmelerde Tj<3
    agT = Ag(ix)
    tum_tj3 = [x for x in agT.nodes if kapi_adayi(x) and EL[x]["Tj"] < 3]
    yeni = [x for x in tum_tj3 if x not in grup]
    S14 = pd.DataFrame([{"Cisim": x, "Tj": EL[x]["Tj"], "a (AU)": EL[x]["a"], "Sınıf": sinif(x), "İlk eşleşme sırası": agT.ilk_sira.get(x)} for x in yeni]).sort_values("Tj", ascending=False) if yeni else pd.DataFrame()
    r["Gruptaki Tj<3 sayısı"] = len([x for x in grup if kapi_adayi(x) and EL[x]["Tj"] < 3]); r["Yeni Tj<3 (tüm eşleşmeler)"] = len(yeni)
    # S15 / Fig 8: rotalar → Thereus (ve kendi hedef)
    kapi_list = [x for x in grup if kapi_adayi(x) and EL[x]["Tj"] < 3] + yeni
    d, pr = agT._dij(agT.A)
    hedefler = [("Thereus", THEREUS)]
    kh = KENDI_HEDEF.get(kod)
    if kh and kh != THEREUS:
        EL[kh] = sbdb_hedef(kh); hedefler.append(("Kendi H1 hedefi", kh))
    # Rota ağı (yazarın yöntemi): k=7 eşleşmeleri + k=7 dışındaki kapıların ilk eşleşmesi; yazarın Dijkstra'sı
    tum = eslesme_listesi(ix); ilk = {}
    for mi, m_ in enumerate(tum):
        for x in m_:
            ilk.setdefault(x, mi)
    n7 = len(eslesme_listesi(ix[:7 * n]))
    GT = yazar_graf(tum[:n7] + [tum[ilk[g]] for g in kapi_list if g in ilk and ilk[g] >= n7])
    DT_, PT_ = yazar_dij(GT)
    S15 = []
    for hadi, hed in hedefler:
        for g in kapi_list:
            if g not in DT_ or not np.isfinite(DT_[g]):
                continue
            yk = _yazar_yol(PT_, g)
            durak = YAZAR_DURAK.get((kod, g))
            if durak and durak in GT[EARTH] and g in GT[durak] and abs(GT[EARTH][durak] + GT[durak][g] - DT_[g]) < 1e-9:
                yk = [EARTH, durak, g]
            y = yk + [hed]
            S15.append({"Hedef türü": hadi, "Hedef": hed, "Kapı": g, "Kapı Tj": EL[g]["Tj"], "Kapı grupta mı": g in grup,
                        "Rota": etiket(agT, y[:-1]) + " → " + hed.split(" (")[0], "Dünya→kapı (ağ)": float(DT_[g]),
                        "Kapı→hedef": ymaliyet(g, hed), "FT (toplam maliyet)": float(DT_[g]) + ymaliyet(g, hed), "_yol": y})
    S15 = pd.DataFrame(S15)
    if len(S15):
        horizons(set(sum(S15["_yol"].tolist(), [])) | {EARTH, THEREUS} | set(h2.Qn))
        alt = []
        for _, rw in S15.iterrows():
            t = agT.id[rw["Kapı"]]
            hub = [q for q in np.nonzero(agT.A[0])[0] if agT.A[q, t] and abs(agT.C[0, q] + agT.C[q, t] - d[t]) < 1e-6]
            yl = [[EARTH, agT.nodes[q], rw["Kapı"], rw["Hedef"]] for q in hub]
            mts = [mt(y) for y in yl]; mts = [m_ for m_ in mts if np.isfinite(m_)]
            ft = rw["FT (toplam maliyet)"]
            alt.append({"Eşit maliyetli tek duraklı alternatif sayısı": len(hub),
                        "MT min–max (alternatifler)": f"{min(mts):.2f} – {max(mts):.2f}" if mts else "—",
                        "EFF min–max (alternatifler)": f"{ft/max(mts):.2f} – {ft/min(mts):.2f}" if mts else "—",
                        "_effmin": ft / max(mts) if mts else np.nan, "_effmax": ft / min(mts) if mts else np.nan})
        S15 = pd.concat([S15, pd.DataFrame(alt, index=S15.index)], axis=1)
        S15["MT (AU)"] = S15["_yol"].map(mt); S15["EFF = FT/MT"] = S15["FT (toplam maliyet)"] / S15["MT (AU)"]
        for hadi, hed in hedefler:
            s = S15["Hedef"] == hed
            S15.loc[s, "FT sırası"] = S15.loc[s, "FT (toplam maliyet)"].rank(method="min")
            S15.loc[s, "EFF sırası"] = S15.loc[s, "EFF = FT/MT"].rank(method="min")
            S15.loc[s, "MT sırası"] = S15.loc[s, "MT (AU)"].rank(method="min")
        th = S15[S15["Hedef"] == THEREUS]
        if len(th):
            bf = th.loc[th["FT (toplam maliyet)"].idxmin()]; be = th.loc[th["EFF = FT/MT"].idxmin()]
            r["Thereus: rota sayısı"] = len(th)
            r["Thereus: en ucuz rota (FT)"] = f"{bf['Kapı'].split(' (')[0]} — {bf['FT (toplam maliyet)']:.2f}"
            r["Thereus: en 'verimli' rota (EFF)"] = f"{be['Kapı'].split(' (')[0]} — EFF {be['EFF = FT/MT']:.2f} (FT {be['FT (toplam maliyet)']:.2f}, MT {be['MT (AU)']:.2f})"
            r["Thereus: EFF birincisi grupta mı"] = bool(be["Kapı grupta mı"])
            r["Thereus: EFF birincisi FT'de kaçıncı"] = int(be["FT sırası"])
            r["Thereus: EFF–MT sıra korelasyonu"] = th["EFF = FT/MT"].corr(th["MT (AU)"], method="spearman") if len(th) > 2 else np.nan
            r["Thereus: EFF birincisi eşit maliyetli durak seçimine göre değişebilir mi"] = bool(
                any(th["_effmin"].drop(be.name) < be["_effmax"])) if len(th) > 1 else False
    r["Doğrudan Dünya→Thereus"] = maliyet(EARTH, THEREUS)
    return r, dict(S11=S11, stres=stres, rot7=rot7, S14=S14, S15=S15, ag7=ag7, grup=grup, ana=ana, ara=ara, top5_7=top5_7)


# ------------------------------------------------------------------ grafikler
def g_stres(axs, kod, R):
    st = R["stres"]
    for ax, ad in zip(axs, ("Ana", "Ara")):
        s = st[st["Kapı"].str.startswith(ad)] if len(st) else st
        if not len(s):
            ax.text(0.5, 0.5, "Kapı yok", ha="center", transform=ax.transAxes, color="grey"); ax.set_title(f"{kod} — {ad} kapı"); continue
        for i in range(5):
            ax.plot(s["k"], s[f"Top {i+1}"], "o-", ms=3, label=f"Top {i+1}")
        ax.axhline(s["Doğrudan Dünya→kapı"].iloc[0], color="k", ls=":", lw=1, label="Doğrudan maliyet")
        ax.set_title(f"{kod} — {s['Kapı'].iloc[0]}", fontsize=8); ax.set_xlabel("k (grup)"); ax.legend(fontsize=5)


def g_ag(ax, kod, R):
    rot = R["rot7"]
    if not len(rot):
        ax.text(0.5, 0.5, "Kapı yok", ha="center", transform=ax.transAxes, color="grey"); ax.set_title(kod); ax.axis("off"); return
    ag = R["ag7"]; yollar = [y for y in rot["_yol"] if y]
    ns = []
    for y in yollar:
        for x in y:
            if x not in ns:
                ns.append(x)
    ang = np.linspace(0, 2 * np.pi, len(ns), endpoint=False)
    pos = {x: (np.cos(a_), np.sin(a_)) for x, a_ in zip(ns, ang)}
    for i, a_ in enumerate(ns):
        for b in ns[i + 1:]:
            ia, ib = ag.id[a_], ag.id[b]
            if ag.A[ia, ib] or ag.A[ib, ia]:
                ax.plot(*zip(pos[a_], pos[b]), color="grey", ls="--", lw=0.5)
                ax.text(*(np.add(pos[a_], pos[b]) / 2), f"{ag.C[ia, ib]:.1f}", fontsize=5, color="grey")
    for y, c in zip(yollar, ("orange", "limegreen")):
        for i in range(len(y) - 1):
            ax.plot(*zip(pos[y[i]], pos[y[i + 1]]), color=c, lw=3)
    for x, (px, py) in pos.items():
        renk = "gold" if x in (R["ana"], R["ara"]) else ("lightblue" if x != EARTH else "steelblue")
        ax.scatter(px, py, s=300, c=renk, edgecolors="k", zorder=3)
        ax.text(px, py - 0.17, "Dünya" if x == EARTH else f"{x.split(' (')[0]} ({ag.ilk_sira.get(x)})", ha="center", fontsize=6)
    ax.set_title(f"{kod} (turuncu: ana, yeşil: ara rota)"); ax.axis("off"); ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4)


def _yorunge(el):
    if not el or el.get("EC", 1) >= 1:
        return None
    a, e, i, om, w = el["A"], el["EC"], *np.radians([el["IN"], el["OM"], el["W"]])
    nu = np.linspace(0, 2 * np.pi, 200); r = a * (1 - e * e) / (1 + e * np.cos(nu))
    x, y = r * np.cos(nu), r * np.sin(nu)
    R3 = lambda t, ax_: np.array([[np.cos(t), -np.sin(t), 0], [np.sin(t), np.cos(t), 0], [0, 0, 1]]) if ax_ == "z" else np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    M = R3(om, "z") @ R3(i, "x") @ R3(w, "z")
    return M @ np.vstack([x, y, np.zeros_like(x)])


def g_3d(ax, kod, R):
    rot = R["rot7"]; ax.scatter([0], [0], [0], c="yellow", s=80, edgecolors="k")
    for y, c in zip([y for y in rot["_yol"] if y] if len(rot) else [], ("orange", "limegreen")):
        P = np.array([xyz(x) for x in y]); ax.plot(P[:, 0], P[:, 1], P[:, 2], color=c, lw=2)
        for x in y:
            p = xyz(x); ax.scatter(*p, s=25, c="b" if x == EARTH else "k")
            ax.text(*p, "Dünya" if x == EARTH else x.split(" ")[1] if " " in x else x, fontsize=6)
            o_ = _yorunge(HOR.get(x, {}).get("el"))
            if o_ is not None and x != EARTH:
                ax.plot(*o_, lw=0.5, ls="--", alpha=0.6)
    ax.set_title(kod); ax.set_xlabel("X (AU)"); ax.set_ylabel("Y (AU)"); ax.set_zlabel("Z (AU)")


def g_uclu(ax, kod, R, hedef=THEREUS):
    s = R["S15"]
    s = s[s["Hedef"] == hedef] if len(s) else s
    if not len(s):
        ax.text(0.5, 0.5, "Rota yok", ha="center", transform=ax.transAxes, color="grey"); ax.set_title(kod); return
    s = s.sort_values("EFF = FT/MT").head(12); x = np.arange(len(s)); b = 0.27
    ax.bar(x - b, s["MT (AU)"], b, color="salmon", label="MT (AU)")
    ax2 = ax.twinx(); ax2.bar(x, s["FT (toplam maliyet)"], b, color="slateblue", alpha=0.7, label="FT")
    ax3 = ax.twinx(); ax3.spines["right"].set_position(("axes", 1.12)); ax3.bar(x + b, s["EFF = FT/MT"], b, color="mediumseagreen", label="EFF")
    ax.set_xticks(x, [k.split(" (")[0].split(" ")[-1] + ("*" if g else "") for k, g in zip(s["Kapı"], s["Kapı grupta mı"])], rotation=60, fontsize=6)
    ax.set_title(f"{kod}: Thereus rotaları (EFF'e göre sıralı; * = elbow grubu)", fontsize=8)
    for a_, c in ((ax, "salmon"), (ax2, "slateblue"), (ax3, "mediumseagreen")):
        a_.tick_params(axis="y", colors=c, labelsize=6)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="salmon", label="MT: fiziksel mesafe (AU)"), Patch(color="slateblue", label="FT: toplam maliyet"),
                       Patch(color="mediumseagreen", label="EFF = FT/MT (düşük = 'verimli')")], fontsize=6, loc="upper left")  # Line2D


# ------------------------------------------------------------------ ana akış
if __name__ == "__main__":
    eksikleri_tamamla(); print("Tamamlanan elemanlar:", EKSIK_NOT, flush=True)
    ozet, SON = [], {}
    for kod in FORMULLER:
        t0 = time.time()
        r, R = analiz(kod); ozet.append(r); SON[kod] = R
        kl = os.path.join(CIKTI, "formuller", kod); os.makedirs(kl, exist_ok=True)
        klTR = os.path.join(CACHE, "tr_grafik", kod); os.makedirs(klTR, exist_ok=True)   # Türkçe çalışma grafikleri (teslim edilmez; İngilizceleri makale_grafikleri*.py)
        fig, axs = plt.subplots(1, 2, figsize=(14, 5)); g_stres(axs, kod, R); fig.suptitle(f"{kod}: Fig. 5 / S16 — Stres testi (Top 5 rota maliyeti, k=1–7)")
        fig.tight_layout(); fig.savefig(os.path.join(klTR, "fig5_stres_testi.png"), dpi=120); plt.close(fig)
        fig, ax = plt.subplots(figsize=(10, 9)); g_ag(ax, kod, R); fig.suptitle(f"{kod}: Fig. 6 / S17 — Ağ topolojisi (k=7)")
        fig.tight_layout(); fig.savefig(os.path.join(klTR, "fig6_ag_topolojisi.png"), dpi=120); plt.close(fig)
        fig = plt.figure(figsize=(10, 8)); ax = fig.add_subplot(projection="3d"); g_3d(ax, kod, R); fig.suptitle(f"{kod}: Fig. 7 / S18 — 15.08.1977 3D konumlar")
        fig.savefig(os.path.join(klTR, "fig7_3d.png"), dpi=110); plt.close(fig)
        fig, ax = plt.subplots(figsize=(12, 6)); g_uclu(ax, kod, R); fig.tight_layout(); fig.savefig(os.path.join(klTR, "fig8_uclu_karsilastirma.png"), dpi=120); plt.close(fig)
        # S19: rota cisimleri arası Öklid mesafeleri
        ns = []
        for y in (R["rot7"]["_yol"].tolist() if len(R["rot7"]) else []):
            for x in y + [THEREUS]:
                if x not in ns:
                    ns.append(x)
        S19 = pd.DataFrame([[np.linalg.norm(xyz(a_) - xyz(b)) for b in ns] for a_ in ns],
                           index=["Dünya" if x == EARTH else x.split(" (")[0] for x in ns], columns=["Dünya" if x == EARTH else x.split(" (")[0] for x in ns])
        R["S19"] = S19
        with pd.ExcelWriter(os.path.join(kl, f"{kod}_H3.xlsx")) as w:
            pd.DataFrame([r]).T.reset_index().rename(columns={"index": "Ölçüt", 0: "Değer"}).to_excel(w, "Özet", index=False)
            R["S11"].to_excel(w, "S11 Tj tablosu", index=False)
            R["stres"].to_excel(w, "S13 stres testi", index=False)
            R["rot7"].drop(columns="_yol", errors="ignore").to_excel(w, "k7 ana-ara rotalar", index=False)
            R["S14"].to_excel(w, "S14 yeni Tj<3", index=False)
            R["S15"].drop(columns=["_yol", "_effmin", "_effmax"], errors="ignore").to_excel(w, "S15 rotalar FT-MT-EFF", index=False)
            S19.to_excel(w, "S19 Öklid mesafeleri")
        print(f"{kod}: grup={r['Elbow grubu (eşleşme)']} ana={r['Ana kapı'][:20]} ara={r['Ara kapı'][:20]} rota={r.get('Thereus: rota sayısı', 0)}  ({time.time()-t0:.0f} s)", flush=True)
    ozet = pd.DataFrame(ozet)
    for k_, R in SON.items():
        for c in ("ag7",):
            R.pop(c, None)
    pd.to_pickle((ozet, SON, EKSIK_NOT), os.path.join(CACHE, "h3_sonuc.pkl"))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(ozet.drop(columns=["Eşitlik"]).T.to_string())
