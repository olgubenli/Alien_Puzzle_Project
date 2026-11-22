# -*- coding: utf-8 -*-
"""Ortak araçlar: Wow! günü Excel verisini (salt okunur) yükler, raporları .md / .xlsx / .docx olarak yazar."""
import glob, os, pickle, sys
import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, "cikti")
CACHE = os.path.join(KOK, "cache")
os.makedirs(CIKTI, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)

MASAUSTU = os.path.dirname(os.path.dirname(KOK))
BULMACA = os.path.join(MASAUSTU, "uzaylı bulmaca")
VERI_KLASOR = os.path.join(BULMACA, "orjinal tarihler dosyalar", "wow tarihi")
BIGDATA_DB = os.path.join(BULMACA, "kopya tarihler dosyalar - Copy", "bigdata.db")
ESKI_H1_CSV = os.path.join(BULMACA, "wow_signal_19770815_matches.csv")

TARIH = "1977-08-15"
TOLERANS = 1.0  # yüzde, makaledeki Hipotez 1 ile aynı

# MPC ve SBDB sayfaları "Asteroids (Unique)" sayfasının alt kümeleri; tekrar olmasın diye alınmaz.
SAYFALAR = ["Asteroids (Unique)", "Planets", "Natural Satellites", "Dwarf Planets",
            "Artificial Satellites", "Stars", "Gas & Dust Clouds"]
GEZEGENLER = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
GEZEGEN_TR = {"Mercury": "Merkür", "Venus": "Venüs", "Earth": "Dünya", "Mars": "Mars",
              "Jupiter": "Jüpiter", "Saturn": "Satürn", "Uranus": "Uranüs", "Neptune": "Neptün"}


def veri_yukle():
    """26 harf dosyasından mesafesi olan tüm cisimler: DataFrame(isim, harf, sayfa, d). Önbellekli."""
    cp = os.path.join(CACHE, f"wow_{TARIH}.pkl")
    if os.path.exists(cp):
        return pd.read_pickle(cp)
    dosyalar = sorted(glob.glob(os.path.join(VERI_KLASOR, f"?_objects_with_RADEC_{TARIH}.xlsx")))
    assert len(dosyalar) == 26, f"26 harf dosyası bekleniyordu, {len(dosyalar)} bulundu"
    satir = []
    for f in dosyalar:
        harf = os.path.basename(f)[0]
        x = pd.ExcelFile(f)
        for s in SAYFALAR:
            if s not in x.sheet_names:
                continue
            d = x.parse(s)
            col = [c for c in d.columns if str(c).startswith("Instant_Sun_Dist")]
            if not col:
                continue
            v = pd.to_numeric(d[col[0]], errors="coerce")
            ok = v.notna() & np.isfinite(v)
            for isim, val in zip(d.loc[ok, "Object"].astype(str), v[ok]):
                satir.append((isim, harf, s, float(val)))
    df = pd.DataFrame(satir, columns=["isim", "harf", "sayfa", "d"])
    df = df.drop_duplicates("isim").reset_index(drop=True)
    df.to_pickle(cp)
    return df


def gezegenler(df):
    p = df[df.sayfa == "Planets"].set_index("isim")["d"]
    return {g: float(p[g]) for g in GEZEGENLER}


