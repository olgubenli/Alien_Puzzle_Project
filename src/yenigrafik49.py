# -*- coding: utf-8 -*-

"""

Created on Sun Oct 26 16:56:14 2025



@author: olgub

"""



# -*- coding: utf-8 -*-

# ANALYSIS PLOTS FOR 1d / 10d / 100d WINDOWS (Publication-ready, Matplotlib)

# Author: you+assistant

# Requirements: pandas, numpy, matplotlib



import pandas as pd

import numpy as np

import matplotlib.pyplot as plt

from io import StringIO

from pathlib import Path

from matplotlib.colors import BoundaryNorm # discrete heatmap scale

# Inset (PIP) için yeni kütüphane

from mpl_toolkits.axes_grid1.inset_locator import Bbox

from matplotlib.ticker import MultipleLocator # Minor ticks için eklendi

import colorsys

from matplotlib.colors import to_rgba

# plot_presence_matrix için eklendi

from mpl_toolkits.axes_grid1.inset_locator import inset_axes



# --- YENİ EKLENEN KÜTÜPHANELER (AU Color Map için) ---

import matplotlib.colors as mcolors

from matplotlib import cm

# --- YENİ EKLENEN KÜTÜPHANELER (Grafik J Lejantı için) ---

from matplotlib.lines import Line2D

from matplotlib.patches import Patch

# --- KORELASYON ANALİZİ İÇİN YENİ KÜTÜPHANE ---

from scipy import stats

# --- ---



# --- YENİ EKLENEN KÜTÜPHANELER (AU Color Map için) ---

import matplotlib.colors as mcolors

from matplotlib import cm

# --- YENİ EKLENEN KÜTÜPHANELER (Grafik J Lejantı için) ---

from matplotlib.lines import Line2D

from matplotlib.patches import Patch





# Korelasyon Analizi için (Grafik J)

from scipy.stats import spearmanr





# ----- YENİ EKLENEN KÜTÜPHANELER (L & M: Regresyon Analizi için) -----

from sklearn.linear_model import LinearRegression

from sklearn.preprocessing import PolynomialFeatures

from sklearn.pipeline import make_pipeline

from sklearn.metrics import r2_score

# --- ---





# Kümeleme Analizi için (Grafik N)

from sklearn.cluster import DBSCAN

from sklearn.preprocessing import StandardScaler

# --- ---



# Ki-Kare Analizi için (Grafik O)

from scipy.stats import chi2_contingency

# --- ---









# ----------------------------- #

# 0) GLOBAL SETTINGS (PAPER)

# ----------------------------- #

AU_MIN = 0.146557

AU_MAX = 800.253762

# TOP_N artık sadece eski plot_presence_matrix için kullanılıyor

TOP_N_OLD = 30



# Font sizes for publication (Genel ayarlar)

# plot_presence_matrix_100d içinde daha küçük fontlar override edilebilir

plt.rcParams.update({

    "figure.dpi": 100,

    "savefig.dpi": 300,

    "font.size": 10,

    "axes.titlesize": 11,

    "axes.labelsize": 10,

    "xtick.labelsize": 9,

    "ytick.labelsize": 9,

    "legend.fontsize": 9,

})



OUTDIR = Path("outputs_plots")

OUTDIR.mkdir(parents=True, exist_ok=True)



# ----------------------------- #

# 1) RAW DATA (EMBEDDED)

#    You provided these tables.

# ----------------------------- #



# --- 1d Verisi ---

csv_1d_matches = """object_id,horizons_id,au,object_type,day,window

32532 Thereus (2001 PT13),32532,12.361452,Asteroids,1977-08-15,1

"""

df_1d = pd.read_csv(StringIO(csv_1d_matches), parse_dates=["day"])

csv_1d_repeat = """object_id,horizons_id,repeat_count,window

32532 Thereus (2001 PT13),32532,1,1

"""

df_1d_rep = pd.read_csv(StringIO(csv_1d_repeat))



# --- 10d Verisi ---

csv_10d_matches = """object_id,horizons_id,au,object_type,day,window

C/1984 K1 (Shoemaker),1984 K1,12.061745,Asteroids,1981-09-01,10

C/1983 R1 (Shoemaker),1983 R1,12.973974,Asteroids,1988-06-23,10

C/1997 N1 (Tabur),1997 N1,12.814228,Asteroids,1994-01-10,10

C/1998 W3 (LINEAR),1998 W3,12.750168,Asteroids,1994-01-10,10

C/1999 U1 (Ferris),1999 U1,12.800197,Asteroids,1994-01-10,10

10199 Chariklo (1997 CU26),10199;,13.428591,Asteroids,1999-08-14,10

C/2002 O7 (LINEAR),2002 O7,13.580322,Asteroids,1999-08-14,10

10199 Chariklo (1997 CU26),10199;,13.10234,Asteroids,2005-02-28,10

C/1999 K5 (LINEAR),1999 K5,13.173429,Asteroids,2005-02-28,10

C/1999 K8 (LINEAR),1999 K8,13.169699,Asteroids,2005-02-28,10

C/2000 A1 (Montani),2000 A1,13.291389,Asteroids,2005-02-28,10

C/2000 O1 (Koehn),2000 O1,13.237278,Asteroids,2005-02-28,10

C/2005 B1 (Christensen),2005 B1,13.47292,Asteroids,2010-12-05,10

C/2005 Q1 (LINEAR),2005 Q1,13.545696,Asteroids,2010-12-05,10

C/2006 P1 (McNaught),2006 P1,13.736831,Asteroids,2010-12-05,10

C/2014 W10 (PANSTARRS),2014 W10,13.474429,Asteroids,2010-12-05,10

C/2016 C1 (PANSTARRS),2016 C1,13.616862,Asteroids,2010-12-05,10

C/2008 S3 (Boattini),2008 S3,13.009327,Asteroids,2016-04-19,10

C/2020 W5 (Lemmon),2020 W5,13.058144,Asteroids,2016-04-19,10

C/2015 T2 (PANSTARRS),2015 T2,13.336196,Asteroids,2022-07-22,10

C/2017 E3 (PANSTARRS),2017 E3,13.327859,Asteroids,2022-07-22,10

C/2017 S7 (Lemmon),2017 S7,13.384712,Asteroids,2022-07-22,10

C/2024 T5 (ATLAS),2024 T5,13.207571,Asteroids,2022-07-22,10

"""

df_10d = pd.read_csv(StringIO(csv_10d_matches), parse_dates=["day"])

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

df_10d_rep = pd.read_csv(StringIO(csv_10d_repeat))



# --- 100d Verisi ---

csv_100d_matches = """object_id,horizons_id,au,object_type,day,window

C/1956 R1 (Arend-Roland),1956 R1,12.057273,Asteroids,1960-07-11,100

C/1959 Q2 (Alcock),1959 Q2,12.119094,Asteroids,1962-12-03,100

C/1966 T1 (Rudnicki),1966 T1,12.173256,Asteroids,1963-09-18,100

346889 Rhiphonos (2009 QV38),346889;,11.765358,Asteroids,1966-10-30,100

C/1976 U1 (Lovas),1976 U1,11.799032,Asteroids,1972-03-21,100

C/1970 N1 (Abe),1970 N1,12.11272,Asteroids,1974-05-16,100

C/1979 M3 (Torres),1979 M3,12.216004,Asteroids,1975-02-04,100

C/1980 E1 (Bowell),1980 E1,12.271511,Asteroids,1978-01-19,100

121725 Aphidas (1999 XX143),121725;,12.056397,Asteroids,1979-04-05,100

C/1975 V2 (Bradfield),1975 V2,12.202213,Asteroids,1979-04-05,100

346889 Rhiphonos (2009 QV38),346889;,12.063333,Asteroids,1982-02-17,100

C/1987 A1 (Levy),1987 A1,12.278792,Asteroids,1983-05-24,100

5145 Pholus (1992 AD),5145;,12.622428,Asteroids,1985-08-11,100

C/1990 K1 (Levy),1990 K1,12.879355,Asteroids,1986-12-28,100

2060 Chiron (1977 UB),2060;,13.020158,Asteroids,1987-07-15,100

60558 Echeclus (2000 EC98),60558;,12.76268,Asteroids,1989-01-08,100

C/1994 N1 (Nakamura-Nishimura-Machholz),1994 N1,12.705727,Asteroids,1990-09-13,100

C/1986 P1-A (Wilson),1986 P1-A,12.764158,Asteroids,1991-03-05,100

C/1986 P1-B (Wilson),1986 P1-B,12.771709,Asteroids,1991-03-05,100

C/1987 W3 (Jensen-Shoemaker),1987 W3,12.66305,Asteroids,1992-06-20,100

C/1998 M3 (Larsen),1998 M3,12.699285,Asteroids,1993-10-02,100

C/1998 U1 (LINEAR),1998 U1,12.71676,Asteroids,1993-10-02,100

C/1997 J2 (Meunier-Dupouy),1997 J2,12.82872,Asteroids,1993-10-02,100

C/1988 L1 (Shoemaker-Holt-Rodriquez),1988 L1,12.852298,Asteroids,1993-10-02,100

C/1999 J2 (Skiff),1999 J2,13.000352,Asteroids,1995-04-22,100

C/1999 S4 (LINEAR),1999 S4,13.216208,Asteroids,1996-08-30,100

C/1999 Y1 (LINEAR),1999 Y1,13.074899,Asteroids,1996-08-30,100

7066 Nessus (1993 HA2),7066;,13.2093,Asteroids,1996-08-30,100

C/1993 Q1 (Mueller),1993 Q1,13.511649,Asteroids,1998-05-03,100

10199 Chariklo (1997 CU26),10199;,13.361985,Asteroids,2000-01-23,100

C/2003 A2 (Gleason),2003 A2,13.365048,Asteroids,2000-01-23,100

346889 Rhiphonos (2009 QV38),346889;,13.54599,Asteroids,2000-01-23,100

C/1997 N1 (Tabur),1997 N1,13.522876,Asteroids,2001-07-07,100

C/2006 S2 (LINEAR),2006 S2,13.19103,Asteroids,2002-09-19,100

C/2006 K3 (McNaught),2006 K3,13.227071,Asteroids,2002-09-19,100

330836 Orius (2009 HW77),330836;,13.410914,Asteroids,2002-09-19,100

C/1998 U1 (LINEAR),1998 U1,13.230192,Asteroids,2003-03-12,100

330836 Orius (2009 HW77),330836;,13.226503,Asteroids,2003-03-12,100

10199 Chariklo (1997 CU26),10199;,13.079301,Asteroids,2004-06-18,100

C/1999 S4 (LINEAR),1999 S4,13.176276,Asteroids,2004-06-18,100

10199 Chariklo (1997 CU26),10199;,13.176944,Asteroids,2006-04-09,100

C/2002 E2 (Snyder-Murakami),2002 E2,13.161532,Asteroids,2006-04-09,100

C/2013 J5 (Boattini),2013 J5,13.455851,Asteroids,2007-10-25,100

10199 Chariklo (1997 CU26),10199;,13.354361,Asteroids,2007-10-25,100

C/2010 X1 (Elenin),2010 X1,13.421261,Asteroids,2007-10-25,100

10199 Chariklo (1997 CU26),10199;,13.39332,Asteroids,2008-01-31,100

C/2003 G1 (LINEAR),2003 G1,13.241877,Asteroids,2008-01-31,100

C/2011 UF305 (LINEAR),2011 UF305,13.449562,Asteroids,2008-01-31,100

10199 Chariklo (1997 CU26),10199;,13.664406,Asteroids,2009-08-27,100

C/2014 L5 (Lemmon),2014 L5,13.494066,Asteroids,2009-08-27,100

C/2015 D3 (PANSTARRS),2015 D3,13.551283,Asteroids,2011-02-14,100

C/2007 W3 (LINEAR),2007 W3,13.61917,Asteroids,2012-11-09,100

C/2017 F1 (Lemmon),2017 F1,13.489589,Asteroids,2012-11-09,100

C/2008 A1 (McNaught),2008 A1,13.443229,Asteroids,2012-11-09,100

C/2014 B1 (Schwartz),2014 B1,13.474282,Asteroids,2012-11-09,100

C/2019 Q3 (PANSTARRS),2019 Q3,13.597094,Asteroids,2013-05-01,100

C/2019 M3 (ATLAS),2019 M3,13.223771,Asteroids,2014-07-23,100

C/2009 O4 (Hill),2009 O4,13.366932,Asteroids,2014-07-23,100

C/2009 K5 (McNaught),2009 K5,13.423127,Asteroids,2014-07-23,100

C/2017 U7 (PANSTARRS),2017 U7,13.297756,Asteroids,2014-07-23,100

C/2008 FK75 (Lemmon-Siding Spring),2008 FK75,13.234082,Asteroids,2015-09-04,100

C/2009 UG89 (Lemmon),2009 UG89,13.061826,Asteroids,2015-09-04,100

C/2015 K7 (COIAS),2015 K7,12.990218,Asteroids,2017-06-11,100

C/2021 X1 (Maury-Attard),2021 X1,13.095546,Asteroids,2018-10-18,100

C/2014 S1 (PANSTARRS),2014 S1,13.195659,Asteroids,2018-10-18,100

C/2017 K2 (PANSTARRS),2017 K2,13.015091,Asteroids,2018-10-18,100

C/2022 E2 (ATLAS),2022 E2,13.141698,Asteroids,2019-12-25,100

C/2014 L5 (Lemmon),2014 L5,13.19922,Asteroids,2019-12-25,100

C/2012 F3 (PANSTARRS),2012 F3,13.242103,Asteroids,2019-12-25,100

C/2024 N4 (Sarneczky),2024 N4,13.239412,Asteroids,2019-12-25,100

C/2013 G9 (Tenagra),2013 G9,13.045612,Asteroids,2019-12-25,100

C/2025 N2 (ATLAS),2025 N2,13.160774,Asteroids,2020-03-09,100

C/2025 B2 (Borisov),2025 B2,13.359779,Asteroids,2021-08-16,100

C/2015 V2 (Johnson),2015 V2,13.16286,Asteroids,2021-08-16,100

C/2025 F2 (SWAN),2025 F2,13.150077,Asteroids,2021-08-16,100

C/2017 F2 (PANSTARRS),2017 F2,13.24814,Asteroids,2023-01-04,100

C/2019 K1 (ATLAS),2019 K1,13.124568,Asteroids,2024-05-29,100

C/2019 M4 (TESS),2019 M4,13.166621,Asteroids,2024-05-29,100

C/2021 A1 (Leonard),2021 A1,12.847927,Asteroids,2025-09-15,100

C/2017 Y2 (PANSTARRS),2017 Y2,13.064829,Asteroids,2025-09-15,100

121725 Aphidas (1999 XX143),121725;,11.712108,Asteroids,1968-09-05,100

C/1972 L1 (Sandage),1972 L1,11.827043,Asteroids,1968-09-05,100

C/1971 E1 (Toba),1971 E1,12.230323,Asteroids,1974-12-11,100

C/1979 M1 (Bradfield),1979 M1,12.181723,Asteroids,1976-03-18,100

C/1980 L1 (Torres),1980 L1,12.301341,Asteroids,1976-03-18,100

C/1978 H1 (Meier),1978 H1,12.274834,Asteroids,1982-07-01,100

Pioneer 11,Pioneer 11,12.117961,Artificial Satellites,1982-07-01,100

346889 Rhiphonos (2009 QV38),346889;,12.332542,Asteroids,1982-07-01,100

C/1988 C1 (Maury-Phinney),1988 C1,12.357418,Asteroids,1984-01-20,100

C/1979 M3 (Torres),1979 M3,12.360509,Asteroids,1984-01-20,100

5335 Damocles (1991 DA),5335;,12.614808,Asteroids,1985-11-06,100

60558 Echeclus (2000 EC98),60558;,12.999013,Asteroids,1989-05-19,100

C/1988 C1 (Maury-Phinney),1988 C1,12.809206,Asteroids,1992-02-11,100

C/1997 D1 (Mueller),1997 D1,12.711415,Asteroids,1993-08-09,100

C/1989 Q1 (Okazaki-Levy-Rudenko),1989 Q1,12.937936,Asteroids,1993-08-09,100

C/1999 K8 (LINEAR),1999 K8,12.953719,Asteroids,1995-07-28,100

C/2000 U5 (LINEAR),2000 U5,13.018462,Asteroids,1995-07-28,100

C/1990 M1 (McNaught-Hughes),1990 M1,12.976473,Asteroids,1995-07-28,100

C/2000 A1 (Montani),2000 A1,13.059378,Asteroids,1996-02-02,100

C/2003 S3 (LINEAR),2003 S3,13.274495,Asteroids,1998-03-29,100

C/1993 Q1 (Mueller),1993 Q1,13.28742,Asteroids,1998-03-29,100

C/2004 X3 (LINEAR),2004 X3,13.478014,Asteroids,2000-06-07,100

C/2005 Q1 (LINEAR),2005 Q1,13.442653,Asteroids,2000-06-07,100

C/2007 JA21 (LINEAR),2007 JA21,13.324559,Asteroids,2001-10-15,100

C/2006 E1 (McNaught),2006 E1,13.476825,Asteroids,2001-10-15,100

C/1999 S2 (McNaught-Watson),1999 S2,13.141066,Asteroids,2002-12-08,100

330836 Orius (2009 HW77),330836;,13.324083,Asteroids,2002-12-08,100

C/2006 OF2 (Broughton),2006 OF2,13.136465,Asteroids,2004-04-16,100

10199 Chariklo (1997 CU26),10199;,13.076515,Asteroids,2004-04-16,100

C/1999 H3 (LINEAR),1999 H3,13.089556,Asteroids,2004-04-16,100

10199 Chariklo (1997 CU26),10199;,13.221138,Asteroids,2006-09-24,100

C/2001 G1 (LONEOS),2001 G1,13.206561,Asteroids,2006-09-24,100

C/2009 R1 (McNaught),2009 R1,13.238778,Asteroids,2GEÇ-09-24,100

10199 Chariklo (1997 CU26),10199;,13.299948,Asteroids,2007-05-30,100

C/2001 RX14 (LINEAR),2001 RX14,13.258993,Asteroids,2007-05-30,100

C/2002 A3 (LINEAR),2002 A3,13.205672,Asteroids,2007-05-30,100

C/2013 S1 (Catalina),2013 S1,13.383226,Asteroids,2008-12-13,100

10199 Chariklo (1997 CU26),10199;,13.534375,Asteroids,2008-12-13,100

31824 Elatus (1999 UG5),31824;,13.544936,Asteroids,2008-12-13,100

C/2002 J5 (LINEAR),2002 J5,13.520464,Asteroids,2GEÇ-12-13,100

C/2014 W3 (PANSTARRS),2014 W3,13.436829,Asteroids,2008-12-13,100

C/2012 E2 (SWAN),2012 E2,13.369002,Asteroids,2008-12-13,100

10199 Chariklo (1997 CU26),10199;,13.582892,Asteroids,2009-03-22,100

C/2015 J1 (PANSTARRS),2015 J1,13.562974,Asteroids,2009-03-22,100

C/2015 X7 (ATLAS),2015 X7,13.52426,Asteroids,2011-09-01,100

330836 Orius (2009 HW77),330836;,13.510959,Asteroids,2011-09-01,100

C/2010 U3 (Boattini),2010 U3,13.38825,Asteroids,2014-02-09,100

C/2018 C2 (Lemmon),2018 C2,13.224711,Asteroids,2014-02-09,100

C/2010 F4 (Machholz),2010 F4,13.21085,Asteroids,2014-02-09,100

C/2018 W2 (Africano),2018 W2,13.319913,Asteroids,2015-06-27,100

C/2010 X1 (Elenin),2010 X1,13.236284,Asteroids,2015-06-27,100

C/2021 S1 (ATLAS),2021 S1,12.98936,Asteroids,2017-03-14,100

C/2022 O1 (ATLAS),2022 O1,12.998289,Asteroids,2017-03-14,100

C/2013 L2 (Catalina),2013 L2,12.951841,Asteroids,2017-03-14,100

C/2021 K3 (Catalina),2021 K3,12.973965,Asteroids,2017-03-14,100

C/2006 S3 (LONEOS),2006 S3,13.037608,Asteroids,2017-03-14,100

C/2011 F1 (LINEAR),2011 F1,13.000802,Asteroids,2017-03-14,100

C/2022 K1 (Leonard),2022 K1,13.089505,Asteroids,2017-03-14,100

C/2013 G2 (McNaught),2013 G2,12.981541,Asteroids,2017-03-14,100

C/2020 N1 (PANSTARRS),2020 N1,12.96548,Asteroids,2017-03-14,100

C/2020 T4 (PANSTARRS),2020 T4,13.052839,Asteroids,2017-03-14,100

C/2020 R7 (ATLAS),2020 R7,13.15732,Asteroids,2018-02-20,100

C/2013 B2 (Catalina),2013 B2,12.933129,Asteroids,2018-02-20,100

C/2ZREİ O1 (PANSTARRS),2024 O1,12.94947,Asteroids,2018-02-20,100

C/2019 E3 (ATLAS),2019 E3,13.267216,Asteroids,2019-07-04,100

C/2013 V2 (Borisov),2013 V2,13.210703,Asteroids,2019-07-04,100

C/2014 AA52 (Catalina),2014 AA52,13.265321,Asteroids,2019-07-04,100

C/2015 J1 (PANSTARRS),2015 J1,13.089684,Asteroids,2019-07-04,100

C/2016 K1 (LINEAR),2016 K1,13.088577,Asteroids,2020-11-21,100

C/2024 N1 (PANSTARRS),2024 N1,13.244011,Asteroids,2020-11-21,100

C/2015 X7 (ATLAS),2015 X7,13.159067,Asteroids,2021-04-26,100

C/2015 D3 (PANSTARRS),2015 D3,13.225276,Asteroids,2021-04-26,100

C/2019 M3 (ATLAS),2019 M3,13.139592,Asteroids,2023-06-03,100

C/2015 XY1 (Lemmon),2015 XY1,13.351281,Asteroids,2023-06-03,100

60558 Echeclus (2000 EC98),60558;,13.107327,Asteroids,2024-09-10,100

C/2017 U7 (PANSTARRS),2017 U7,13.035074,Asteroids,2024-09-10,100

121725 Aphidas (1999 XX143),121725;,12.197575,Asteroids,1979-06-15,100

C/1975 X1 (Sato),1975 X1,12.050436,Asteroids,1979-06-15,100

C/1976 D2 (Schuster),1976 D2,12.06943,Asteroids,1979-06-15,100

C/1975 V1-A (West),1975 V1-A,12.274791,Asteroids,1979-06-15,100

C/2006 YC (Catalina-Christensen),2006 YC,13.655089,Asteroids,2011-11-30,100

C/2016 J2 (Denneau),2016 J2,13.67682,Asteroids,2011-11-30,100

C/2016 E2 (Kowalski),2016 E2,13.619625,Asteroids,2011-11-30,100

C/2016 K1 (LINEAR),2016 K1,13.668287,Asteroids,2011-11-30,100

330836 Orius (2009 HW77),330836;,13.617109,Asteroids,2011-11-30,100

"""

