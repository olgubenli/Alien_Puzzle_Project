# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 20:25:31 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
v35_fixed:
- v34_fixed (sPet_ha hatası düzeltilmiş v33) baz alındı.
- n=100 grafiğindeki küçük yüzdelerin (<8%) 'f' (uzaklık faktörü)
  okunabilirliği artırmak için tekrar artırıldı (merkezden daha uzağa).
- f (pct>=4): 0.76 -> 0.80
- f (else): 0.78 -> 0.82
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from pathlib import Path

# --- VERİ ---
OUTDIR = Path("outputs_plots"); OUTDIR.mkdir(parents=True, exist_ok=True)

csv_1d_repeat = """object_id,horizons_id,repeat_count,window
32532 Thereus (2001 PT13),32532,1,1
"""
csv_10d_repeat = """object_id,horizons_id,repeat_count,window
10199 Chariklo (1997 CU26),10199;,2,10
C/1983 R1 (Shoemaker),1983 R1,1,10
C/1984 K1 (Shoemaker),1984 K1,1,10
C/1997 N1 (Tabur),1997 N1,1,10
C/1998 W3 (LINEAR),1998 W3,1,10
C/1999 K5 (LINEAR),1999 K5,1,10
C/1999 K8 (LINEAR),1999 K8,1,10
C/1999 U1 (Ferris),1999 U1,1,10
C/2000 A1 (Montani),2000 A1,1,10
C/2000 O1 (Koehn),2000 O1,1,10
C/2002 O7 (LINEAR),2002 O7,1,10
C/2005 B1 (Christensen),2005 B1,1,10
C/2005 Q1 (LINEAR),2005 Q1,1,10
C/2006 P1 (McNaught),2006 P1,1,10
C/2008 S3 (Boattini),2008 S3,1,10
C/2014 W10 (PANSTARRS),2014 W10,1,10
C/2015 T2 (PANSTARRS),2015 T2,1,10
C/2016 C1 (PANSTARRS),2016 C1,1,10
C/2017 E3 (PANSTARRS),2017 E3,1,10
C/2017 S7 (Lemmon),2017 S7,1,10
C/2020 W5 (Lemmon),2020 W5,1,10
C/2024 T5 (ATLAS),2024 T5,1,10
"""
csv_100d_repeat = """object_id,horizons_id,repeat_count,window
10199 Chariklo (1997 CU26),10199;,11,100
330836 Orius (2009 HW77),330836;,5,100
346889 Rhiphonos (2009 QV38),346889;,4,100
121725 Aphidas (1999 XX143),121725;,3,100
60558 Echeclus (2000 EC98),60558;,3,100
C/1979 M3 (Torres),1979 M3,2,100
C/1988 C1 (Maury-Phinney),1988 C1,2,100
C/1993 Q1 (Mueller),1993 Q1,2,100
C/1998 U1 (LINEAR),1998 U1,2,100
C/1999 S4 (LINEAR),1999 S4,2,100
C/2010 X1 (Elenin),2010 X1,2,100
C/2014 L5 (Lemmon),2014 L5,2,100
C/2015 D3 (PANSTARRS),2015 D3,2,100
C/2015 J1 (PANSTARRS),2015 J1,2,100
C/2015 X7 (ATLAS),2015 X7,2,100
C/2016 K1 (LINEAR),2016 K1,2,100
C/2017 U7 (PANSTARRS),2017 U7,2,100
C/2019 M3 (ATLAS),2019 M3,2,100
2060 Chiron (1977 UB),2060;,1,100
31824 Elatus (1999 UG5),31824;,1,100
5145 Pholus (1992 AD),5145;,1,100
5335 Damocles (1991 DA),5335;,1,100
7066 Nessus (1993 HA2),7066;,1,100
C/1956 R1 (Arend-Roland),1956 R1,1,100
C/1959 Q2 (Alcock),1959 Q2,1,100
C/1966 T1 (Rudnicki),1966 T1,1,100
C/1970 N1 (Abe),1970 N1,1,100
C/1971 E1 (Toba),1971 E1,1,100
C/1972 L1 (Sandage),1972 L1,1,100
C/1975 V1-A (West),1975 V1-A,1,100
C/1975 V2 (Bradfield),1975 V2,1,100
C/1975 X1 (Sato),1975 X1,1,100
C/1976 D2 (Schuster),1976 D2,1,100
C/1976 U1 (Lovas),1976 U1,1,100
C/1978 H1 (Meier),1978 H1,1,100
C/1979 M1 (Bradfield),1979 M1,1,100
C/1980 E1 (Bowell),1980 E1,1,100
C/1980 L1 (Torres),1980 L1,1,100
C/1986 P1-A (Wilson),1986 P1-A,1,100
C/1986 P1-B (Wilson),1986 P1-B,1,100
C/1987 A1 (Levy),1987 A1,1,100
C/1987 W3 (Jensen-Shoemaker),1987 W3,1,100
C/1988 L1 (Shoemaker-Holt-Rodriquez),1988 L1,1,100
C/1989 Q1 (Okazaki-Levy-Rudenko),1989 Q1,1,100
C/1990 K1 (Levy),1990 K1,1,100
C/1990 M1 (McNaught-Hughes),1990 M1,1,100
C/1994 N1 (Nakamura-Nishimura-Machholz),1994 N1,1,100
C/1997 D1 (Mueller),1997 D1,1,100
C/1997 J2 (Meunier-Dupouy),1997 J2,1,100
C/1997 N1 (Tabur),1997 N1,1,100
C/1998 M3 (Larsen),1998 M3,1,100
C/1999 H3 (LINEAR),1999 H3,1,100
C/1999 J2 (Skiff),1999 J2,1,100
C/1999 K8 (LINEAR),1999 K8,1,100
C/1999 S2 (McNaught-Watson),1999 S2,1,100
C/1999 Y1 (LINEAR),1999 Y1,1,100
C/2000 A1 (Montani),2000 A1,1,100
C/2000 U5 (LINEAR),2000 U5,1,100
C/2001 G1 (LONEOS),2001 G1,1,100
C/2001 RX14 (LINEAR),2001 RX14,1,100
C/2002 A3 (LINEAR),2002 A3,1,100
C/2002 E2 (Snyder-Murakami),2002 E2,1,100
C/2002 J5 (LINEAR),2002 J5,1,100
C/2003 A2 (Gleason),2003 A2,1,100
C/2003 G1 (LINEAR),2003 G1,1,100
C/2003 S3 (LINEAR),2003 S3,1,100
C/2004 X3 (LINEAR),2004 X3,1,100
C/2005 Q1 (LINEAR),2005 Q1,1,100
C/2006 E1 (McNaught),2006 E1,1,100
C/2006 K3 (McNaught),2006 K3,1,100
C/2006 OF2 (Broughton),2006 OF2,1,100
C/2006 S2 (LINEAR),2006 S2,1,100
C/2006 S3 (LONEOS),2006 S3,1,100
C/2006 YC (Catalina-Christensen),2006 YC,1,100
C/2007 JA21 (LINEAR),2007 JA21,1,100
C/2007 W3 (LINEAR),2007 W3,1,100
C/2008 A1 (McNaught),2008 A1,1,100
C/2008 FK75 (Lemmon-Siding Spring),2008 FK75,1,100
C/2009 K5 (McNaught),2009 K5,1,100
C/2009 O4 (Hill),2009 O4,1,100
C/2009 R1 (McNaught),2009 R1,1,100
C/2009 UG89 (Lemmon),2009 UG89,1,100
C/2010 F4 (Machholz),2010 F4,1,100
C/2010 U3 (Boattini),2010 U3,1,100
C/2011 F1 (LINEAR),2011 F1,1,100
C/2011 UF305 (LINEAR),2011 UF305,1,100
C/2012 E2 (SWAN),2012 E2,1,100
C/2012 F3 (PANSTARRS),2012 F3,1,100
C/2013 B2 (Catalina),2013 B2,1,100
C/2013 G2 (McNaught),2013 G2,1,100
C/2013 G9 (Tenagra),2013 G9,1,100
C/2013 J5 (Boattini),2013 J5,1,100
C/2013 L2 (Catalina),2013 L2,1,100
C/2013 S1 (Catalina),2013 S1,1,100
C/2013 V2 (Borisov),2013 V2,1,100
C/2014 AA52 (Catalina),2014 AA52,1,100
C/2014 B1 (Schwartz),2014 B1,1,100
C/2014 S1 (PANSTARRS),2014 S1,1,100
C/2014 W3 (PANSTARRS),2014 W3,1,100
C/2015 K7 (COIAS),2015 K7,1,100
C/2015 V2 (Johnson),2015 V2,1,100
C/2015 XY1 (Lemmon),2015 XY1,1,100
C/2016 E2 (Kowalski),2016 E2,1,100
C/2Z16 J2 (Denneau),2Z16 J2,1,100
C/2017 F1 (Lemmon),2017 F1,1,100
C/2017 F2 (PANSTARRS),2017 F2,1,100
C/2017 K2 (PANSTARRS),2017 K2,1,100
C/2G17 Y2 (PANSTARRS),2017 Y2,1,100
C/2018 C2 (Lemmon),2018 C2,1,100
C/2018 W2 (Africano),2018 W2,1,100
C/2019 E3 (ATLAS),2019 E3,1,100
C/2019 K1 (ATLAS),2019 K1,1,100
C/2019 M4 (TESS),2019 M4,1,100
C/2019 Q3 (PANSTARRS),2019 Q3,1,100
C/2020 N1 (PANSTARRS),2020 N1,1,100
C/2020 R7 (ATLAS),2020 R7,1,100
C/2020 T4 (PANSTARRS),2020 T4,1,100
C/2021 A1 (Leonard),2021 A1,1,100
C/2021 K3 (Catalina),2021 K3,1,100
C/2021 S1 (ATLAS),2021 S1,1,100
C/2021 X1 (Maury-Attard),2021 X1,1,100
C/2202 E2 (ATLAS),2022 E2,1,100
C/2022 K1 (Leonard),2022 K1,1,100
C/2022 O1 (ATLAS),2022 O1,1,100
C/2024 N1 (PANSTARRS),2024 N1,1,100
C/2024 N4 (Sarneczky),2024 N4,1,100
C/2024 O1 (PANSTARRS),2024 O1,1,100
C/2025 B2 (Borisov),2025 B2,1,100
C/2025 F2 (SWAN),2025 F2,1,100
C/2025 N2 (ATLAS),2025 N2,1,100
Pioneer 11,Pioneer 11,1,100
"""

