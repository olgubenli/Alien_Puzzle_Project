# -*- coding: utf-8 -*-
"""Faz 3: 6,E,Q,U,J,5 karakterlerini birer kez kullanan rastgele eşitlikler üretir."""
import json, os
import numpy as np

YAPRAK = ["6", "E", "Q", "U", "J", "5"]
DEGISKEN = set("EQUJ")
OPS = ["+", "-", "*", "/", "|-|"]
YAZAR = ("(6*abs(E-Q))", "(5*abs(U-J))")
KOK = os.path.dirname(os.path.abspath(__file__))
DOSYA = os.path.join(KOK, "faz3_sonuclar", "formuller.json")


def agac(yap, rng):
    if len(yap) == 1:
        return yap[0]
    k = rng.integers(1, len(yap))
    a, b = agac(yap[:k], rng), agac(yap[k:], rng)
    op = OPS[rng.integers(len(OPS))]
    return f"abs({a}-{b})" if op == "|-|" else f"({a}{op}{b})"


def derle(ifade):
    return eval("lambda E,Q,U,J: " + ifade, {"abs": np.abs})


def imza(sol, sag, X):
    with np.errstate(all="ignore"):
        L = np.broadcast_to(derle(sol)(*X), X[0].shape); R = np.broadcast_to(derle(sag)(*X), X[0].shape)
        d = np.abs(L - R) / np.abs(R)
    if not np.all(np.isfinite(d)) or np.allclose(d, d[0]):      # sabit / tanımsız formülleri at
        return None
    return tuple(np.round(d, 7))


def uret(n=1000, tohum=2026):
    rng = np.random.default_rng(tohum)
    X = [np.random.default_rng(7).uniform(0.5, 30, 64) for _ in range(4)]
    goruldu = {imza(*YAZAR, X): "YAZAR"}
    out = [{"id": "YAZAR", "sol": YAZAR[0], "sag": YAZAR[1]}]
    deneme = 0
    while len(out) < n + 1:
        deneme += 1
        p = list(rng.permutation(YAPRAK)); k = int(rng.integers(1, 6))
        if not (DEGISKEN & set(p[:k]) and DEGISKEN & set(p[k:])):
            continue
        sol, sag = agac(p[:k], rng), agac(p[k:], rng)
        s = imza(sol, sag, X)
        if s is None or s in goruldu:
            continue
        goruldu[s] = len(out)
        out.append({"id": f"R{len(out):04d}", "sol": sol, "sag": sag})
    os.makedirs(os.path.dirname(DOSYA), exist_ok=True)
    json.dump(out, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return out, deneme


if __name__ == "__main__":
    f, d = uret()
    print(len(f), "formül,", d, "deneme")
    for x in f[:8]:
        print(x["id"], x["sol"], "=", x["sag"])