# ------------------------------------------------------------------ rapor yazıcı
class Rapor:
    """Blok listesi: ('h', seviye, metin) | ('p', metin) | ('t', başlık, DataFrame)."""

    def __init__(self, baslik):
        self.baslik = baslik
        self.bloklar = []

    def h(self, metin, seviye=2):
        self.bloklar.append(("h", seviye, metin))

    def p(self, metin):
        self.bloklar.append(("p", metin))

    def img(self, yol, aciklama="", genislik_cm=16):
        self.bloklar.append(("i", yol, aciklama, genislik_cm))

    def t(self, baslik, df, sadece_excel=False):
        self.bloklar.append(("x" if sadece_excel else "t", baslik, df.copy()))

    @staticmethod
    def _fmt(v):
        if isinstance(v, (float, np.floating)):
            if not np.isfinite(v):
                return "—"
            return f"{v:.6f}".rstrip("0").rstrip(".") if abs(v) < 1e6 else f"{v:.4g}"
        if isinstance(v, (bool, np.bool_)):
            return "Evet" if v else "Hayır"
        return "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v)

    def kaydet(self, dosya_adi, klasor=None):
        yol = os.path.join(klasor or CIKTI, dosya_adi)
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        self._md(yol + ".md")
        self._xlsx(yol + ".xlsx")
        self._docx(yol + ".docx")
        print("Kaydedildi:", yol + ".md / .xlsx / .docx")

    def _md(self, yol):
        L = [f"# {self.baslik}", ""]
        for b in self.bloklar:
            if b[0] == "i":
                rel = os.path.relpath(b[1], os.path.dirname(yol)).replace("\\", "/")
                L += [f"![{b[2]}]({rel.replace(' ', '%20')})", "", f"*{b[2]}*" if b[2] else "", ""]
            elif b[0] == "x":
                L += [f"*{b[1]}: {len(b[2])} satır — tam liste Excel dosyasında.*", ""]
            elif b[0] == "h":
                L += ["#" * b[1] + " " + b[2], ""]
            elif b[0] == "p":
                L += [b[1], ""]
            else:
                _, bas, df = b
                if bas:
                    L += [f"**{bas}**", ""]
                L.append("| " + " | ".join(map(str, df.columns)) + " |")
                L.append("|" + "---|" * len(df.columns))
                for r in df.itertuples(index=False):
                    L.append("| " + " | ".join(self._fmt(v).replace("|", "\\|") for v in r) + " |")
                L.append("")
        with open(yol, "w", encoding="utf-8") as f:
            f.write("\n".join(L))

    def _xlsx(self, yol):
        with pd.ExcelWriter(yol, engine="openpyxl") as w:
            notlar = [(b[2] if b[0] == "h" else b[1]) for b in self.bloklar if b[0] in ("h", "p")]
            notlar += [f"Grafik: {os.path.basename(b[1])} — {b[2]}" for b in self.bloklar if b[0] == "i"]
            pd.DataFrame({self.baslik: notlar}).to_excel(w, sheet_name="Açıklama", index=False)
            kullanilan = set()
            for i, b in enumerate(self.bloklar):
                if b[0] not in ("t", "x"):
                    continue
                ad = "".join(c for c in (b[1] or f"Tablo{i}") if c not in '[]:*?/\\')[:28] or f"Tablo{i}"
                while ad in kullanilan:
                    ad = ad[:25] + f"_{i}"
                kullanilan.add(ad)
                b[2].to_excel(w, sheet_name=ad, index=False)
            for ws in w.book.worksheets:
                for col in ws.columns:
                    n = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                    ws.column_dimensions[col[0].column_letter].width = min(max(10, n + 2), 70)

    def _docx(self, yol):
        from docx import Document
        from docx.shared import Pt, Cm
        doc = Document()
        doc.styles["Normal"].font.name = "Calibri"
        doc.styles["Normal"].font.size = Pt(10)
        doc.add_heading(self.baslik, 0)
        for b in self.bloklar:
            if b[0] == "i":
                if os.path.exists(b[1]):
                    doc.add_picture(b[1], width=Cm(b[3]))
                    if b[2]:
                        doc.add_paragraph().add_run(b[2]).italic = True
            elif b[0] == "x":
                doc.add_paragraph(f"{b[1]}: {len(b[2])} satır — tam liste Excel dosyasında.")
            elif b[0] == "h":
                doc.add_heading(b[2], min(b[1], 4))
            elif b[0] == "p":
                for satir in b[1].split("\n"):
                    doc.add_paragraph(satir.replace("**", "").replace("`", ""))
            else:
                _, bas, df = b
                if bas:
                    doc.add_paragraph().add_run(bas).bold = True
                tb = doc.add_table(rows=1, cols=len(df.columns))
                tb.style = "Light Grid Accent 1"
                for j, c in enumerate(df.columns):
                    tb.rows[0].cells[j].text = str(c)
                for r in df.itertuples(index=False):
                    cells = tb.add_row().cells
                    for j, v in enumerate(r):
                        cells[j].text = self._fmt(v)
                for row in tb.rows:
                    for c in row.cells:
                        for par in c.paragraphs:
                            for run in par.runs:
                                run.font.size = Pt(8)
                doc.add_paragraph()
        doc.save(yol)