# --- DataFrames ---
df_1d_rep = pd.read_csv(StringIO(csv_1d_repeat))
df_10d_rep = pd.read_csv(StringIO(csv_10d_repeat))
df_100d_rep = pd.read_csv(StringIO(csv_100d_repeat))

# --- Çiz ---
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
fig.patch.set_facecolor('white')

# n = 1 day
data_1d = df_1d_rep['repeat_count']; labels_1d = df_1d_rep['object_id']
wed1, txt1, aut1 = ax1.pie(data_1d, autopct='%1.1f%%', startangle=90,
                           colors=['#D4E6F1'], pctdistance=0.5, labels=labels_1d)
for t in txt1: t.set_fontsize(10); t.set_position((0,0)); t.set_ha('center'); t.set_va('center')
# --- DÜZELTME: '1t 0' hatası '10' olarak düzeltildi ---
for a in aut1: a.set_fontsize(10); a.set_position((0,-0.15)); a.set_ha('center'); a.set_va('center')

# n = 10 days (Chariklo radyal)
tot10 = df_10d_rep['repeat_count'].sum()
char10 = df_10d_rep[df_10d_rep['repeat_count']>1]['repeat_count'].sum()
oth10  = tot10 - char10
wed2, txt2, aut2 = ax2.pie([char10, oth10], autopct='%1.1f%%', startangle=90,
                           colors=['#AED581','#E6F5E0'], explode=(0.1,0),
                           labels=['10199 Chariklo','Others (1 repeat)'],
                           pctdistance=0.6, labeldistance=1.05, rotatelabels=True)
