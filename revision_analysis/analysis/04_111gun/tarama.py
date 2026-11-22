# -*- coding: utf-8 -*-
"""22 eşitlik × 111 tarih taraması. Her tarihte E, U, J o günün gerçek mesafesi; Q bilinmeyen.
Denklem Q için çözülür; Ref-makale yalnızca pozitif kökü, diğerleri tüm köklerin mutlak değerini kullanır.
Her kökün ±%1 içindeki cisimler o formülün o günkü eşleşmesidir (kökler birleştirilir)."""
import os, sys, time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ortak as o  # noqa: E402
import veri111  # noqa: E402

np.seterr(all="ignore")
KOK = os.path.dirname(os.path.abspath(__file__))
a = np.abs
r30 = np.sqrt(30)

# kod, etiket, yazım, kök kuralı ('pozitif' | 'mutlak'), f(E,U,J) -> (sol(Q), sag(Q))
ESITLIKLER = [
    ("Ref-makale", "6|E−Q| = 5|U−J| (yalnız pozitif kök, makaledeki gibi)", "pozitif",
     lambda E, U, J: (lambda Q: 6 * a(E - Q), lambda Q: 5 * a(U - J) + 0 * Q)),
    ("Ref-mutlak", "6|E−Q| = 5|U−J| (negatif kökün mutlak değeri de)", "mutlak",
     lambda E, U, J: (lambda Q: 6 * a(E - Q), lambda Q: 5 * a(U - J) + 0 * Q)),
    ("F1", "6+E+Q = U+J+5", "mutlak", lambda E, U, J: (lambda Q: 6 + E + Q, lambda Q: U + J + 5 + 0 * Q)),
    ("F1-mutlak", "|6+E+Q| = |U+J+5|", "mutlak", lambda E, U, J: (lambda Q: a(6 + E + Q), lambda Q: a(U + J + 5) + 0 * Q)),
    ("F2", "(6+E+Q+U+J+5)/6 = 5", "mutlak", lambda E, U, J: (lambda Q: (6 + E + Q + U + J + 5) / 6, lambda Q: 5 + 0 * Q)),
    ("F2-mutlak", "|(6+E+Q+U+J+5)/6| = 5", "mutlak", lambda E, U, J: (lambda Q: a((6 + E + Q + U + J + 5) / 6), lambda Q: 5 + 0 * Q)),
    ("F3", "(6+5)(Q−E) = U+J", "mutlak", lambda E, U, J: (lambda Q: 11 * (Q - E), lambda Q: U + J + 0 * Q)),
    ("F3-mutlak", "(6+5)|Q−E| = U+J", "mutlak", lambda E, U, J: (lambda Q: 11 * a(Q - E), lambda Q: U + J + 0 * Q)),
    ("F4", "√(6×5) = (Q−E)/(U−J)", "mutlak", lambda E, U, J: (lambda Q: r30 + 0 * Q, lambda Q: (Q - E) / (U - J))),
    ("F4-mutlak", "√(6×5) = |Q−E|/|U−J|", "mutlak", lambda E, U, J: (lambda Q: r30 + 0 * Q, lambda Q: a(Q - E) / a(U - J))),
    ("F5", "Q×E = U+J", "mutlak", lambda E, U, J: (lambda Q: Q * E, lambda Q: U + J + 0 * Q)),
    ("F5-mutlak", "|Q×E| = U+J", "mutlak", lambda E, U, J: (lambda Q: a(Q * E), lambda Q: U + J + 0 * Q)),
    ("F6", "(U−6)+(E−5) = Q−J", "mutlak", lambda E, U, J: (lambda Q: (U - 6) + (E - 5) + 0 * Q, lambda Q: Q - J)),
    ("F6-mutlak", "|U−6|+|E−5| = |Q−J|", "mutlak", lambda E, U, J: (lambda Q: a(U - 6) + a(E - 5) + 0 * Q, lambda Q: a(Q - J))),
    ("F7", "(6×J)/(U−Q) = E/5", "mutlak", lambda E, U, J: (lambda Q: 6 * J / (U - Q), lambda Q: E / 5 + 0 * Q)),
    ("F7-mutlak", "(6×J)/|U−Q| = E/5", "mutlak", lambda E, U, J: (lambda Q: 6 * J / a(U - Q), lambda Q: E / 5 + 0 * Q)),
    ("F8", "(U+6)/(Q−5) = E/J", "mutlak", lambda E, U, J: (lambda Q: (U + 6) / (Q - 5), lambda Q: E / J + 0 * Q)),
    ("F8-mutlak", "(U+6)/|Q−5| = E/J", "mutlak", lambda E, U, J: (lambda Q: (U + 6) / a(Q - 5), lambda Q: E / J + 0 * Q)),
    ("F9", "(Q+U)/(J+6) = 5", "mutlak", lambda E, U, J: (lambda Q: (Q + U) / (J + 6), lambda Q: 5 + 0 * Q)),
    ("F9-mutlak", "|Q+U|/(J+6) = 5", "mutlak", lambda E, U, J: (lambda Q: a(Q + U) / (J + 6), lambda Q: 5 + 0 * Q)),
    ("F10", "E×5 = (Q−U)/(J−6)", "mutlak", lambda E, U, J: (lambda Q: E * 5 + 0 * Q, lambda Q: (Q - U) / (J - 6))),
    ("F10-mutlak", "E×5 = |Q−U|/|J−6|", "mutlak", lambda E, U, J: (lambda Q: E * 5 + 0 * Q, lambda Q: a(Q - U) / a(J - 6))),
]
KODLAR = [e[0] for e in ESITLIKLER]
YAZIM = {e[0]: e[1] for e in ESITLIKLER}

