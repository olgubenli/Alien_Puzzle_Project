# -*- coding: utf-8 -*-
"""Tarama motoru: E sabit, Q x U x J tüm kombinasyonları; sapma dağılımı + en küçük sapmalar."""
import numpy as np
import faz2_ortak as o

TOPK = 60

# ---------------------------------------------------------------- formüller
# Eşitlik formülleri: f(E,Q,U,J) -> (sol, sag); sapma = |sol-sag| / |sag| * 100
ESITLIKLER = {
    "Y0  6|E-Q| = 5|U-J|   (yazar)": lambda E, Q, U, J: (6 * abs(E - Q) + 0 * U, 5 * abs(U - J)),
    "A1  5|E-Q| = 6|U-J|": lambda E, Q, U, J: (5 * abs(E - Q) + 0 * U, 6 * abs(U - J)),
    "A2  |E-Q| = |U-J|": lambda E, Q, U, J: (abs(E - Q) + 0 * U, abs(U - J)),
    "A3  6|E-U| = 5|Q-J|": lambda E, Q, U, J: (6 * abs(E - U) + 0 * J, 5 * abs(Q - J) + 0 * U),
    "A4  6|E-J| = 5|Q-U|": lambda E, Q, U, J: (6 * abs(E - J) + 0 * U, 5 * abs(Q - U) + 0 * J),
    "A5  6(E+Q) = 5(U+J)": lambda E, Q, U, J: (6 * (E + Q) + 0 * U, 5 * (U + J)),
    "A6  6EQ = 5UJ (çarpım)": lambda E, Q, U, J: (6 * E * Q + 0 * U, 5 * U * J),
    "A7  6E/Q = 5U/J": lambda E, Q, U, J: (6 * E / Q + 0 * U, 5 * U / J),
    "A8  6+|E-Q| = 5+|U-J|": lambda E, Q, U, J: (6 + abs(E - Q) + 0 * U, 5 + abs(U - J)),
    "A9  6E = 5(Q+U+J)/3": lambda E, Q, U, J: (6 * E + 0 * U + 0 * J, 5 * (Q + U + J) / 3),
    "A10 6|E-Q|U = 5J": lambda E, Q, U, J: (6 * abs(E - Q) * U + 0 * J, 5 * J + 0 * U),
}

# Eski (Faz 1) tek-değer formülleri: değer -> en yakın gezegen; sapma = |F-P|/P * 100
ESKI10 = {
    "F1  (6+E+Q)-(U+J+5)": lambda E, Q, U, J: (6 + E + Q) - (U + J + 5),
    "F2  (toplam/6)-5": lambda E, Q, U, J: (6 + E + Q + U + J + 5) / 6 - 5,
    "F3  (6+5)(Q-E)/(U+J)": lambda E, Q, U, J: 11 * (Q - E) / (U + J),
    "F4  sqrt(30)+(Q-E)/(U-J)": lambda E, Q, U, J: np.sqrt(30) + (Q - E) / (U - J),
    "F5  (Q*E)/(U+J)": lambda E, Q, U, J: Q * E / (U + J),
    "F6  (U-6)-(Q-J)+(E-5)": lambda E, Q, U, J: (U - 6) - (Q - J) + (E - 5),
    "F7  (6J)/(U-Q)+E/5": lambda E, Q, U, J: 6 * J / (U - Q) + E / 5,
    "F8  (U+6)/(Q-5)*E/J": lambda E, Q, U, J: (U + 6) / (Q - 5) * E / J,
    "F9  ((Q+U)/(J+6))-5": lambda E, Q, U, J: (Q + U) / (J + 6) - 5,
    "F10 5E-(Q-U)/(J-6)": lambda E, Q, U, J: E * 5 - (Q - U) / (J - 6),
}


def _sapma_esitlik(f, E, q, U, J):
    with np.errstate(divide="ignore", invalid="ignore"):
        sol, sag = f(E, q, U[:, None], J[None, :])
        d = np.abs(sol - sag) / np.abs(sag) * 100
    return d, None


def _sapma_tek(f, E, q, U, J, hedef):
    with np.errstate(divide="ignore", invalid="ignore"):
        F = np.broadcast_to(f(E, q, U[:, None], J[None, :]), (len(U), len(J)))
        dd = np.abs(F[..., None] - hedef) / hedef * 100        # (U,J,8)
        k = np.nanargmin(np.where(np.isfinite(dd), dd, np.inf), axis=-1)
        d = np.take_along_axis(dd, k[..., None], -1)[..., 0]
    return d, k


def tara(f, E, Q, U, J, hedef=None):
    """Tüm Q×U×J kombinasyonlarını tarar.
    Dönüş: n_toplam, n_esik, n_yerel, en küçük TOPK sapma ve indeksleri (qi, ui, ji, hedef_i)."""
    n_esik = n_yerel = 0
    best_d = np.empty(0); best_i = np.empty((0, 4), int)
    nU, nJ = len(U), len(J)
    for qi, q in enumerate(Q):
        if hedef is None:
            d, k = _sapma_esitlik(f, E, q, U, J)
        else:
            d, k = _sapma_tek(f, E, q, U, J, hedef)
        d = np.where(np.isfinite(d), d, np.inf).ravel()
        n_esik += int((d <= o.ESIK).sum())
        n_yerel += int((d <= o.YEREL).sum())
        m = min(TOPK, d.size)
        idx = np.argpartition(d, m - 1)[:m]
        ui, ji = np.divmod(idx, nJ)
        hi = k.ravel()[idx] if k is not None else -np.ones(m, int)
        best_d = np.concatenate([best_d, d[idx]])
        best_i = np.concatenate([best_i, np.c_[np.full(m, qi), ui, ji, hi]])
        s = np.argsort(best_d)[:TOPK]
        best_d, best_i = best_d[s], best_i[s]
    return {"n_toplam": len(Q) * nU * nJ, "n_esik": n_esik, "n_yerel": n_yerel,
            "kucuk": best_d, "idx": best_i}