# --- TEMİZLENMİŞ BLOK BİTTİ ---



# Tarih düzeltmeleri

csv_100d_matches = csv_100d_matches.replace("2İNDİ-12-13", "2008-12-13")

csv_100d_matches = csv_100d_matches.replace("2Oc06-09-24", "2006-09-24")



# YENİ EKLENEN DÜZELTME SATIRI:

csv_100d_matches = csv_100d_matches.replace("2GEÇ-12-13", "2008-12-13") # <--- BU SATIRI EKLE

# HATA İÇİN YENİ EKLEME (BU SATIRI EKLE):

csv_100d_matches = csv_100d_matches.replace("2GEÇ-09-24", "2006-09-24") # <--- HATA VEREN DİZE BUYDU



df_100d = pd.read_csv(StringIO(csv_100d_matches), parse_dates=["day"])



# --- GÜNCELLENMİŞ VE TEMİZLENMİŞ 100D_REPEATS BLOKU ---

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

C/2016 J2 (Denneau),2016 J2,1,100

C/2017 F1 (Lemmon),2017 F1,1,100

C/2017 F2 (PANSTARRS),2017 F2,1,100

C/2017 K2 (PANSTARRS),2017 K2,1,100

C/2017 Y2 (PANSTARRS),2017 Y2,1,100

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

C/2ZREİ E2 (ATLAS),2022 E2,1,100

C/2ZREİ K1 (Leonard),2022 K1,1,100

C/2ZREİ O1 (ATLAS),2022 O1,1,100

C/2024 N1 (PANSTARRS),2024 N1,1,100

C/2024 N4 (Sarneczky),2024 N4,1,100

C/2024 O1 (PANSTARRS),2024 O1,1,100

C/2025 B2 (Borisov),2025 B2,1,100

C/2025 F2 (SWAN),2025 F2,1,100

C/2025 N2 (ATLAS),2025 N2,1,100

Pioneer 11,Pioneer 11,1,100