_POS = np.geomspace(1e-6, 1000.0, 200001)
_X = np.concatenate([-_POS[::-1], [0.0], _POS])


def kokler(g):
    y = g(_X)
    out = list(_X[y == 0])
    s = np.sign(y)
    for i in np.nonzero(s[:-1] * s[1:] < 0)[0]:
        lo, hi = _X[i], _X[i + 1]
        glo = g(np.array([lo]))[0]
        for _ in range(100):
            m = 0.5 * (lo + hi); gm = g(np.array([m]))[0]
            if np.sign(gm) == np.sign(glo):
                lo, glo = m, gm
            else:
                hi = m
        r = 0.5 * (lo + hi); gr = g(np.array([r]))[0]
        if np.isfinite(gr) and abs(gr) <= 1e-8 * (1 + abs(y[i]) + abs(y[i + 1])):
            out.append(r)
    return sorted(set(round(v, 9) for v in out))


def tara(veri):
    satir, hedef = [], []
    for t, x in veri.items():
        df, P = x["df"], x["P"]
        E, U, J = P["Earth"], P["Uranus"], P["Jupiter"]
        d = df.d.values; isim = df.isim.values
        for kod, _, kural, f in ESITLIKLER:
            sol, sag = f(E, U, J)
            kk = kokler(lambda q: sol(q) - sag(q))
            hs = sorted({round(abs(r), 9) for r in kk if (r > 0 if kural == "pozitif" else r != 0)})
            hedef.append({"formul": kod, "day": t, "window": x["pencere"],
                          "kokler": "; ".join(f"{r:.6f}" for r in kk), "hedefler": "; ".join(f"{h:.6f}" for h in hs),
                          "hedef_ana": min(hs, key=lambda h: abs(h - 12.26)) if hs else np.nan})
            best = {}
            for h in hs:
                sap = np.abs(d - h) / h * 100
                for i in np.nonzero(sap <= o.TOLERANS)[0]:
                    if i not in best or sap[i] < best[i][1]:
                        best[i] = (h, sap[i])
            for i, (h, s) in best.items():
                satir.append({"formul": kod, "day": t, "window": x["pencere"], "object_id": isim[i],
                              "au": d[i], "hedef": h, "sapma": s})
    m = pd.DataFrame(satir); m["day"] = pd.to_datetime(m["day"])
    h = pd.DataFrame(hedef); h["day"] = pd.to_datetime(h["day"])
    return m, h


if __name__ == "__main__":
    t0 = time.time()
    veri = veri111.hepsini_yukle()
    m, h = tara(veri)
    m.to_pickle(os.path.join(KOK, "cache", "eslesmeler.pkl")); h.to_pickle(os.path.join(KOK, "cache", "hedefler.pkl"))
    print("süre %.0f s" % (time.time() - t0))
    print(m.groupby(["formul", "window"]).size().unstack(fill_value=0).reindex(KODLAR).to_string())