txt2[0].set_fontsize(10)
aut2[0].set_fontsize(9); aut2[0].set_rotation(txt2[0].get_rotation()); aut2[0].set_rotation_mode('anchor')
txt2[1].set_fontsize(10); txt2[1].set_position((0,-0.15)); txt2[1].set_ha('center'); txt2[1].set_rotation(0)
aut2[1].set_fontsize(9);  aut2[1].set_position((0,-0.35)); aut2[1].set_rotation(0)

# n = 100 days
rep1 = df_100d_rep.query('repeat_count==1')['repeat_count'].sum()
rep2 = df_100d_rep.query('repeat_count==2')['repeat_count'].sum()
top  = df_100d_rep.query('repeat_count>2').sort_values('repeat_count', ascending=False)
data100 = top['repeat_count'].tolist() + [rep2, rep1]
labels100 = ['10199 Chariklo','330836 Orius','346889 Rhiphonos','60558 Echeclus','121725 Aphidas','Repeated 2x','Repeated 1x']
colors100 = ['#C39BD3','#C39BD3','#C39BD3','#C39BD3','#C3A3D3','#E8DAEF','#F4ECF7']
exp100 = [0.1,0.1,0.1,0.1,0.1,0.1,0.05]

def autopct_inside(p): return f'{p:0.1f}%'

