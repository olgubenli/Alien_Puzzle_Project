# -*- coding: utf-8 -*-
"""Faz 3 analizi: plan bölüm 4.1'deki önceden kayıtlı ölçütler."""
import json, os
import numpy as np, pandas as pd
from scipy import stats
import faz2_ortak as o

C = os.path.join(o.KOK, "faz3_sonuclar")
df = pd.read_csv(C + "/faz3_ham.csv")
kont = [f"h1_{t}" for t in o.kontrol_tarihleri()]
df["h1_lambda"] = df[kont].mean(1)
df["h1_n"] = df[f"h1_{o.WOW}"]
df["h1_P"] = np.where(df.h1_n >= 1, stats.poisson.cdf(df.h1_n, df.h1_lambda.clip(lower=1e-12)), np.nan)
Y = df[df.id == "YAZAR"].iloc[0]; R = df[df.id != "YAZAR"]
s = {"formul_sayisi": len(R)}

# ---------------- F3-H1
h1 = R[R.h1_n >= 1]
s["H1"] = {
    "1977'de >=1 eşleşme veren formül": len(h1),
    "1977'de tam 1 eşleşme veren formül": int((R.h1_n == 1).sum()),
    "1977'de Thereus'u bulan formül": int(R.h1_thereus.sum()),
    "1977'de TEK eşleşmesi Thereus olan formül": int(((R.h1_n == 1) & R.h1_thereus).sum()),
    "yazar_n_1977": int(Y.h1_n), "yazar_lambda_kontrol": float(Y.h1_lambda), "yazar_P": float(Y.h1_P),
    "P <= yazar olan rastgele formül oranı": float((h1.h1_P <= Y.h1_P).mean()),
}
th = R[R.h1_thereus]
s["H1"]["Thereus bulanların en iyi sapması: yazardan iyi olan"] = int((th.h1_en_iyi_sapma < Y.h1_en_iyi_sapma).sum())

# ---------------- F3-H2
g = R[R.h2_guvenilir == True]
pa = float((g.h2_sekizinci_norm <= Y.h2_sekizinci_norm).mean())
pb = float((g.h2_max_bosluk >= Y.h2_max_bosluk).mean())
gs = g.dropna(subset=["h2s_sekizinci_norm"])
s["H2"] = {
    "güvenilir formül": len(g),
    "yazar 8. sapma (norm.)": float(Y.h2_sekizinci_norm), "rastgele medyan": float(g.h2_sekizinci_norm.median()),
    "(a) 8. sapması yazardan iyi/eşit oranı": pa,
    "yazar en büyük boşluk": float(Y.h2_max_bosluk), "rastgele medyan boşluk": float(g.h2_max_bosluk.median()),
    "(b) boşluğu yazardan büyük/eşit oranı": pb,
    "yazar lehine seçilen yüzdelik": min(pa, pb),
    "sinyal anı: (a) oranı": float((gs.h2s_sekizinci_norm <= Y.h2s_sekizinci_norm).mean()),
    "sinyal anı: (b) oranı": float((gs.h2s_max_bosluk >= Y.h2s_max_bosluk).mean()),
}

# ---------------- F3-H3
g3 = R[R.h2_n_esik >= 8]
s["H3"] = {"Top 8'i olan formül": len(g3),
           "Truva + Hilda hikâyesi olan": int(g3.h3_hikaye.sum()),
           "hikâye oranı": float(g3.h3_hikaye.mean()),
           "en az bir Truva": float((g3.h3_truva > 0).mean()), "en az bir Hilda": float((g3.h3_hilda > 0).mean()),
           "yazarda hikâye": bool(Y.h3_hikaye)}

# ---------------- zaman
s["Zaman"] = {"yazar: sinyal anında korunan Top 8 üyesi": int(Y.zaman_top8_korunan),
              "rastgele (güvenilir) korunan dağılımı": g.zaman_top8_korunan.value_counts().sort_index().to_dict(),
              "rastgelelerin yazardan kararlı/eşit oranı": float((g.zaman_top8_korunan >= Y.zaman_top8_korunan).mean())}

# ---------------- karar
k1 = s["H1"]["P <= yazar olan rastgele formül oranı"]; k2 = s["H2"]["yazar lehine seçilen yüzdelik"]; k3 = s["H3"]["hikâye oranı"]
def sinif(p): return "UÇ (%1)" if p <= 0.01 else ("zayıf (%1–5)" if p <= 0.05 else "şansla tutarlı (>%5)")
s["KARAR"] = {"F3-H1": [k1, sinif(k1)], "F3-H2": [k2, sinif(k2)], "F3-H3": [k3, sinif(k3)],
              "hipotez tuttu mu": bool(k1 <= 0.01 and k2 <= 0.01 and k3 <= 0.01)}
json.dump(s, open(C + "/faz3_ozet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print(json.dumps(s, ensure_ascii=False, indent=1, default=float))

# örnekler
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print("\nTek eşleşmesi Thereus olan rastgele formüller:")
print(R[(R.h1_n == 1) & R.h1_thereus][["id", "formul", "h1_en_iyi_sapma", "h1_lambda", "h1_P"]].to_string())
print("\nH1 P'si en küçük 10 formül:"); print(h1.nsmallest(10, "h1_P")[["id", "formul", "h1_n", "h1_lambda", "h1_P", "h1_1977_isimler"]].to_string())
print("\nH2'de en sıkı 8 formül:"); print(g.nsmallest(8, "h2_sekizinci_norm")[["id", "formul", "h2_n_esik", "h2_sekizinci_norm", "h2_max_bosluk"]].to_string())
print("\nH2'de en büyük boşluklu 8 formül:"); print(g.nlargest(8, "h2_max_bosluk")[["id", "formul", "h2_n_esik", "h2_sekizinci_norm", "h2_max_bosluk", "h2_max_bosluk_sira"]].to_string())
