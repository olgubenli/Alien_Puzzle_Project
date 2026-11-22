# -*- coding: utf-8 -*-
"""İngilizce karşılaştırma panelleri: her şekil türü için formül başına üretilmiş (makale biçimindeki) PNG'leri tek bir ızgarada toplar.
Çıktı: <bölüm>/cikti/karsilastirma_EN/Panel_<şekil>.png (Türkçe eski paneller raporlara bağlı olduğu için yerinde bırakılır)."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

KOK = os.path.dirname(os.path.abspath(__file__))
BOLUM = {
    "04_111gun": ("Hypothesis 1 (Section 3.1)", ["Ref-makale", "Ref-mutlak", "F1", "F1-mutlak", "F2", "F2-mutlak", "F3", "F3-mutlak", "F4", "F4-mutlak",
                                                 "F5", "F5-mutlak", "F6", "F6-mutlak", "F7", "F7-mutlak", "F8", "F8-mutlak", "F9", "F9-mutlak", "F10", "F10-mutlak"],
                  ["FigS1_Fig1_AU_Distribution_by_Window", "FigS2_AU_Scatter_by_Window", "FigS3_Presence_Matrix_10d_1d_Inset", "FigS4_Presence_Matrix_Master_111d",
                   "FigS5_Repetition_Frequency_Pies", "FigS6_Fig2_AU_Density_by_Epoch_1990", "FigS7_Fig3_DBSCAN_Clusters", "FigS8_AU_vs_Time_Rolling_Mean_Outliers",
                   "FigS9_Polynomial_Regression_Deg3", "FigS10_Regression_Residuals"]),
    "05_h2": ("Hypothesis 2 (Section 3.2)", ["Ref", "F1", "F1-mutlak", "F2", "F2-mutlak", "F3", "F3-mutlak", "F4", "F4-mutlak", "F5", "F5-mutlak",
                                             "F6", "F6-mutlak", "F7", "F7-mutlak", "F8", "F8-mutlak", "F9", "F9-mutlak", "F10", "F10-mutlak"],
              ["Fig4_S12_KDE_Elbow", "FigS11_Deviation_Groups_Pie", "FigS13_LogLog_Histogram", "FigS14_Heliocentric_Distance_Top8", "FigS15_GroupA_vs_GroupB_Violin"]),
    "06_h3": ("Hypothesis 3 (Section 3.3)", ["Ref", "F1", "F1-mutlak", "F2", "F2-mutlak", "F3", "F3-mutlak", "F4", "F4-mutlak", "F5", "F5-mutlak",
                                             "F6", "F6-mutlak", "F7", "F7-mutlak", "F8", "F8-mutlak", "F9", "F9-mutlak", "F10", "F10-mutlak"],
              ["Fig5_S16_Stress_Test", "Fig6_S17_Network_Topology", "Fig7_S18_3D_Illustration", "FigS19_Inter_Body_Distances", "Fig8_S20_Triple_Comparison"]),
}
HUCRE = 1000      # her küçük resmin en uzun kenarı (piksel)


def font(n):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, n)
        except OSError:
            pass
    return ImageFont.load_default()


def panel(bolum, baslik, kodlar, sekil):
    yollar = [(k, os.path.join(KOK, bolum, "cikti", "formuller", k, f"{sekil}.png")) for k in kodlar]
    yollar = [(k, p) for k, p in yollar if os.path.exists(p)]
    if not yollar:
        return None
    ims = []
    for k, p in yollar:
        im = Image.open(p).convert("RGB"); im.thumbnail((HUCRE, HUCRE)); ims.append((k, im))
    w = max(im.width for _, im in ims); h = max(im.height for _, im in ims)
    sut = 5 if len(ims) > 12 else 4; sat = math.ceil(len(ims) / sut); ust = 90; et = 40
    tuval = Image.new("RGB", (sut * w, ust + sat * (h + et)), "white"); d = ImageDraw.Draw(tuval)
    d.text((20, 20), f"{baslik} — {sekil.replace('_', ' ')} — all readings (adopted reading first)", fill="black", font=font(44))
    for n, (k, im) in enumerate(ims):
        x = (n % sut) * w; y = ust + (n // sut) * (h + et)
        d.text((x + 10, y + 4), "Ref (adopted reading)" if k.startswith("Ref") and n == 0 else k.replace("-mutlak", "-abs"), fill="black", font=font(30))
        tuval.paste(im, (x + (w - im.width) // 2, y + et))
    kl = os.path.join(KOK, bolum, "cikti", "karsilastirma_EN"); os.makedirs(kl, exist_ok=True)
    out = os.path.join(kl, f"Panel_{sekil}.png"); tuval.save(out, optimize=True); return out


if __name__ == "__main__":
    for b in (sys.argv[1:] or BOLUM):
        baslik, kodlar, sekiller = BOLUM[b]
        for s in sekiller:
            print(panel(b, baslik, kodlar, s), flush=True)