wed3, txt3, aut3 = ax3.pie(data100, autopct=autopct_inside, startangle=90, colors=colors100,
                           explode=exp100, labels=labels100, pctdistance=0.72,
                           labeldistance=1.05,
                           rotatelabels=True, # (v32'deki gibi çapraz)
                           wedgeprops={'edgecolor':'white','linewidth':1.5})

# --- GÜNCELLENEN BÖLÜM ---
# Genel autopct iç yerleşim
for w,t,a in zip(wed3, txt3, aut3):
    pct = float(a.get_text().replace('%',''))
    
    # Yüzde ve uzaklık faktörlerini optimize edelim
    if pct >= 12:   fs, f = 9, 0.84 # (Büyük dilimler için)
    elif pct >= 8:  fs, f = 8, 0.80 # (8%-12% arası için)
    elif pct >= 4:  fs, f = 8, 0.80 # <-- DEĞİŞİKLİK: (Chariklo 6.7%) f=0.76 -> 0.80
    else:           fs, f = 8, 0.82 # <-- DEĞİŞİKLİK: (Diğer küçükler) f=0.78 -> 0.82
    
    a.set_fontsize(fs); a.set_color('black'); a.set_ha('center'); a.set_va('center')
    x,y = a.get_position(); a.set_position((x*f, y*f))
    a.set_rotation(t.get_rotation()) # (v32'deki gibi rotasyonu koru)
    a.set_rotation_mode('anchor')

# ---- Repeated 2x (index 5): etiket + yüzde, 1 SATIR AŞAĞI ----
# (Bu bölüm v32'deki gibi kaldı, "15.8%" altta ve DÜZ)
w   = wed3[5]
ang = np.deg2rad((w.theta1 + w.theta2)/2.0)
cx, cy = w.center; r = w.r

r_label = 0.62          # etiket yarıçapı
# Etiket konumu
xL = cx + r * r_label * np.cos(ang)
yL = cy + r * r_label * np.sin(ang)

# Yüzde, etiketin dikey olarak 1 satır altına (overlap düzeltmesi)
xP = xL          # Etiketle aynı X koordinatı
yP = yL - 0.18   # Etiketin Y koordinatından biraz aşağıda (index 6'daki gibi)

txt3[5].set_position((xL, yL)); txt3[5].set_rotation(0)
txt3[5].set_ha('center'); txt3[5].set_va('center'); txt3[5].set_fontsize(9)

aut3[5].set_position((xP, yP)); aut3[5].set_rotation(0)
aut3[5].set_ha('center'); aut3[5].set_va('center'); aut3[5].set_fontsize(8)

# Repeated 1x (index 6) aynı
# --- DÜZELTME: 'sPet_ha' hatası 'set_ha' olarak düzeltildi ---
txt3[6].set_position((0.024, -0.22)); txt3[6].set_rotation(0); txt3[6].set_ha('center'); txt3[6].set_fontsize(9)
aut3[6].set_position((0.024, -0.4));  aut3[6].set_rotation(0)

# Başlıklar
fig.tight_layout(rect=[0.05,0.15,0.95,0.9])
SPACE=0.012
fig.text(0.20,0.12,'n = 1 day',ha='center',fontsize=12)
fig.text(0.50+0.5*SPACE,0.12,'n = 10 days',ha='center',fontsize=12)
fig.text(0.80+1.0*SPACE,0.12,'n = 100 days',ha='center',fontsize=12)

# Kaydet
png = OUTDIR / "repeat_count_pie_charts_summary_FINAL_v35_fixed.png"
pdf = OUTDIR / "repeat_count_pie_charts_summary_FINAL_v35_fixed.pdf"
fig.savefig(png, dpi=300, facecolor='white')
fig.savefig(pdf, facecolor='white')
print("- ", png.name, "\n- ", pdf.name)