"""

# --- TEMİZLENMİŞ BLOK BİTTİ ---

df_100d_rep = pd.read_csv(StringIO(csv_100d_repeat))



# ----------------------------- #

# 2) CONCAT & BASIC PREP

# ----------------------------- #



# Veri setlerindeki çöp satırları (NaN olanları) temizle

df_1d = df_1d.dropna(subset=['window'])

df_10d = df_10d.dropna(subset=['window'])

df_100d = df_100d.dropna(subset=['window'])

df_1d_rep = df_1d_rep.dropna(subset=['window'])

df_10d_rep = df_10d_rep.dropna(subset=['window'])

df_100d_rep = df_100d_rep.dropna(subset=['window'])





df_matches = pd.concat([df_1d, df_10d, df_100d], ignore_index=True)

df_repeats = pd.concat([df_1d_rep, df_10d_rep, df_100d_rep], ignore_index=True)



# Ensure dtypes (Veri temizlendi, bu satırlar artık hata vermemeli)

df_matches["window"] = df_matches["window"].astype(int)

df_repeats["window"] = df_repeats["window"].astype(int)



# For plotting daily counts & heatmaps we need day sorted

df_matches = df_matches.sort_values(["window", "day"]).reset_index(drop=True)



# ----------------------------- #

# 3) PLOTTING HELPERS

# ----------------------------- #



def savefig(fig, basename: str):

    # *** HATA DÜZELTİLDİ: U+00A0 -> Boşluk ***

    png = OUTDIR / f"{basename}.png"

    pdf = OUTDIR / f"{basename}.pdf"

    fig.savefig(png, bbox_inches="tight")

    fig.savefig(pdf, bbox_inches="tight")

    print(f"Saved: {png.name}, {pdf.name}")



# --- plot_daily_counts, plot_au_heatmap, plot_presence_matrix (eski),

# --- plot_au_distribution, plot_au_stripplot, plot_au_vs_repeat

# --- fonksiyonları burada, değişmedi ---

def plot_daily_counts(df_win: pd.DataFrame):

    if df_win.empty: return # Veri yoksa çizme

    g = df_win.groupby("day")["object_id"]

    unique_counts = g.nunique()

    total_counts = g.size()

    extra = total_counts - unique_counts



    days = unique_counts.index.values

    fig = plt.figure(figsize=(8, 3.2))

    plt.bar(days, unique_counts.values, label="Unique")

    plt.bar(days, extra.values, bottom=unique_counts.values, label="Extra repeats", alpha=0.6)

    ma = unique_counts.rolling(7, min_periods=1).mean()

    plt.plot(days, ma.values, linewidth=2, label="7-day MA")

    plt.xlabel("Date"); plt.ylabel("Detections (stacked)")

    w = int(df_win["window"].iloc[0])

    plt.title(f"Daily counts — Window {w}d")

    plt.legend(loc="upper right", frameon=False)

    plt.tight_layout()

    savefig(fig, f"daily_counts_{w}d")

    plt.close(fig)



def plot_au_heatmap(df_win: pd.DataFrame):

    if df_win.empty: return # Veri yoksa çizme

    bins = np.geomspace(AU_MIN, AU_MAX, 20)

    days_sorted = np.sort(df_win["day"].unique())

    day_to_idx = {d:i for i,d in enumerate(days_sorted)}

    day_idx = df_win["day"].map(day_to_idx).values



    H, xedges, yedges = np.histogram2d(

        day_idx, df_win["au"].values,

        bins=[np.arange(-0.5, len(days_sorted)+0.5, 1), bins]

    )



    H = np.clip(H, 0, 11)

    Hm = np.ma.masked_where(H == 0, H)

    cmap = plt.get_cmap("viridis", 11)

    cmap.set_under("#f5f5ff")

    bounds = np.arange(0.5, 11.5, 1.0)

    norm = BoundaryNorm(bounds, cmap.N)



    fig = plt.figure(figsize=(8, 3.2))

    im = plt.imshow(

        Hm.T, aspect='auto', origin='lower',

        extent=[-0.5, len(days_sorted)-0.5, bins.min(), bins.max()],

        cmap=cmap, norm=norm

    )

    plt.yscale("log")

    tick_idx = np.linspace(0, len(days_sorted)-1, num=min(6, len(days_sorted)), dtype=int)

    plt.xticks(tick_idx, [pd.to_datetime(days_sorted[i]).date() for i in tick_idx], rotation=0)



    cbar = plt.colorbar(im, ticks=np.arange(1, 12))

    cbar.set_label("Detections")



    w = int(df_win["window"].iloc[0])

    plt.title(f"AU heatmap — Window {w}d")

    plt.xlabel("Date"); plt.ylabel("AU (log)")

    plt.tight_layout()

    savefig(fig, f"au_heatmap_{w}d")

    plt.close(fig)



def plot_presence_matrix(df_win: pd.DataFrame, df_rep_win: pd.DataFrame, top_n: int = TOP_N_OLD): # TOP_N_OLD kullanıldı

    if df_win.empty or df_rep_win.empty: return # Veri yoksa çizme

    rep_sorted = df_rep_win.sort_values("repeat_count", ascending=False)

    top_ids = list(rep_sorted["object_id"].head(top_n))

    sub = df_win[df_win["object_id"].isin(top_ids)].copy()

    days_sorted = np.sort(sub["day"].unique())

    day_to_idx = {d:i for i,d in enumerate(days_sorted)}



    objects = [obj for obj in rep_sorted['object_id'] if obj in top_ids]

    objects.reverse() # En çok tekrar eden en üstte olsun diye ters çevir

    obj_to_idx = {obj: i for i, obj in enumerate(objects)}





    mat = np.zeros((len(objects), len(days_sorted)), dtype=int)

    for i, oid in enumerate(objects):

        dset = sub.loc[sub["object_id"]==oid, "day"].unique()

        if not dset.size > 0:

            continue



        mat_row_idx = obj_to_idx[oid]

        for d in dset:

            if d in day_to_idx:

                mat[mat_row_idx, day_to_idx[d]] = 1



    fig = plt.figure(figsize=(9, 5))

    ax = plt.gca()

    # Eksenleri ters çevir: y=0 en üstte olsun (imshow default)

    ax.imshow(mat, aspect='auto', origin='upper', cmap='Greys')



    ax.set_yticks(range(len(objects)))

    # Ters çevrilmiş object listesini kullanma, normal sıralı kullan

    ax.set_yticklabels([objects[i] for i in range(len(objects))], fontsize=6) # Doğru sıra



    tick_idx = np.linspace(0, len(days_sorted)-1, num=min(6, len(days_sorted)), dtype=int)

    ax.set_xticks(tick_idx)

    ax.set_xticklabels([pd.to_datetime(days_sorted[i]).date() for i in tick_idx], rotation=0)

    ax.set_xlabel("Date"); ax.set_ylabel("Object (Top by repeats)")



    rep_map = {r["object_id"]: r["repeat_count"] for _, r in rep_sorted.iterrows()}

    # Bar grafiği için rep_vals'ı da doğru sırada al

    rep_vals = [rep_map.get(oid, 0) for oid in objects]



    ax_bar = inset_axes(ax, width="12%", height="100%", loc='right',

                        bbox_to_anchor=(1.05, 0.0, 1.0, 1.0),

                        bbox_transform=ax.transAxes,

                        borderpad=0)

    # Bar grafiğini doğru sırada çiz

    ax_bar.barh(range(len(objects)), rep_vals)

    ax_bar.set_yticks([])

    ax_bar.set_xlabel("Repeat")

    ax_bar.invert_yaxis() # y eksenini ters çevir ki ana grafikle eşleşsin



    w = int(df_win["window"].iloc[0])

    ax.set_title(f"Presence matrix — Window {w}d")



    savefig(fig, f"presence_matrix_{w}d")

    plt.close(fig)



def plot_au_distribution(df_all: pd.DataFrame):

    if df_all.empty: return # Veri yoksa çizme

    data = [df_all[df_all["window"]==w]["au"].values for w in [1,10,100]]

    labels = ["1d","10d","100d"]



    fig = plt.figure(figsize=(7.2, 4.0))

    ax = plt.gca()



    valid_data = []

    valid_positions = []

    for i, d in enumerate(data, start=1):

        # Sadece 1'den fazla veri noktası varsa violin çiz

        if len(d) > 1:

            valid_data.append(d)

            valid_positions.append(i)



    if valid_data:

        # Violin plot'u çiz

        parts = ax.violinplot(valid_data, positions=valid_positions, showmeans=False, showmedians=False, showextrema=False)

        # Violin rengini ayarla (örneğin açık mavi)

        for pc in parts['bodies']:

            pc.set_facecolor('#D0E4F5')

            pc.set_edgecolor('grey')

            pc.set_alpha(0.7)



    # Box plot'u çiz

    bp = ax.boxplot(

        [d for d in data if len(d)>0], # Verisi olanları al

        positions=[i for i,d in enumerate(data,1) if len(d)>0], # Verisi olan pozisyonları al

        widths=0.2,

        showfliers=False, # Aykırı değerleri gösterme

        patch_artist=True, # Kutuları doldurmak için

        boxprops=dict(facecolor='white', alpha=0.9, zorder=2), # Kutu rengi

        medianprops=dict(color='darkorange', linewidth=2, zorder=3), # Medyan çizgisi

        whiskerprops=dict(zorder=4), # Bıyık çizgileri

        capprops=dict(zorder=4), # Bıyık uçları

    )



    whisker_fontsize = 6

    whisker_x_offset = 0.12 # Yazının kutudan uzaklığı



    # --- 1d için ---

    data_1d_val = data[0][0] if len(data[0]) > 0 else np.nan

    if not np.isnan(data_1d_val):

         # 1d tek nokta olduğu için kutu yerine sadece noktayı ve değerini göster

         ax.plot(1, data_1d_val, 'o', color='grey', markersize=5, zorder=5)

         ax.text(1 - whisker_x_offset, data_1d_val, f"{data_1d_val:.2f}",

                 ha='right', va='center', fontsize=whisker_fontsize, color='black', zorder=11)



    # --- 10d için ---

    data_10d = data[1]

    if len(data_10d) > 0:

        # Boxplot bıyıklarını hesapla (IQR metodu)

        q1_10d, q3_10d = np.percentile(data_10d, [25, 75]) if len(data_10d) > 1 else (data_10d[0], data_10d[0])

        iqr_10d = q3_10d - q1_10d

        whisk_low_10d = q1_10d - 1.5 * iqr_10d

        whisk_high_10d = q3_10d + 1.5 * iqr_10d

        # Bıyık sınırları içindeki min/max değerleri bul

        non_outliers_low_10d = data_10d[data_10d >= whisk_low_10d]

        whisker_min_10d = np.min(non_outliers_low_10d) if len(non_outliers_low_10d) > 0 else q1_10d

        non_outliers_high_10d = data_10d[data_10d <= whisk_high_10d]

        whisker_max_10d = np.max(non_outliers_high_10d) if len(non_outliers_high_10d) > 0 else q3_10d



        median_10d = np.median(data_10d)

        # Medyan değerini kutunun üzerine yaz

        ax.text(2, median_10d + 0.05, f"{median_10d:.2f}", ha="center", va="bottom", fontsize=8, color="black", fontweight="bold", zorder=11)

        # Bıyık değerlerini yaz

        ax.text(2 - whisker_x_offset, whisker_min_10d, f"{whisker_min_10d:.2f}", ha='right', va='center', fontsize=whisker_fontsize, zorder=11)

        ax.text(2 - whisker_x_offset, whisker_max_10d, f"{whisker_max_10d:.2f}", ha='right', va='center', fontsize=whisker_fontsize, zorder=11)



    # --- 100d için ---

    data_100d = data[2]

    if len(data_100d) > 0:

        q1_100d, q3_100d = np.percentile(data_100d, [25, 75]) if len(data_100d) > 1 else (data_100d[0], data_100d[0])

        iqr_100d = q3_100d - q1_100d

        whisk_low_100d = q1_100d - 1.5 * iqr_100d

        whisk_high_100d = q3_100d + 1.5 * iqr_100d

        non_outliers_low_100d = data_100d[data_100d >= whisk_low_100d]

        whisker_min_100d = np.min(non_outliers_low_100d) if len(non_outliers_low_100d) > 0 else q1_100d

        non_outliers_high_100d = data_100d[data_100d <= whisk_high_100d]

        whisker_max_100d = np.max(non_outliers_high_100d) if len(non_outliers_high_100d) > 0 else q3_100d



        median_100d = np.median(data_100d)

        ax.text(3, median_100d + 0.05, f"{median_100d:.2f}", ha="center", va="bottom", fontsize=8, color="black", fontweight="bold", zorder=11)

        ax.text(3 - whisker_x_offset, whisker_min_100d, f"{whisker_min_100d:.2f}", ha='right', va='center', fontsize=whisker_fontsize, zorder=11)

        ax.text(3 - whisker_x_offset, whisker_max_100d, f"{whisker_max_100d:.2f}", ha='right', va='center', fontsize=whisker_fontsize, zorder=11)



    ax.set_ylim(11, 14) # Y ekseni limitleri

    ax.set_xticks([1,2,3]); ax.set_xticklabels(labels) # X ekseni etiketleri

    ax.set_ylabel("AU") # Y ekseni başlığı



    # Her grup için n sayısını yaz

    text_y_position = 13.9 # n yazısının yüksekliği

    for i, w in enumerate([1,10,100], start=1):

        n = df_all[df_all["window"]==w].shape[0]

        if n > 0:

            ax.text(i, text_y_position, f"n={n}", ha="center", va="top", fontsize=9)



    ax.grid(axis='y', linestyle='--', alpha=0.7) # Yatay grid çizgileri

    plt.tight_layout() # Düzeni sıkıştır

    savefig(fig, "au_distribution_by_window_final_no_title")

    plt.close(fig)





def plot_au_stripplot(df_all: pd.DataFrame, ylim=(11, 14.5), jitter=0.10, alpha=0.6):

    if df_all.empty: return # Veri yoksa çizme

    fig = plt.figure(figsize=(7.2, 4.0))

    ax = plt.gca()



    x_positions = {1:1, 10:2, 100:3} # Grupların x pozisyonları

    colors = {1:"#6baed6", 10:"#fdae6b", 100:"#74c476"} # Grupların renkleri



    current_ylim = ylim # Y ekseni limitleri



    for w in [1,10,100]:

        vals = df_all[df_all["window"]==w]["au"].values

        if len(vals) == 0:

            continue

        # Jitter ekle (noktaların x ekseninde hafifçe dağılması)

        xs = np.random.normal(loc=x_positions[w], scale=jitter, size=len(vals))

        ax.scatter(xs, vals, s=20, alpha=alpha, edgecolors='none', label=f"{w}d", c=colors[w], zorder=1)



        # n sayısını yaz

        ax.text(x_positions[w], current_ylim[1]-0.05, f"n={len(vals)}", ha="center", va="top", fontsize=9)



    # Gruplar arasına dikey çizgiler ekle

    for x in [1.5, 2.5]:

        ax.axvline(x, color="grey", linewidth=0.8, alpha=0.8)



    ax.set_xlim(0.5, 3.5) # X ekseni limitleri

    ax.set_ylim(*current_ylim) # Y ekseni limitleri

    ax.set_xticks([1,2,3]); ax.set_xticklabels(["1d","10d","100d"]) # X ekseni etiketleri

    ax.set_ylabel("AU") # Y ekseni başlığı



    # Ana Y ekseni grid çizgileri (0.5 aralıklarla)

    major_ticks = np.arange(current_ylim[0], current_ylim[1] + 0.1, 0.5)

    ax.set_yticks(major_ticks)

    ax.grid(which='major', axis='y', linestyle='--', alpha=0.5, color='darkgrey')



    # İkincil Y ekseni grid çizgileri (0.1 aralıklarla)

    ax.yaxis.set_minor_locator(MultipleLocator(0.1))



    # İkincil grid çizgilerini belirli aralıkta çiz (11.5 - 14.0 arası)

    minor_locator = ax.yaxis.get_minor_locator()

    minor_tick_locs = minor_locator.tick_values(current_ylim[0], current_ylim[1])



    for y_val in minor_tick_locs:

        # Sadece belirlenen aralıktaki ve ana tick olmayan çizgileri çiz

        if 11.5 - 1e-9 <= y_val <= 14.0 + 1e-9:

             if not np.isclose(y_val % 0.5, 0, atol=1e-9) and not np.isclose(y_val % 0.5, 0.5, atol=1e-9):

                 ax.axhline(y_val, color='lightgrey', linestyle=':', alpha=0.7, linewidth=0.6, zorder=0)



    # Tick'leri içeri al ve sağ tarafta da göster

    ax.tick_params(axis='y', which='both', direction='in', right=True)



    plt.tight_layout()

    savefig(fig, "au_stripplot_by_window_11_14.5_minor_grid_11.5_14")

    plt.close(fig)



def plot_au_vs_repeat(df_win: pd.DataFrame, df_rep_win: pd.DataFrame):

    if df_win.empty or df_rep_win.empty: return # Veri yoksa çizme



    # Her cisim için medyan AU ve toplam tespit sayısını hesapla

    med = df_win.groupby("object_id")["au"].median().reset_index(name="median_au")

    size = df_win.groupby("object_id")["day"].size().reset_index(name="det_count")

    rep = df_rep_win[["object_id","repeat_count"]]



    # Verileri birleştir

    merged = med.merge(rep, on="object_id", how="left").merge(size, on="object_id", how="left")

    merged["repeat_count"] = merged["repeat_count"].fillna(0) # NaN repeat'leri 0 yap



    fig = plt.figure(figsize=(8, 3.2))

    # Scatter plot: x=median AU, y=repeat count, boyut=tespit sayısı

    plt.scatter(merged["median_au"], merged["repeat_count"],

                s=20 + 5*merged["det_count"], alpha=0.75) # Boyut ayarı

    plt.xscale("log"); plt.xlim(AU_MIN, AU_MAX) # X eksenini logaritmik yap

    plt.xlabel("Median AU (log)"); plt.ylabel("Repeat count")

    w = int(df_win["window"].iloc[0])

    plt.title(f"AU vs Repeat — Window {w}d")



    # En çok tekrar eden birkaç cismi etiketle

    n_labels = 5 if w > 1 else 1 # 1d için sadece 1 etiket

    top_n_labels = merged.sort_values("repeat_count", ascending=False).head(n_labels)



    for _, r in top_n_labels.iterrows():

        plt.text(r["median_au"], r["repeat_count"], r["object_id"],

                 fontsize=7, ha="left", va="bottom")



    plt.tight_layout()

    savefig(fig, f"au_vs_repeat_{w}d")

    plt.close(fig)





# --- plot_presence_heatmap_10d_with_1d_inset fonksiyonu (SON HALİ) ---

def plot_presence_heatmap_10d_with_1d_inset(df_10d: pd.DataFrame, df_10d_rep: pd.DataFrame, df_1d: pd.DataFrame, df_1d_rep: pd.DataFrame):

    """

    10d verisi için ana matrisi ve 1d verisi için özel inset'i çizer (SON HAL).

    """

    def get_shade(color_tuple, total_shades, rank): # Renk tonu helper

        if total_shades <= 1: return color_tuple

        r, g, b, a = to_rgba(color_tuple); h, s, v = colorsys.rgb_to_hsv(r, g, b)

        min_v_scale, max_v_scale = 0.5, 1.0

        v_scale = max_v_scale - (max_v_scale - min_v_scale) * (rank / (total_shades - 1)) if total_shades > 1 else max_v_scale

        new_v = np.clip(v * v_scale, 0, 1.0); r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, new_v)

        return (r_new, g_new, b_new, a)



    # Renk haritaları

    rep_sorted_10d = df_10d_rep.sort_values("repeat_count", ascending=False); objects_10d = list(rep_sorted_10d["object_id"])

    obj_to_idx_10d = {o:i for i,o in enumerate(objects_10d)}; n_objects_10d = len(objects_10d)

    object_1d_name = df_1d_rep["object_id"].iloc[0] if not df_1d_rep.empty else "None"

    base_cmap = plt.get_cmap("Spectral", n_objects_10d); obj_to_base_color = {obj: base_cmap(i) for i, obj in enumerate(objects_10d)}

    pip_color = plt.get_cmap("hot")(0.5)

    if object_1d_name not in obj_to_base_color and object_1d_name != "None": obj_to_base_color[object_1d_name] = pip_color



    # 10d Veri Hazırlığı

    if df_10d_rep.empty: print("10d_rep verisi bulunamadı..."); return

    all_target_dates_str = ["1965-03-15", "1973-11-29", "1981-09-01", "1988-06-23", "1994-01-10", "1999-08-14", "2005-02-28", "2010-12-05", "2016-04-19", "2022-07-22"]

    days_sorted_10d = np.array(all_target_dates_str, dtype='datetime64[ns]'); day_to_idx_10d = {d:i for i,d in enumerate(days_sorted_10d)}; n_days_10d = len(days_sorted_10d)

    df_10d_sorted = df_10d.sort_values(["object_id", "day"]); df_10d_sorted["det_rank"] = df_10d_sorted.groupby("object_id").cumcount()

    det_counts = df_10d_sorted.groupby("object_id").size().to_dict()



    # Ana Grafik Çizimi

    fig, ax = plt.subplots(figsize=(8.5, 5)); ax.set_facecolor('#ffffff')

    ax.set_yticks(range(n_objects_10d)); ax.set_yticklabels(objects_10d, fontsize=7)

    tick_idx_10d = np.arange(n_days_10d); ax.set_xticks(tick_idx_10d)

    date_labels = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in days_sorted_10d]; ax.set_xticklabels(date_labels, rotation=90, fontsize=8)

    plot_padding_y = 0.15; ax.set_xlim(-0.5, (n_days_10d - 0.5)); ax.set_ylim(-0.5 - plot_padding_y, (n_objects_10d - 0.5) + plot_padding_y)

    ax.set_xlabel("Date"); ax.set_ylabel("Object Name"); ax.set_title("Presence Matrix 10d")

    ax.set_xticks(np.arange(-.5, n_days_10d - 0.5, 1), minor=True); ax.set_yticks(np.arange(-.5, n_objects_10d - 0.5, 1), minor=True)

    ax.grid(which='minor', color='#d9d9d9', linestyle='-', linewidth=1.5, zorder=10); ax.grid(which='major', axis='both', visible=False); ax.tick_params(which='minor', bottom=False, left=False)

    for spine in ax.spines.values(): spine.set_zorder(20)

    rect_height = 0.9; rect_width = 0.8; alpha_val = 0.85; pad_y = (1 - rect_height) / 2.0; pad_x = (1 - rect_width) / 2.0

    for _, row in df_10d_sorted.iterrows():

        oid = row['object_id']; day = row['day']

        if oid in obj_to_idx_10d and day in day_to_idx_10d:

            i = obj_to_idx_10d[oid]; j = day_to_idx_10d[day]; base_color = obj_to_base_color[oid]

            total_dets = det_counts.get(oid, 1); rank = row["det_rank"]; final_color = get_shade(base_color, total_dets, rank)

            x_coord = (j - 0.5) + pad_x; y_coord = (i - 0.5) + pad_y

            rect = plt.Rectangle((x_coord, y_coord), rect_width, rect_height, facecolor=final_color, alpha=alpha_val, edgecolor=None, linewidth=0, zorder=5)

            ax.add_patch(rect)



    # 1d Inset Çizimi

    bbox_coords = [-0.3, 9.5, 3.5, 20.5]; ax_bbox = ax.get_position(); trans = ax.transData + fig.transFigure.inverted()

    bbox_fig_coords = trans.transform_bbox(Bbox.from_extents(bbox_coords)); ax_inset = fig.add_axes(bbox_fig_coords)

    if not df_1d.empty and not df_1d_rep.empty:

        object_1d = df_1d_rep["object_id"].iloc[0]; day_1d_str = pd.to_datetime(df_1d["day"].iloc[0]).strftime('%Y-%m-%d')

        ax_inset.set_facecolor('#ffffff'); shift_x = 0.2

        ax_inset.text(1.0 + shift_x, 19.8, "Presence Matrix 1d", fontsize=8, ha='center', va='top', zorder=25)

        ax_inset.set_xlim(bbox_coords[0], bbox_coords[2]); ax_inset.set_ylim(bbox_coords[1], bbox_coords[3])

        x_ticks_minor_inset = np.arange(np.ceil(bbox_coords[0]-0.5)+0.5, bbox_coords[2] + 1e-9, 1)

        y_ticks_minor_inset = np.arange(bbox_coords[1], bbox_coords[3] + 1e-9, 1)

        ax_inset.set_xticks(x_ticks_minor_inset, minor=True); ax_inset.set_yticks(y_ticks_minor_inset, minor=True)

        ax_inset.grid(which='minor', color='#d9d9d9', linestyle='-', linewidth=1.5, zorder=10)

        ax_inset.grid(which='major', axis='both', visible=False); ax_inset.tick_params(which='both', bottom=False, left=False, top=False, right=False, labelbottom=False, labelleft=False, labeltop=False, labelright=False)

        ax_inset.set_xticks([]); ax_inset.set_yticks([])

        center_x = 1.5 + shift_x; center_y = 14.5

        label_y_pos = center_y; label_y_x_pos = 0.0 + shift_x

        ax_inset.text(label_y_x_pos, label_y_pos, object_1d, ha='center', va='center', rotation=90, fontsize=6, zorder=15)

        label_x_pos = center_x; label_x_y_pos = 10.5

        ax_inset.text(label_x_pos, label_x_y_pos, day_1d_str, ha='center', va='center', fontsize=6, zorder=15)

        inset_rect_width = 0.95; inset_rect_height = 0.9; x_coord_inset = center_x - inset_rect_width / 2; y_coord_inset = center_y - inset_rect_height / 2

        rect_inset = plt.Rectangle((x_coord_inset, y_coord_inset), inset_rect_width, inset_rect_height, facecolor=pip_color, alpha=alpha_val, edgecolor=None, linewidth=0, zorder=12)

        ax_inset.add_patch(rect_inset)

        tick_color = 'black'; tick_lw = 1.0; tick_linestyle = '--'; tick_start_x = label_y_x_pos + 0.1; tick_start_y = label_x_y_pos + 0.3

        ax_inset.plot([tick_start_x, center_x], [center_y, center_y], color=tick_color, lw=tick_lw, linestyle=tick_linestyle, zorder=11)

        ax_inset.plot([center_x, center_x], [tick_start_y, center_y], color=tick_color, lw=tick_lw, linestyle=tick_linestyle, zorder=11)

        for spine in ax_inset.spines.values(): spine.set_edgecolor('black'); spine.set_linewidth(1.5); spine.set_zorder(20)

    else: # 1d verisi boşsa

        ax_inset.set_facecolor('none'); ax_inset.set_yticks([]); ax_inset.set_xticks([])

        ax_inset.set_title("1d PIP (No data)", fontsize=7)

        for spine in ax_inset.spines.values(): spine.set_edgecolor('black'); spine.set_linewidth(1.5)

    savefig(fig, "presence_matrix_10d_by_object_with_1d_inset_final")

    plt.close(fig)



# ----------------------------------------------------------------- #

# ----- ESKİ FONKSİYON: 100d PRESENCE MATRIX (KODLANMIŞ EKSENLER) -----

# ----- GÜNCELLENDİ: 4 PANELE (QUADRANT) BÖLME -----

# ----------------------------------------------------------------- #

def plot_presence_matrix_100d(df_100d: pd.DataFrame, df_100d_rep: pd.DataFrame, target_100_days_str: list):

    """

    100 günlük veriyi, kodlanmış eksenlerle (O1.., D1..) görselleştirir.

    İSTEĞİN ÜZERİNE GÜNCELLENDİ:

    Okunabilirlik için grafik 4 panele (2x2 quadrant) bölünür.

    - 131 Cisim -> 66 (A/C) + 65 (B/D)

    - 100 Gün    -> 50 (A/B) + 50 (C/D)

    Sonuç olarak 2 sayfa (Sayfa 1: A+B, Sayfa 2: C+D) üretilir.

    Anahtar listelerini konsola ve dosyalara yazdırır.

    """

    if df_100d.empty or df_100d_rep.empty:

        print("100d verisi bulunamadı, grafik çizilemiyor.")

        return



    print("\n--- Generating 100d Presence Matrix (4-Panel Quadrant) ---")



    # === CİSİM SIRALAMA VE KODLAMA (Alfabetik) ===

    valid_objects = df_100d_rep['object_id'].dropna().unique()

    all_objects = sorted(list(valid_objects))

    n_objects_100d = len(all_objects)

    if n_objects_100d == 0: print("Uyarı: 100d_rep verisinde geçerli cisim bulunamadı."); return

    # Kodlama ve anahtar listeleri (Orijinaliyle aynı)

    object_to_code = {obj: f"O{i+1}" for i, obj in enumerate(all_objects)}

    print("\nObject Codes Key (Alphabetical Order):"); object_key_lines = [f"O{i+1}: {obj}" for i, obj in enumerate(all_objects)]; print("\n".join(object_key_lines))

    obj_key_path = OUTDIR / "object_key_100d.txt"

    with open(obj_key_path, "w", encoding='utf-8') as f: f.write("\n".join(object_key_lines))

    print(f"Object key saved to: {obj_key_path}")

    obj_cmap_100d = plt.get_cmap("Spectral", n_objects_100d); obj_to_base_color_100d = {obj: obj_cmap_100d(i) for i, obj in enumerate(all_objects)}

    # Cisim index haritası

    obj_name_to_idx = {name: i for i, name in enumerate(all_objects)}





    # === GÜN SIRALAMA VE KODLAMA (SAĞLANAN LİSTEYE GÖRE, Kronolojik) ===

    target_100_days_dt = pd.to_datetime(target_100_days_str).sort_values()

    all_days = target_100_days_dt.values # Numpy array of datetimes

    n_days_100d = len(all_days)

    if n_days_100d != 100: print(f"Uyarı: Sağlanan gün listesi {n_days_100d} gün içeriyor, 100 değil.")

    # Kodlama ve anahtar listeleri (Orijinaliyle aynı)

    day_to_code = {day: f"D{i+1}" for i, day in enumerate(all_days)}

    print("\nDay Codes Key (Chronological Order):"); day_key_lines = [f"D{i+1}: {pd.to_datetime(day).strftime('%Y-%m-%d')}" for i, day in enumerate(all_days)]; print("\n".join(day_key_lines))

    day_key_path = OUTDIR / "day_key_100d.txt"

    with open(day_key_path, "w", encoding='utf-8') as f: f.write("\n".join(day_key_lines))

    # Gün index haritası

    day_dt_to_idx = {day: i for i, day in enumerate(all_days)} # Datetime objesi ile index map



    # === Veri Hazırlığı (Rank Hesaplama) ===

    df_100d_sorted = df_100d.sort_values(["object_id", "day"])

    df_100d_sorted["det_rank"] = df_100d_sorted.groupby("object_id").cumcount()

    det_counts_100d = df_100d_sorted.groupby("object_id").size().to_dict()



    # === BÖLME NOKTALARI ===

    # Cisimler: 131 -> 66 + 65

    split_obj_idx = 66

    # Günler: 100 -> 50 + 50

    split_day_idx = 50



    # Panel A/C (O1-O66)

    objects_AC = all_objects[0:split_obj_idx]

    obj_codes_AC = [object_to_code[o] for o in objects_AC]

    n_obj_AC = len(objects_AC)

    # Panel B/D (O67-O131)

    objects_BD = all_objects[split_obj_idx:]

    obj_codes_BD = [object_to_code[o] for o in objects_BD]

    n_obj_BD = len(objects_BD)



    # Panel A/B (D1-D50)

    days_AB = all_days[0:split_day_idx]

    day_codes_AB = [day_to_code[d] for d in days_AB]

    n_day_AB = len(days_AB)

    # Panel C/D (D51-D100)

    days_CD = all_days[split_day_idx:]

    day_codes_CD = [day_to_code[d] for d in days_CD]

    n_day_CD = len(days_CD)





    # === YARDIMCI ÇİZİM FONKSİYONU (Panel Ayarları için) ===

    def setup_panel(ax, obj_codes_list, day_codes_list, n_obj, n_day, title):

        """Belirli bir panel (ax) için eksenleri, etiketleri ve ızgarayı ayarlar."""

        ax.set_facecolor('#ffffff')

        

        # Etiket boyutu artırıldı (4 -> 5)

        tick_labelsize = 5 



        # --- Y Ekseni (Cisimler) ---

        ax.set_yticks(range(n_obj))

        ax.set_yticklabels(obj_codes_list, fontsize=tick_labelsize)

        

        # --- X Ekseni (Günler) ---

        # Sıklık artırıldı (10 -> 5)

        xtick_interval = 5 

        xtick_indices = np.arange(0, n_day, xtick_interval)

        # Etiket listesi

        xtick_labels = [day_codes_list[i] for i in xtick_indices] # Sadece aralıktakileri al

        ax.set_xticks(xtick_indices) # Sadece aralıktakilere tick koy

        ax.set_xticklabels(xtick_labels, fontsize=tick_labelsize, rotation=90)

        

        # --- Eksen Limitleri & Başlıklar ---

        ax.set_xlim(-0.5, n_day - 0.5)

        ax.set_ylim(-0.5, n_obj - 0.5)

        ax.invert_yaxis() # O1 en üstte

        ax.set_xlabel("Day Code")

        ax.set_ylabel("Object Code")

        ax.set_title(title, fontsize=10) # Panel başlığı

        

        # --- Izgara ---

        ax.set_xticks(np.arange(-.5, n_day - 0.5, 1), minor=True)

        ax.set_yticks(np.arange(-.5, n_obj - 0.5, 1), minor=True)

        ax.grid(which='minor', color='#d9d9d9', linestyle='-', linewidth=0.3, zorder=10)

        ax.grid(which='major', axis='both', visible=False)

        ax.tick_params(which='major', length=0) # Major tick'lerin görünmesini engelle

        ax.tick_params(which='minor', length=0)

        for spine in ax.spines.values(): spine.set_zorder(20)



    # === GRAFİK ÇİZİMİ (2 Sayfa, 4 Panel) ===



    # --- Sayfa 1 (Panel A, Panel B) ---

    # A4 Dikey: 8.3 x 11.7 inç

    fig1, (axA, axB) = plt.subplots(2, 1, figsize=(8.3, 11.7), constrained_layout=True)

    fig1.suptitle("Presence Matrix 100d (Days D1-D50)", fontsize=14, y=1.02)

    

    # Panel A: O1-O66, D1-D50

    setup_panel(axA, obj_codes_AC, day_codes_AB, n_obj_AC, n_day_AB, 

                f"Panel A: Objects O1-O{n_obj_AC} (N={n_obj_AC}), Days D1-D{n_day_AB} (N={n_day_AB})")

    # Panel B: O67-O131, D1-D50

    setup_panel(axB, obj_codes_BD, day_codes_AB, n_obj_BD, n_day_AB, 

                f"Panel B: Objects O{n_obj_AC+1}-O{n_objects_100d} (N={n_obj_BD}), Days D1-D{n_day_AB} (N={n_day_AB})")



    # --- Sayfa 2 (Panel C, Panel D) ---

    fig2, (axC, axD) = plt.subplots(2, 1, figsize=(8.3, 11.7), constrained_layout=True)

    fig2.suptitle(f"Presence Matrix 100d (Days D{n_day_AB+1}-D{n_days_100d})", fontsize=14, y=1.02)

    

    # Panel C: O1-O66, D51-D100

    setup_panel(axC, obj_codes_AC, day_codes_CD, n_obj_AC, n_day_CD, 

                f"Panel C: Objects O1-O{n_obj_AC} (N={n_obj_AC}), Days D{n_day_AB+1}-D{n_days_100d} (N={n_day_CD})")

    # Panel D: O67-O131, D51-D100

    setup_panel(axD, obj_codes_BD, day_codes_CD, n_obj_BD, n_day_CD, 

                f"Panel D: Objects O{n_obj_AC+1}-O{n_objects_100d} (N={n_obj_BD}), Days D{n_day_AB+1}-D{n_days_100d} (N={n_day_CD})")





    # --- Renkli Kareler (Tüm paneller için tek döngü) ---

    rect_height_100d = 1.0; rect_width_100d = 1.0; alpha_val_100d = 0.9

    pad_y_100d = 0; pad_x_100d = 0



    # get_shade fonksiyonunu tekrar tanımla (scope için)

    def get_shade_local(color_tuple, total_shades, rank):

        if total_shades <= 1: return color_tuple

        r, g, b, a = to_rgba(color_tuple); h, s, v = colorsys.rgb_to_hsv(r, g, b)

        min_v_scale, max_v_scale = 0.5, 1.0

        v_scale = max_v_scale - (max_v_scale - min_v_scale) * (rank / (total_shades - 1)) if total_shades > 1 else max_v_scale

        new_v = np.clip(v * v_scale, 0, 1.0); r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, new_v)

        return (r_new, g_new, b_new, a)



    # Ana veri döngüsü

    for _, row in df_100d_sorted.iterrows():

        oid = row['object_id']

        day = row['day'] # Bu zaten datetime objesi



        # Sadece anahtarda olan cisimleri ve hedef listedeki günleri işle

        if oid in obj_name_to_idx and day in day_dt_to_idx:

            # Global indexleri al (0-130 ve 0-99)

            i_global = obj_name_to_idx[oid]

            j_global = day_dt_to_idx[day] 



            base_color = obj_to_base_color_100d[oid]

            total_dets = det_counts_100d.get(oid, 1)

            rank = row["det_rank"]

            final_color = get_shade_local(base_color, total_dets, rank)



            target_ax = None

            plot_i, plot_j = -1, -1 # Panel içi lokal indexler



            # Hangi panele çizileceğine karar ver

            if j_global < split_day_idx: # Gün D1-D50 (Sayfa 1)

                plot_j = j_global # X koord 0-49

                if i_global < split_obj_idx: # Cisim O1-O66 (Panel A)

                    target_ax = axA

                    plot_i = i_global # Y koord 0-65

                else: # Cisim O67-O131 (Panel B)

                    target_ax = axB

                    plot_i = i_global - split_obj_idx # Y koord 0-64

            

            else: # Gün D51-D100 (Sayfa 2)

                plot_j = j_global - split_day_idx # X koord 0-49

                if i_global < split_obj_idx: # Cisim O1-O66 (Panel C)

                    target_ax = axC

                    plot_i = i_global # Y koord 0-65

                else: # Cisim O67-O131 (Panel D)

                    target_ax = axD

                    plot_i = i_global - split_obj_idx # Y koord 0-64



            # Eğer geçerli bir panele atandıysa, kareyi çiz

            if target_ax is not None:

                x_coord = (plot_j - 0.5) + pad_x_100d

                y_coord = (plot_i - 0.5) + pad_y_100d



                rect = plt.Rectangle(

                    (x_coord, y_coord), rect_width_100d, rect_height_100d,

                    facecolor=final_color, alpha=alpha_val_100d,

                    edgecolor='none', linewidth=0, zorder=5)

                target_ax.add_patch(rect)



    # --- Kaydetme ---

    savefig(fig1, "presence_matrix_100d_coded_Page1_AB")

    savefig(fig2, "presence_matrix_100d_coded_Page2_CD")

    plt.close(fig1)

    plt.close(fig2)

    print("--- 100d Presence Matrix (4 panels on 2 pages) generated ---")





# ----------------------------------------------------------------- #

# ----- YENİ MASTER FONKSİYON: 111 GÜN x 149 CİSİM -----

# ----- GÜNCELLENDİ: Hatalı Panel Atama Mantığı Düzeltildi -----

# ----------------------------------------------------------------- #

def plot_presence_matrix_111d_149obj(df_all_matches: pd.DataFrame, master_object_list: list, master_day_list: np.ndarray):

    """

    Tüm 1d, 10d, 100d verilerini (149 benzersiz cisim) alır ve

    birleşik 111 günlük hedef listesine göre (D1-D111) görselleştirir.

    

    Grafik, 4 panele (2x2) TEK BİR SAYFADA birleştirilmiştir.

    Düzen:

     - Sol Üst (A): O1-74 vs D1-56

     - Sağ Üst (C): O1-74 vs D57-111

     - Sol Alt (B): O75-149 vs D1-56

     - Sağ Alt (D): O75-149 vs D57-111

     

    Renkler AU DEĞERİNE göre atanır.

    Sağ tarafa global bir renk çubuğu (colorbar) eklenmiştir.

    

    DÜZELTME: Tüm 189 tespitin doğru panellere yerleştirilmesi sağlandı.

    

    Anahtar listelerini konsola ve dosyalara yazdırır.

    """

    if df_all_matches.empty or not master_object_list or master_day_list.size == 0:

        print("Master Matrix için veri (df_all_matches, cisim veya gün listesi) bulunamadı, grafik çizilemiyor.")

        return



    print("\n--- Generating MASTER Presence Matrix (111d x 149obj) (Single Page AC/BD, AU Color, FIXED) ---")



    # === CİSİM SIRALAMA VE KODLAMA (Alfabetik, 149 Cisim) ===

    all_objects = master_object_list # Bu zaten sıralı 149'luk liste

    n_objects_total = len(all_objects)

    if n_objects_total != 149:

        print(f"Uyarı: Sağlanan cisim listesi {n_objects_total} cisim içeriyor, 149 değil.")

    

    object_to_code = {obj: f"O{i+1}" for i, obj in enumerate(all_objects)}

    all_object_codes = [object_to_code[o] for o in all_objects] # Kod listesi

    # ... (anahtar dosyası yazdırma kısmı aynı) ...

    obj_key_path = OUTDIR / "object_key_149_master.txt"

    with open(obj_key_path, "w", encoding='utf-8') as f: f.write("\n".join([f"O{i+1}: {obj}" for i, obj in enumerate(all_objects)]))

    print(f"Master Object key saved to: {obj_key_path}")



    obj_name_to_idx = {name: i for i, name in enumerate(all_objects)} # Cisim adı -> Global Index (0-148)



    

    # === GÜN SIRALAMA VE KODLAMA (Kronolojik, 111 Gün) ===

    all_days = master_day_list # Bu zaten sıralı 111'lik datetime dizisi

    n_days_total = len(all_days)

    if n_days_total != 111:

        print(f"Uyarı: Sağlanan gün listesi {n_days_total} gün içeriyor, 111 değil.")



    day_to_code = {day: f"D{i+1}" for i, day in enumerate(all_days)}

    all_day_codes = [day_to_code[d] for d in all_days] # Kod listesi

    # ... (anahtar dosyası yazdırma kısmı aynı) ...

    day_key_path = OUTDIR / "day_key_111_master.txt"

    with open(day_key_path, "w", encoding='utf-8') as f: f.write("\n".join([f"D{i+1}: {pd.to_datetime(day).strftime('%Y-%m-%d')}" for i, day in enumerate(all_days)]))

    print(f"Master Day key saved to: {day_key_path}")

    

    day_dt_to_idx = {day: i for i, day in enumerate(all_days)} # Datetime -> Global Index (0-110)



    # === Veri Hazırlığı ===

    df_master_sorted = df_all_matches.sort_values(["object_id", "day"])



    # === RENK MANTIĞI (Global AU Skalası) ===

    min_au = df_all_matches['au'].min()

    max_au = df_all_matches['au'].max()

    print(f"  -> Global AU aralığı: {min_au:.2f} - {max_au:.2f}")

    

    cmap = plt.get_cmap('turbo') 

    norm = mcolors.Normalize(vmin=min_au, vmax=max_au)

    scalar_mappable = cm.ScalarMappable(norm=norm, cmap=cmap)



    # === GÖRSEL BÖLME NOKTALARI (YAKLAŞIK ORTA) ===

    i_split_idx = 74 # İlk 74 cisim (O1-O74) üstte, kalan 75 cisim (O75-O149) altta

    j_split_idx = 56 # İlk 56 gün (D1-D56) solda, kalan 55 gün (D57-D111) sağda



    # Panel Listeleri (Görsel Bölmeye Göre)

    obj_codes_AC = all_object_codes[0:i_split_idx]    # O1-O74

    obj_codes_BD = all_object_codes[i_split_idx:]    # O75-O149

    day_codes_AB = all_day_codes[0:j_split_idx]      # D1-D56

    day_codes_CD = all_day_codes[j_split_idx:]      # D57-D111



    # Panel Boyutları (Görsel Bölmeye Göre)

    n_obj_AC = len(obj_codes_AC) # 74

    n_obj_BD = len(obj_codes_BD) # 75

    n_day_AB = len(day_codes_AB) # 56

    n_day_CD = len(day_codes_CD) # 55





    # === YARDIMCI ÇİZİM FONKSİYONU (Panel Ayarları için - Aynı kaldı) ===

    def setup_panel(ax, obj_codes_list, day_codes_list, n_obj, n_day, title):

        """Belirli bir panel (ax) için eksenleri, etiketleri ve ızgarayı ayarlar."""

        ax.set_facecolor('#ffffff')

        tick_labelsize = 5 

        # Y Ekseni

        ax.set_yticks(range(n_obj))

        ax.set_yticklabels(obj_codes_list, fontsize=tick_labelsize)

        # X Ekseni

        xtick_interval = 5 

        xtick_indices = np.arange(0, n_day, xtick_interval)

        xtick_labels = [day_codes_list[i] for i in xtick_indices if i < n_day]

        ax.set_xticks(xtick_indices)

        ax.set_xticklabels(xtick_labels, fontsize=tick_labelsize, rotation=90)

        # Limitler & Başlıklar

        ax.set_xlim(-0.5, n_day - 0.5)

        ax.set_ylim(-0.5, n_obj - 0.5)

        ax.invert_yaxis() 

        ax.set_xlabel("Day Code")

        ax.set_ylabel("Object Code")

        ax.set_title(title, fontsize=10) 

        # Izgara

        ax.set_xticks(np.arange(-.5, n_day - 0.5, 1), minor=True)

        ax.set_yticks(np.arange(-.5, n_obj - 0.5, 1), minor=True)

        ax.grid(which='minor', color='#d9d9d9', linestyle='-', linewidth=0.3, zorder=10)

        ax.grid(which='major', axis='both', visible=False)

        ax.tick_params(which='major', length=0)

        ax.tick_params(which='minor', length=0)

        for spine in ax.spines.values(): spine.set_zorder(20)



    # === GRAFİK ÇİZİMİ (TEK Sayfa, 2x2 Panel, Görsel Bölmeyle) ===

    fig = plt.figure(figsize=(18, 11.7)) 

    gs = fig.add_gridspec(2, 2, left=0.05, right=0.90, bottom=0.05, top=0.92, wspace=0.1, hspace=0.15)

    

    fig.suptitle(f"Presence Matrix (Master 111d x 149obj) - Color by AU [{min_au:.2f} - {max_au:.2f}]", fontsize=16, y=0.98)



    axA = fig.add_subplot(gs[0, 0]) # Sol Üst

    axC = fig.add_subplot(gs[0, 1]) # Sağ Üst

    axB = fig.add_subplot(gs[1, 0]) # Sol Alt

    axD = fig.add_subplot(gs[1, 1]) # Sağ Alt



    # Panel A: O1-O74 vs D1-D56 (Sol Üst)

    setup_panel(axA, obj_codes_AC, day_codes_AB, n_obj_AC, n_day_AB, 

                  f"Panel A: Objects O1-O{i_split_idx} (N={n_obj_AC}), Days D1-D{j_split_idx} (N={n_day_AB})")

    

    # Panel C: O1-O74 vs D57-D111 (Sağ Üst)

    setup_panel(axC, obj_codes_AC, day_codes_CD, n_obj_AC, n_day_CD, 

                  f"Panel C: Objects O1-O{i_split_idx} (N={n_obj_AC}), Days D{j_split_idx+1}-D{n_days_total} (N={n_day_CD})")



    # Panel B: O75-O149 vs D1-D56 (Sol Alt)

    setup_panel(axB, obj_codes_BD, day_codes_AB, n_obj_BD, n_day_AB, 

                  f"Panel B: Objects O{i_split_idx+1}-O{n_objects_total} (N={n_obj_BD}), Days D1-D{j_split_idx} (N={n_day_AB})")

    

    # Panel D: O75-O149 vs D57-D111 (Sağ Alt)

    setup_panel(axD, obj_codes_BD, day_codes_CD, n_obj_BD, n_day_CD, 

                  f"Panel D: Objects O{i_split_idx+1}-O{n_objects_total} (N={n_obj_BD}), Days D{j_split_idx+1}-D{n_days_total} (N={n_day_CD})")

    



    # --- Renkli Kareler (DÜZELTİLMİŞ YERLEŞTİRME MANTIĞI) ---

    rect_height_master = 1.0; rect_width_master = 1.0; alpha_val_master = 0.9

    pad_y_master = 0; pad_x_master = 0



    # Ana veri döngüsü (189 tespit için)

    for _, row in df_master_sorted.iterrows():

        oid = row['object_id']

        day = row['day'] 

        au_val = row['au'] 



        if oid in obj_name_to_idx and day in day_dt_to_idx:

            i_global = obj_name_to_idx[oid] # 0-148

            j_global = day_dt_to_idx[day]  # 0-110



            final_color = scalar_mappable.to_rgba(au_val)



            target_ax = None

            plot_i, plot_j = -1, -1 # Panel içi lokal indexler



            # DÜZELTİLMİŞ Panel Belirleme ve Lokal Koordinat Hesaplama

            if i_global < i_split_idx: # Üst sıra (A veya C)

                plot_i = i_global # Lokal Y, global Y ile aynı (0-73)

                if j_global < j_split_idx: # Sol sütun (A)

                    target_ax = axA

                    plot_j = j_global # Lokal X, global X ile aynı (0-55)

                else: # Sağ sütun (C)

                    target_ax = axC

                    plot_j = j_global - j_split_idx # Lokal X (0-54)

            else: # Alt sıra (B veya D)

                plot_i = i_global - i_split_idx # Lokal Y (0-74)

                if j_global < j_split_idx: # Sol sütun (B)

                    target_ax = axB

                    plot_j = j_global # Lokal X (0-55)

                else: # Sağ sütun (D)

                    target_ax = axD

                    plot_j = j_global - j_split_idx # Lokal X (0-54)



            # Kareyi çiz (target_ax None olmamalı)

            if target_ax is not None:

                x_coord = (plot_j - 0.5) + pad_x_master

                y_coord = (plot_i - 0.5) + pad_y_master



                rect = plt.Rectangle(

                    (x_coord, y_coord), rect_height_master, rect_width_master,

                    facecolor=final_color, alpha=alpha_val_master,

                    edgecolor='none', linewidth=0, zorder=5)

                target_ax.add_patch(rect)



    # --- GLOBAL RENK ÇUBUĞU EKLEME (Aynı kaldı) ---

    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) 

    cbar = fig.colorbar(scalar_mappable, cax=cbar_ax)

    cbar.set_label('AU Values', rotation=270, labelpad=20, fontsize=12)

    

    # --- Kaydetme ---

    savefig(fig, "presence_matrix_MASTER_SinglePage_AU_Color_FIXED")

    plt.close(fig)

    print("--- MASTER Presence Matrix (4 panels on 1 page, AU Color, FIXED) generated ---")

    



# Gerekli yeni kütüphaneler (script'in en başına ekleyebilirsiniz)

from matplotlib.lines import Line2D

from matplotlib.patches import Patch

# ---

import colorsys

from matplotlib.colors import to_rgba

from scipy.stats import spearmanr # <--- BU SATIRI EKLE

# plot_presence_matrix için eklendi

from mpl_toolkits.axes_grid1.inset_locator import inset_axes







# ----------------------------------------------------------------- #

# ----- GÜNCELLENMİŞ FONKSİYON: J) AU vs ZAMAN (OUTLIER & KORELASYONLU) -----

# ----------------------------------------------------------------- #

def plot_au_over_time_scatter(df_all_matches: pd.DataFrame, master_object_list: list):

    """

    Tüm tespitleri (189 nokta) zamana göre bir dağılım grafiğinde çizer.

    GÜNCELLENDİ (Bilimsel Versiyon):

    - 2 Standart Sapma (2-sigma) bandını gri bölge olarak çizer.

    - 2-sigma dışında kalan "Outlier"ları 'X' ile işaretler.

    - Outlier'ları O-kodları (O1, O2...) ile etiketler.

    - Lejantı buna göre günceller.

    - GÜNCELLENDİ: Spearman Korelasyonunu (rho, p) hesaplar ve grafiğe basar.

    """

    if df_all_matches.empty:

        print("AU vs Time Scatter için veri bulunamadı, grafik çizilemiyor.")

        return

    if not master_object_list:

        print("AU vs Time Scatter için Ana Cisim Listesi (master_object_list) bulunamadı, etiketleme yapılamıyor.")

        return



    print("\n--- Generating AU vs Time Scatter Plot (J) with Outlier Analysis & Correlation ---")



    # --- 1. Adım: Veri Hazırlığı ve İstatistiksel Hesaplamalar ---

    

    # Trend çizgisi için veriyi tarihe göre sırala

    df_plot = df_all_matches.sort_values("day").copy()

    

    # 30 noktalık merkezli hareketli ortalama (Trend)

    df_plot['au_rolling_mean'] = df_plot['au'].rolling(window=30, min_periods=1, center=True).mean()



    # "Artık" (Residual) hesaplaması: Noktanın trende olan dikey uzaklığı

    df_plot['residual'] = df_plot['au'] - df_plot['au_rolling_mean']

    

    # Artıkların Standart Sapması (sigma)

    residual_std = df_plot['residual'].std()

    threshold = 2.0 * residual_std # 2-sigma eşik değeri

    

    print(f"  -> Trend Artıkları (Residuals) Standart Sapması ($\sigma$): {residual_std:.4f} AU")

    print(f"  -> Outlier Eşik Değeri (2$\sigma$): ±{threshold:.4f} AU")



    # Outlier'ları belirle

    df_plot['is_outlier'] = df_plot['residual'].abs() > threshold

    total_outliers = df_plot['is_outlier'].sum() # Toplam outlier sayısını al



    # --- 1.1: Spearman Korelasyonunu Hesapla (Zaman vs AU) ---

    # Zamanı sayısal bir değere (ordinal) çevir

    df_plot['time_ordinal'] = df_plot['day'].map(pd.Timestamp.toordinal)

    rho, pval = spearmanr(df_plot['time_ordinal'], df_plot['au'])

    

    print("\n  --- Spearman Korelasyon (Zaman vs. AU) ---")

    print(f"  Spearman's Rho ($\rho$): {rho:.4f}")

    print(f"  p-değeri (p): {pval}")

    print("  -------------------------------------------")



    # --- 2. Adım: Cisim Kodlarını (O-Kod) Haritalama ---

    # Master Plot (I) ile AYNI alfabetik kodlamayı kullan

    object_to_code_map = {obj: f"O{i+1}" for i, obj in enumerate(master_object_list)}

    df_plot['obj_code'] = df_plot['object_id'].map(object_to_code_map).fillna('N/A')



    # --- 3. Adım: Grafik Çizimi ---

    

    # --- Renk Ayarları (Tüm veri setine göre) ---

    min_au = df_plot['au'].min()

    max_au = df_plot['au'].max()

    cmap = plt.get_cmap('turbo') 

    norm = mcolors.Normalize(vmin=min_au, vmax=max_au)

    

    # --- Grafik Ayarları ---

    fig, ax = plt.subplots(figsize=(15, 7)) 



    # --- 3.1: ±2-Sigma Bandını Çiz (Soluk Gri Alan) ---

    upper_band = df_plot['au_rolling_mean'] + threshold

    lower_band = df_plot['au_rolling_mean'] - threshold

    ax.fill_between(

        df_plot['day'], 

        lower_band, 

        upper_band, 

        color='grey', 

        alpha=0.2,  # Yarı saydam

        zorder=1,   # En altta

        label='Normal Range (±2\sigma)' # Lejant için (daha sonra manuel eklenecek)

    )



    # --- 3.2: Normal Noktaları Çiz ---

    markers = {1: 'o', 10: 's', 100: '^'}

    sizes = {1: 100, 10: 40, 100: 40} 

    labels = {1: '1d Window', 10: '10d Window', 100: '100d Window'}

    

    # Lejant için handle'ları (işaretçileri) topla

    legend_handles = []



    for w in [100, 10, 1]:

        df_w = df_plot[df_plot['window'] == w]

        if df_w.empty:

            continue

            

        sc = ax.scatter(

            x=df_w['day'],

            y=df_w['au'],

            c=df_w['au'],           

            cmap=cmap,              

            norm=norm,              

            marker=markers[w],      

            s=sizes[w],             

            alpha=0.8,

            edgecolor='black',      

            linewidth=0.5,

            label=f"{labels[w]} (N={len(df_w)})", # Geçici etiket

            zorder=5                

        )

        # Lejant için özel bir handle oluştur (renksiz, sadece şekil)

        handle = Line2D([0], [0], marker=markers[w], color='w', 

                        label=f"{labels[w]} (N={len(df_w)})",

                        markerfacecolor='grey', markeredgecolor='black', markersize=8)

        legend_handles.append(handle)



    # --- 3.3: Trend Çizgisini Çiz ---

    line_trend, = ax.plot( # virgül (,) handle'ı almak için

        df_plot['day'], 

        df_plot['au_rolling_mean'], 

        color='red', 

        linestyle='--', 

        linewidth=2.5, 

        label=f'30-Point Rolling Mean (All Data)',

        zorder=10 

    )

    legend_handles.append(line_trend)



    # --- 3.4: Outlier'ları İşaretle ('X') ve Etiketle (O-Kodu) ---

    df_outliers = df_plot[df_plot['is_outlier'] == True]

    # Konsola gerçek sayıyı bas

    print(f"  -> Toplam {len(df_outliers)} adet 2$\sigma$ Outlier bulundu.") 



    # 'X' işaretleri

    ax.scatter(

        df_outliers['day'], 

        df_outliers['au'], 

        marker='x', 

        s=60,       # 'X'ler belirgin olsun

        c='black', 

        linewidth=1.5,

        zorder=7, 

        label='Outlier (> 2\sigma)' # Lejant için

    )

    

    # O-Kod etiketleri

    for _, row in df_outliers.iterrows():

        ax.text(

            row['day'], 

            row['au'], 

            f" O{int(row['obj_code'][1:])}", # Başına boşluk koy ve 'O' ile etiketle

            fontsize=7, 

            ha='left', 

            va='center_baseline', 

            color='black', 

            fontweight='bold',

            zorder=8

        )



    # --- Renk Çubuğu ---

    cbar = fig.colorbar(sc, ax=ax, orientation='vertical', pad=0.01)

    cbar.set_label('AU Value')



    # --- 3.5: Lejantı (Legend) Manuel Olarak Oluştur ---

    # Gri bant için handle

    band_patch = Patch(facecolor='grey', alpha=0.3, label='Normal Range (±2\sigma)')

    legend_handles.append(band_patch)

    

    # 'X' işareti için handle

    outlier_marker = Line2D([0], [0], marker='x', color='w', label=f'Outlier (> 2\sigma) (N={len(df_outliers)})',

                            markerfacecolor='black', markeredgecolor='black', markersize=7)

    legend_handles.append(outlier_marker)



    # Lejantı çiz ve puntoyu küçült

    ax.legend(

        handles=legend_handles, 

        title='Detection Source', 

        fontsize=9, # İstediğin gibi punto küçültüldü

        loc='lower right' # Lejantı sağ alta al

    )

    

    # --- 3.6: Korelasyon Kutusunu Ekle ---

    p_text = f"p < 0.001" if pval < 0.001 else f"p = {pval:.3f}"

    corr_text = f"Spearman's $\\rho$ = {rho:.2f}\n{p_text}" # rho için \rho kullan

    

    ax.text(0.02, 0.98, corr_text, transform=ax.transAxes, fontsize=9,

            verticalalignment='top', ha='left',

            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='black'))





    # --- Eksen ve Başlık Ayarları ---

    ax.set_xlabel('Date')

    ax.set_ylabel('AU Value')

    ax.set_title(f'All Detections (N={len(df_plot)}) by Date and AU (with 2$\sigma$ Outlier Analysis)', fontsize=14)

    ax.grid(True, linestyle=':', alpha=0.7)

    

    plt.tight_layout()

    # Dosya adını güncelle

    savefig(fig, "au_over_time_scatter_with_trend_outliers_corr") 

    plt.close(fig)

    print("--- AU vs Time Scatter Plot (J) with Outliers and Corr generated ---")







# ----------------------------------------------------------------- #

# ----- YENİ FONKSİYON: K) AU YOĞUNLUK DAĞILIMI (EPOCH'A GÖRE) -----

# ----------------------------------------------------------------- #

def plot_au_density_by_epoch(df_all_matches: pd.DataFrame, split_year: int = 1990):

    """

    Tüm tespitlerin (189 nokta) AU dağılımını (yoğunluk grafiği) çizer.

    

    Hipotezi test etmek için veriyi iki döneme ayırır:

    1. 'split_year' öncesi (Örn: 1960-1990)

    2. 'split_year' sonrası (Örn: 1990-2025)

    

    Bu iki dönemin ve genel verinin yoğunluk eğrilerini (KDE) 

    ve medyanlarını karşılaştırmalı olarak gösterir.

    """

    if df_all_matches.empty:

        print("AU Density by Epoch için veri bulunamadı, grafik çizilemiyor.")

        return



    print(f"\n--- Generating AU Density by Epoch Plot (K) (Split @ {split_year}) ---")



    # --- 1. Adım: Veri Setlerini Ayır ---

    split_date = pd.to_datetime(f'{split_year}-01-01')

    

    all_au = df_all_matches['au']

    pre_epoch_au = df_all_matches[df_all_matches['day'] < split_date]['au']

    post_epoch_au = df_all_matches[df_all_matches['day'] >= split_date]['au']



    if pre_epoch_au.empty or post_epoch_au.empty:

        print(f"  -> Uyarı: {split_year} yılına göre ayırmada veri bulunamadı. Grafik çizilemiyor.")

        return



    # --- 2. Adım: Medyanları Hesapla ---

    med_all = all_au.median()

    med_pre = pre_epoch_au.median()

    med_post = post_epoch_au.median()

    

    print(f"  -> Median (All Data): {med_all:.3f} AU (N={len(all_au)})")

    print(f"  -> Median (Pre-{split_year}): {med_pre:.3f} AU (N={len(pre_epoch_au)})")

    print(f"  -> Median (Post-{split_year}): {med_post:.3f} AU (N={len(post_epoch_au)})")



    # --- 3. Adım: Grafiği Çiz ---

    fig, ax = plt.subplots(figsize=(10, 6))



    # Arka plan histogramı (tüm verinin)

    # Odaklanmak için aralığı belirle (örn: 11.5 - 14.0)

    bins = np.linspace(11.5, 14.0, 50) 

    ax.hist(all_au, bins=bins, density=True, color='grey', alpha=0.25, 

            label='Overall Histogram (All Data)')



    # Yoğunluk Eğrileri (KDE)

    # Not: pandas'ın kendi plot fonksiyonunu kullanmak daha kolay

    all_au.plot.kde(ax=ax, color='black', linestyle='--', linewidth=2, 

                    label=f'Overall KDE (N={len(all_au)})')

    pre_epoch_au.plot.kde(ax=ax, color='#0072B2', linewidth=3, 

                          label=f'Pre-{split_year} KDE (N={len(pre_epoch_au)})')

    post_epoch_au.plot.kde(ax=ax, color='#D55E00', linewidth=3, 

                           label=f'Post-{split_year} KDE (N={len(post_epoch_au)})')



    # Medyan Çizgileri

    ax.axvline(med_pre, color='#0072B2', linestyle=':', linewidth=2, 

               label=f'Median (Pre-{split_year}): {med_pre:.2f} AU')

    ax.axvline(med_post, color='#D55E00', linestyle=':', linewidth=2, 

               label=f'Median (Post-{split_year}): {med_post:.2f} AU')



    # --- 4. Adım: Grafiği Güzelleştir ---

    ax.set_title(f'AU Distribution Density by Epoch (Split @ {split_year})', fontsize=14)

    ax.set_xlabel('AU Value')

    ax.set_ylabel('Density (Kernel Density Estimate)')

    ax.set_xlim(11.5, 14.0) # Ana dağılımın olduğu yere odaklan

    ax.legend(fontsize=9)

    ax.grid(True, linestyle=':', alpha=0.7)

    

    plt.tight_layout()

    savefig(fig, f"au_density_by_epoch_split_{split_year}")

    plt.close(fig)

    print(f"--- AU Density by Epoch Plot (K) generated ---")





# ----------------------------------------------------------------- #

# ----- YENİ FONKSİYONLAR: L & M) REGRESYON ANALİZİ -----

# ----------------------------------------------------------------- #

def plot_regression_analysis_au_vs_time(df_all_matches: pd.DataFrame, degree: int = 3):

    """

    Tüm tespitler (189 nokta) için Polinom Regresyon Analizi yapar.

    

    İki yeni grafik üretir:

    L: Modelin veriye uyumunu (fit) gösteren grafik.

    M: Modelin hatalarını (artıklar/residuals) zamana göre gösteren grafik.

    

    Konsola R-kare (R2) ve model katsayılarını basar.

    

    Grafik J'deki Hareketli Ortalamayı da karşılaştırma için çizer.

    """

    if df_all_matches.empty:

        print("Regression Analysis (L&M) için veri bulunamadı.")

        return



    print(f"\n--- Generating Regression Analysis (L & M) with {degree}-Degree Polynomial ---")



    # --- 1. Adım: Veri Hazırlığı (X ve y) ---

    df_plot = df_all_matches.sort_values("day").copy()

    

    # y: Bağımlı değişken (AU)

    y = df_plot['au'].values

    

    # X: Bağımsız değişken (Zaman)

    # sklearn için zamanı sayısal (ordinal) değere çevir

    df_plot['time_ordinal'] = df_plot['day'].map(pd.Timestamp.toordinal)

    X = df_plot['time_ordinal'].values.reshape(-1, 1)



    # --- 2. Adım: Modeli Oluştur ve Fit Et ---

    # make_pipeline: Önce veriyi Polinoma (X^1, X^2, X^3) çevir, sonra Lineer Regresyon yap

    model = make_pipeline(PolynomialFeatures(degree=degree, include_bias=False), LinearRegression())

    model.fit(X, y)



    # --- 3. Adım: Tahminleri ve Metrikleri Hesapla ---

    

    # Modelin 189 nokta için tahminleri (y_pred)

    y_pred = model.predict(X)

    

    # Modelin Hataları (Artıklar/Residuals)

    residuals = y - y_pred

    

    # R-kare (R-squared) (Modelin Başarı Puanı)

    r2 = r2_score(y, y_pred)

    

    # Model Katsayıları (Denklem)

    poly_features = model.named_steps['polynomialfeatures']

    linear_model = model.named_steps['linearregression']

    

    print("  --- Polynomial Regression Results ---")

    print(f"  R-squared (R2): {r2:.4f}")

    # print(f"  Model Intercept (b0): {linear_model.intercept_:.4f}")

    # print(f"  Model Coefficients (b1, b2, b3...): {linear_model.coef_}")

    print("  -----------------------------------")





    # --- 4. Adım: Pürüzsüz Model Çizgisi için Veri Üret ---

    # Zaman aralığı boyunca 500 pürüzsüz nokta oluştur

    X_smooth_ordinal = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)

    y_smooth_pred = model.predict(X_smooth_ordinal)

    

    # Bu pürüzsüz noktaları grafikte çizmek için tarihe geri çevir

    X_smooth_dates = [pd.Timestamp.fromordinal(int(val)) for val in X_smooth_ordinal.flatten()]

    

    # Karşılaştırma için Grafik J'deki Hareketli Ortalamayı da hesapla

    df_plot['au_rolling_mean'] = df_plot['au'].rolling(window=30, min_periods=1, center=True).mean()





    # --- 5. Adım: GRAFİK L (Model Fit Grafiği) ---

    

    fig1, ax1 = plt.subplots(figsize=(15, 7))

    

    # Arka plana Grafik J'deki gibi noktaları çiz (hızlı versiyon)

    # Renk/Marker ayrımı yerine tümünü AU'ya göre renklendir

    sc = ax1.scatter(

        df_plot['day'], y, c=y, cmap='turbo', 

        norm=mcolors.Normalize(vmin=y.min(), vmax=y.max()), 

        alpha=0.6, s=30, zorder=5, label='Actual Detections (N=189)'

    )

    fig1.colorbar(sc, ax=ax1, label='AU Value')

    

    # Grafik J'deki Hareketli Ortalamayı çiz (Karşılaştırma için)

    ax1.plot(df_plot['day'], df_plot['au_rolling_mean'], color='red', linestyle='--', 

             linewidth=2.5, label='30-Point Rolling Mean (Data-Driven)', zorder=10)

    

    # Bizim yeni Regresyon Modelimizi çiz

    ax1.plot(X_smooth_dates, y_smooth_pred, color='blue', linestyle='-', 

             linewidth=3.0, label=f'{degree}-Deg. Polynomial Fit (Model-Driven)', zorder=11)

             

    # R-kare değerini grafiğe yaz

    r2_text = f"$R^2 = {r2:.3f}$"

    ax1.text(0.02, 0.98, r2_text, transform=ax1.transAxes, fontsize=12,

             verticalalignment='top', ha='left',

             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='black'))

    

    ax1.set_title(f'Polynomial Regression Fit (Degree={degree}) vs. Rolling Mean', fontsize=14)

    ax1.set_xlabel('Date')

    ax1.set_ylabel('AU Value')

    ax1.legend()

    ax1.grid(True, linestyle=':', alpha=0.7)

    

    plt.tight_layout()

    savefig(fig1, f"regression_model_fit_poly{degree}d")

    plt.close(fig1)



    # --- 6. Adım: GRAFİK M (Artık/Residual Grafiği) ---

    

    fig2, ax2 = plt.subplots(figsize=(15, 5))

    

    # Artıkları (hataları) zamana göre çiz

    # Hataları pozitif/negatif olarak 'coolwarm' cmap ile renklendir

    sc_res = ax2.scatter(

        df_plot['day'], residuals, c=residuals, 

        cmap='coolwarm', vmin=-abs(residuals).max(), vmax=abs(residuals).max(),

        alpha=0.8, s=30,

        label='Residuals (Actual - Predicted)'

    )

    fig2.colorbar(sc_res, ax=ax2, label='Residual Value (AU)')

    

    # Sıfır Hata (Y=0) çizgisini çiz

    ax2.axhline(0, color='black', linestyle='--', linewidth=1.5, label='Zero Error (Model Prediction)')

    

    ax2.set_title(f'Residuals of {degree}-Degree Polynomial Model vs. Time', fontsize=14)

    ax2.set_xlabel('Date')

    ax2.set_ylabel('Residual (Actual AU - Predicted AU)')

    ax2.legend()

    ax2.grid(True, linestyle=':', alpha=0.7)

    

    plt.tight_layout()

    savefig(fig2, f"regression_residuals_vs_time_poly{degree}d")

    plt.close(fig2)

    

    print("--- Regression Analysis (L & M) generated ---")







# ----------------------------------------------------------------- #

# ----- YENİ FONKSİYON: N) DBSCAN KÜMELEME ANALİZİ (OUTLIER) -----

# ----------------------------------------------------------------- #

def plot_dbscan_clustering_au_vs_time(df_all_matches: pd.DataFrame, eps: float = 0.3, min_samples: int = 5):

    """

    Tüm tespitleri (189 nokta) (Zaman, AU) 2D uzayında kümeleyerek

    doğal grupları ve "gürültü" (outlier) olan noktaları bulur.

    

    Yöntem: DBSCAN (Density-Based Spatial Clustering)

    

    - Veriyi önce StandardScaler ile ölçekler (çünkü Zaman ve AU farklı birimlerdedir).

    - eps (komşuluk yarıçapı) ve min_samples (küme için min. komşu) parametrelerini kullanır.

    - Sonuçları renkli bir scatter plot olarak çizer.

    - GÜNCELLENDİ: Yüksek kontrastlı, hard-code renkler (Kırmızı/Yeşil) kullanır.

    """

    if df_all_matches.empty:

        print("DBSCAN Clustering (N) için veri bulunamadı.")

        return



    print(f"\n--- Generating DBSCAN Clustering (N) (eps={eps}, min_samples={min_samples}) ---")



    # --- 1. Adım: Veri Hazırlığı (X) ---

    df_plot = df_all_matches.sort_values("day").copy()

    

    # Zamanı sayısal (ordinal) değere çevir

    df_plot['time_ordinal'] = df_plot['day'].map(pd.Timestamp.toordinal)

    

    # Kümeleme için X matrisini (Zaman, AU) olarak hazırla

    X = df_plot[['time_ordinal', 'au']].values



    # --- 2. Adım: Veriyi Ölçeklendirme (ÇOK ÖNEMLİ) ---

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print("  -> Data (Time, AU) scaled with StandardScaler.")



    # --- 3. Adım: DBSCAN Modelini Çalıştır ---

    db = DBSCAN(eps=eps, min_samples=min_samples)

    labels = db.fit_predict(X_scaled)

    

    # Bulunan küme sayısını (gürültü hariç) ve gürültü miktarını hesapla

    unique_labels = set(labels)

    n_clusters_ = len(unique_labels) - (1 if -1 in labels else 0)

    n_noise_ = list(labels).count(-1)

    

    print(f"  -> DBSCAN Result: Found {n_clusters_} cluster(s) and {n_noise_} noise/outlier points.")



    # --- 4. Adım: Grafiği Çiz ---

    fig, ax = plt.subplots(figsize=(15, 7))

    

    # --- RENK PALETİ GÜNCELLENMESİ BAŞLANGICI ---

    # Renklerin karışmasını engellemek için, renkleri 'hard-code' olarak atıyoruz.

    # Kırmızı (Cluster 1) ve Yeşil (Cluster 2) olarak güncellendi.

    cluster_colors = {

        0: '#E41A1C',  # Parlak Kırmızı (Cluster 1 için)

        1: '#4DAF4A',  # Parlak Yeşil (Cluster 2 için)

        2: '#377EB8',  # Parlak Mavi (Eğer 3. küme çıkarsa)

        3: '#984EA3',  # Mor (Eğer 4. küme çıkarsa)

        # Gerekirse daha fazla eklenebilir

    }

    # --- RENK PALETİ GÜNCELLENMESİ SONU ---





    # Lejant için handle'lar

    legend_handles = []



    for k in unique_labels:

        # Bu etikete (k) sahip noktaları seç

        class_member_mask = (labels == k)

        xy = df_plot[class_member_mask]

        

        if k == -1:

            # Etiket -1 ise, bu Gürültü/Outlier'dır

            # Bunları siyah 'X' ile çiz

            h = ax.scatter(xy['day'], xy['au'], s=50, c='black', 

                         marker='x', 

                         label=f'Noise / Outlier (N={n_noise_})', 

                         zorder=10)

            legend_handles.append(h)

        else:

            # Normal bir küme ise (0, 1, 2...)

            # Renk paletinden bir renk al

            # GÜNCELLENDİ: Hard-code haritadan renk al

            col = cluster_colors.get(k, 'grey') # Haritadan rengi al, bulamazsa gri yap

            cluster_name = f'Cluster {k + 1} (N={len(xy)})' 

            h = ax.scatter(xy['day'], xy['au'], s=30, alpha=0.8,

                         c=col, # Artık [col] değil, doğrudan 'col'

                         edgecolor='black', linewidth=0.5, 

                         label=cluster_name, zorder=5)

            legend_handles.append(h)



    ax.set_title(f'DBSCAN Clustering Analysis (Time vs. AU) (eps={eps}, min_samples={min_samples})', fontsize=14)

    ax.set_xlabel('Date')

    ax.set_ylabel('AU Value')

    ax.legend(handles=legend_handles, title='Detected Groups') 

    ax.grid(True, linestyle=':', alpha=0.7)

    

    plt.tight_layout()

    savefig(fig, f"dbscan_clusters_au_vs_time_eps{eps}_min{min_samples}")

    plt.close(fig)

    print("--- DBSCAN Clustering (N) generated ---")



# === GÜNCELLEME (Ki-Kare için eklendi) ===

    # Analiz için etiketleri ve kullanılan sıralı df'i geri döndür

    return df_plot, labels







# ----------------------------------------------------------------- #

# ----- YENİ FONKSİYON: O) KÜME KOMPOZİSYON ANALİZİ (Ki-Kare) -----

# ----------------------------------------------------------------- #

def perform_cluster_composition_analysis(df_with_clusters: pd.DataFrame):

    """

    DBSCAN (N) tarafından üretilen küme etiketlerini (cluster_label) alır

    ve bunları orijinal 'window' kategorileri (1d, 10d, 100d) ile karşılaştırır.



    Çıktı olarak bir Kontenjans Tablosu (Crosstab) ve 

    Ki-Kare (Chi-Squared) bağımsızlık testini üretir.

    

    Sonuçları konsola ve "cluster_composition_analysis_chi2.txt" dosyasına yazdırır.

    """

    if df_with_clusters.empty or 'cluster_label' not in df_with_clusters.columns:

        print("Küme Kompozisyon Analizi (O) için veri veya 'cluster_label' sütunu bulunamadı.")

        return

        

    print("\n--- Performing Cluster Composition Analysis (O) (Crosstab & Chi-Squared Test) ---")

    

    # Kopyasını alarak çalış (Warning önlemi)

    df_analysis = df_with_clusters.copy()



    # --- 1. Adım: Veri Hazırlığı (Etiketleri Anlamlandırma) ---

    

    # DBSCAN etiketlerini metne dönüştür

    # Not: Renkler Grafik N'deki hard-code paletle eşleşmeli (0=Kırmızı, 1=Yeşil)

    label_map = {

        -1: "Gürültü / Outlier",

        0: "Küme 1 (Kırmızı)",

        1: "Küme 2 (Yeşil)"

        # Eğer N'de 2. küme (mavi) çıkarsa buraya eklenir

    }

    # Window etiketlerini metne dönüştür

    window_map = {

        1: "1d Window",

        10: "10d Window",

        100: "100d Window"

    }



    df_analysis['cluster_name'] = df_analysis['cluster_label'].map(label_map).fillna(f"Diğer Küme ({df_analysis['cluster_label']})")

    df_analysis['window_name'] = df_analysis['window'].map(window_map)

    

    # --- 2. Adım: Kontenjans Tablosu (Crosstab) ---

    

    # Ana tablo (Test için - Toplamlar hariç)

    # Satırlar: window, Sütunlar: cluster

    crosstab_table = pd.crosstab(

        df_analysis['window_name'], 

        df_analysis['cluster_name']

    )

    

    # Olası tüm kategorilerin tabloda olmasını garantile

    # (Eğer 1d'de hiç outlier yoksa bile sütun/satır görünsün)

    all_windows = ['1d Window', '10d Window', '100d Window']

    # DBSCAN'in bulduğu tüm metin etiketlerini al

    all_clusters = sorted(df_analysis['cluster_name'].unique()) 

    

    crosstab_table = crosstab_table.reindex(

        index=all_windows, 

        columns=all_clusters, 

        fill_value=0

    )



    # Göstermelik tablo (Toplamlar dahil)

    crosstab_with_totals = pd.crosstab(

        df_analysis['window_name'], 

        df_analysis['cluster_name'],

        margins=True, 

        margins_name="Toplam"

    ).reindex(

        index=all_windows + ["Toplam"], 

        columns=all_clusters + ["Toplam"], 

        fill_value=0

    )

    

    # --- 3. Adım: Ki-Kare (Chi-Squared) Testi ---

    

    try:

        chi2_stat, p_val, dof, expected_freqs = chi2_contingency(crosstab_table)

        

        # --- 4. Adım: Sonuçları Formatla ve Yazdır ---

        output_lines = []

        output_lines.append("############################################################")

        output_lines.append("### (O) Küme Kompozisyon Analizi (Ki-Kare Testi) Sonuçları ###")

        output_lines.append("############################################################")

        

        output_lines.append("\n--- 1. Kontenjans Tablosu (Gözlenen Frekanslar) ---")

        output_lines.append(crosstab_with_totals.to_string())

        

        output_lines.append("\n--- 2. Ki-Kare (Chi-Squared) Test İstatistikleri ---")

        output_lines.append(f"  Ki-Kare Değeri (chi2)   : {chi2_stat:.4f}")

        output_lines.append(f"  Serbestlik Derecesi (dof): {dof}")

        output_lines.append(f"  p-değeri (p-value)       : {p_val:.6f}")

        

        output_lines.append("\n--- 3. Yorum ---")

        if p_val < 0.05:

            output_lines.append(f"  SONUÇ: p-değeri ({p_val:.2e}) < 0.05 olduğu için istatistiksel olarak ANLAMLIDIR.")

            output_lines.append("  -> 'window' tipi (1d, 10d, 100d) ile 'küme etiketi' (Gürültü, Küme 1, Küme 2)")

            output_lines.append("     arasında GÜÇLÜ bir ilişki (bağımlılık) vardır.")

        else:

            output_lines.append(f"  SONUÇ: p-değeri ({p_val:.6f}) >= 0.05 olduğu için istatistiksel olarak ANLAMLI DEĞİLDİR.")

            output_lines.append("  -> 'window' tipi ile 'küme etiketi' arasında anlamlı bir ilişki bulunamamıştır (bağımsızdırlar).")



        output_lines.append("############################################################")



        # Sonuçları konsola bas

        print("\n" + "\n".join(output_lines))

        

        # Sonuçları dosyaya kaydet

        filepath = OUTDIR / "cluster_composition_analysis_chi2.txt"

        with open(filepath, "w", encoding='utf-8') as f:

            f.write("\n".join(output_lines))

            

        print(f"\nAnaliz sonuçları şuraya kaydedildi: {filepath.name}")



    except ValueError as e:

        print(f"HATA: Ki-Kare testi çalıştırılamadı. Veri yetersiz olabilir. Hata: {e}")

        print("Oluşturulan Crosstab:")

        print(crosstab_table)



    print("--- Cluster Composition Analysis (O) generated ---")







# ----------------------------- #

# 5) RUN: GENERATE ALL FIGURES

# ----------------------------- #

if __name__ == "__main__":



    # --- Önceki hatanı düzelt (2GEÇ-09-24) ---

    if "2GEÇ-09-24" in csv_100d_matches:

        print("Hata düzeltiliyor: 2GEÇ-09-24 -> 2006-09-24")

        csv_100d_matches = csv_100d_matches.replace("2GEÇ-09-24", "2006-09-24")

        df_100d = pd.read_csv(StringIO(csv_100d_matches), parse_dates=["day"])

        df_matches = pd.concat([df_1d, df_10d, df_100d], ignore_index=True)

        df_matches["window"] = df_matches["window"].astype(int)

        df_matches = df_matches.sort_values(["window", "day"]).reset_index(drop=True)



    # --- Senin sağladığın 100 gün listesi ---

    target_100_days_str_list = [

        "1960-07-11", "1961-05-20", "1962-12-03", "1963-09-18", "1964-02-25",

        "1966-10-30", "1967-08-08", "1968-04-14", "1969-11-02", "1970-01-27",

        "1971-06-09", "1972-03-21", "1974-05-16", "1975-02-04", "1976-07-29",

        "1978-01-19", "1979-04-05", "1980-10-12", "1982-02-17", "1983-05-24",

        "1984-03-11", "1985-08-11", "1986-12-28", "1987-07-15", "1989-01-08",

        "1990-09-13", "1991-03-05", "1992-06-20", "1993-10-02", "1995-04-22",

        "1996-08-30", "1997-11-17", "1998-05-03", "2000-01-23", "2001-07-07",

        "2002-09-19", "2003-03-12", "2004-06-18", "2006-04-09", "2007-10-25",

        "2008-01-31", "2009-08-27", "2011-02-14", "2012-11-09", "2013-05-11",

        "2014-07-23", "2015-09-04", "2017-06-11", "2018-10-18", "2019-12-25",

        "2020-03-09", "2021-08-16", "2023-01-04", "2024-05-29", "2025-09-15",

        "1960-11-28", "1962-08-14", "1964-07-03", "1966-01-12", "1968-09-05",

        "1970-08-22", "1972-01-07", "1974-12-11", "1976-03-18", "1978-08-02",

        "1980-04-29", "1982-07-01", "1984-01-20", "1985-11-06", "1987-02-26",

        "1989-05-19", "1990-12-01", "1992-02-11", "1993-08-09", "1995-07-28",

        "1996-02-02", "1998-03-29", "2000-06-07", "2001-10-15", "2002-12-08",

        "2004-04-16", "2006-09-24", "2007-05-30", "2008-12-13", "2009-03-22",

        "2011-09-01", "2012-07-18", "2014-02-09", "2015-06-27", "2017-03-14",

        "2018-02-20", "2019-07-04", "2020-11-21", "2021-04-26", "2023-06-03",

        "2024-09-10", "1979-06-15", "1997-06-15", "2011-11-30", "2025-01-17"

    ]

    # --- ---



    print("Generating standard plots (A-F)...")



    # A) Daily counts

    for w in [1,10,100]:

        df_win = df_matches[df_matches["window"]==w]

        if w != 100 or len(df_win['day'].unique()) < 200:

            plot_daily_counts(df_win)

        else:

            print(f"Skipping daily counts for {w}d (too many days)")



    # B) AU heatmaps

    for w in [1,10,100]:

        df_win = df_matches[df_matches["window"]==w]

        if w != 100 or len(df_win['day'].unique()) < 200:

            plot_au_heatmap(df_win)

        else:

            print(f"Skipping AU heatmap for {w}d (too many days)")



    # C) Eski Presence matrices (Yorumda)

    # print("\nGenerating old Presence Matrix plots (C)...")

    # for w in [1,10,100]:

    #     plot_presence_matrix(df_matches[df_matches["window"]==w], df_repeats[df_repeats["window"]==w], top_n=TOP_N_OLD)



    # D) AU distribution

    print("\nGenerating AU Distribution plot (D)...")

    plot_au_distribution(df_matches)



    # E) AU vs Repeat

    print("\nGenerating AU vs Repeat plots (E)...")

    for w in [1,10,100]:

        plot_au_vs_repeat(

            df_matches[df_matches["window"]==w],

            df_repeats[df_repeats["window"]==w]

        )



    # F) AU Stripplot

    print("\nGenerating AU Stripplot (F)...")

    plot_au_stripplot(df_matches, ylim=(11, 14.5), jitter=0.10, alpha=0.6)



    # ----------------------------------------------------------------- #

    # G) KOMBO GRAFİK (10d + 1d PIP) - SON HALİ

    # ----------------------------------------------------------------- #

    print("\nGenerating Combo Plot (G: 10d Heatmap + 1d Inset)...")

    plot_presence_heatmap_10d_with_1d_inset(

        df_matches[df_matches["window"]==10],

        df_repeats[df_repeats["window"]==10],

        df_matches[df_matches["window"]==1],

        df_repeats[df_repeats["window"]==1]

    )



    # ----------------------------------------------------------------- #

    # H) YENİ 100d PRESENCE MATRIX (KODLANMIŞ EKSENLER)

    # ----------------------------------------------------------------- #

    df_100d_match_data = df_matches[df_matches["window"]==100]

    df_100d_rep_data = df_repeats[df_repeats["window"]==100]



    if not df_100d_match_data.empty and not df_100d_rep_data.empty:

        plot_presence_matrix_100d(

            df_100d_match_data,

            df_100d_rep_data,

            target_100_days_str_list # Sağlanan 100 günü fonksiyona ver

        )

    else:

        print("\nSkipping 100d Presence Matrix (H) because 100d data is missing or empty.")



    # ----------------------------------------------------------------- #

    # I) YENİ MASTER PLOT (111d x 149obj) ÇAĞRISI

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW MASTER Plot (I: 111d x 149obj)...")

    

    # 1. Master Cisim Listesini (149) oluştur

    all_unique_objects = df_repeats['object_id'].dropna().unique()

    master_object_list_sorted = sorted(list(all_unique_objects))

    print(f"  -> Master Object List: {len(master_object_list_sorted)} benzersiz cisim bulundu.")



    # 2. Master Gün Listesini (111) oluştur

    target_10d_days_str_list = [

        "1965-03-15", "1973-11-29", "1981-09-01", "1988-06-23", "1994-01-10", 

        "1999-08-14", "2005-02-28", "2010-12-05", "2016-04-19", "2022-07-22"

    ]

    target_1d_day_str_list = []

    if not df_1d.empty:

        target_1d_day_str_list = [df_1d['day'].iloc[0].strftime('%Y-%m-%d')]



    all_days_str_set = set(target_100_days_str_list) | set(target_10d_days_str_list) | set(target_1d_day_str_list)

    master_day_list_sorted_dt = pd.to_datetime(list(all_days_str_set)).sort_values().values

    print(f"  -> Master Day List: {len(master_day_list_sorted_dt)} benzersiz gün bulundu (Hedef 111).")



    # 3. Master Fonksiyonu Çağır (DÜZELTİLMİŞ HALİYLE)

    if not df_matches.empty and master_object_list_sorted and master_day_list_sorted_dt.size > 0:

        plot_presence_matrix_111d_149obj(

            df_all_matches=df_matches,             

            master_object_list=master_object_list_sorted, 

            master_day_list=master_day_list_sorted_dt    

        )

    else:

        print("\nSkipping MASTER Presence Matrix (I) because data is missing or empty.")





    print(f"\nDone. All files saved under: {OUTDIR}")





# ----------------------------------------------------------------- #

    # J) YENİ ANALİZ GRAFİĞİ (AU vs ZAMAN SCATTER - OUTLIER ANALİZLİ)

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW Analysis Plot (J: AU vs Time Scatter with Outliers)...")

    

    # Fonksiyonun artık 'master_object_list_sorted' listesine ihtiyacı var

    # Bu listenin "Bölüm I" içinde tanımlandığından emin ol

    if not df_matches.empty and 'master_object_list_sorted' in locals():

        plot_au_over_time_scatter(df_matches, master_object_list_sorted)

    else:

        if df_matches.empty:

            print("\nSkipping AU vs Time Scatter (J) because data is missing.")

        else:

            print("\nSkipping AU vs Time Scatter (J) because 'master_object_list_sorted' was not found (Check Plot I).")





# ----------------------------------------------------------------- #

    # K) YENİ ANALİZ GRAFİĞİ (AU YOĞUNLUK - EPOCH'A GÖRE)

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW Analysis Plot (K: AU Density by Epoch)...")

    if not df_matches.empty:

        plot_au_density_by_epoch(df_matches, split_year=1990)

    else:

        print("\nSkipping AU Density by Epoch (K) because data is missing.")





    print(f"\nDone. All files saved under: {OUTDIR}")



# ----------------------------------------------------------------- #

    # L & M) YENİ ANALİZ GRAFİĞİ (REGRESYON ANALİZİ)

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW Analysis Plot (L & M: Regression Analysis)...")

    

    # Bu fonksiyonun 'master_object_list_sorted' listesine İHTİYACI YOK

    # Sadece verinin kendisine ihtiyacı var

    if not df_matches.empty:

        plot_regression_analysis_au_vs_time(df_matches, degree=3)

    else:

        print("\nSkipping Regression Analysis (L & M) because data is missing.")





    print(f"\nDone. All files saved under: {OUTDIR}")





# ----------------------------------------------------------------- #

    # N) YENİ ANALİZ GRAFİĞİ (DBSCAN KÜMELEME)

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW Analysis Plot (N: DBSCAN Clustering)...")

    

    df_clustered_results = None  # (O) adımı için sonuçları sakla

    

    if not df_matches.empty:

        # --- ENGLISH COMMENTS ---

        # Playing with these parameters will change the number of clusters found.

        # eps = Radius (decreasing it finds more outliers)

        # min_samples = Min. number of neighbors (increasing it finds more outliers)

        

        # GÜNCELLEME: Fonksiyon artık (df_plot, labels) döndürüyor

        df_plot_sorted, cluster_labels = plot_dbscan_clustering_au_vs_time(

            df_matches, eps=0.3, min_samples=5

        )

        

        # Etiketleri DataFrame'e ekle ve (O) adımı için sakla

        df_plot_sorted['cluster_label'] = cluster_labels

        df_clustered_results = df_plot_sorted.copy()

        

    else:

        print("\nSkipping DBSCAN Clustering (N) because data is missing.")



    # ----------------------------------------------------------------- #

    # O) YENİ ANALİZ: KÜME KOMPOZİSYONU (Ki-Kare Testi)

    # ----------------------------------------------------------------- #

    print("\nGenerating NEW Analysis (O: Cluster Composition & Chi-Squared Test)...")

    

    if df_clustered_results is not None:

        # (N) adımından alınan etiketli DataFrame'i kullanarak analizi yap

        perform_cluster_composition_analysis(df_clustered_results)

    else:

        print("\nSkipping Cluster Composition (O) because DBSCAN results (N) are missing.")