# -*- coding: utf-8 -*-
"""
v37 (Kavramsal Çözüm):
- (Kullanıcı İsteği) Lejant 3-4 space DAHA SOLA kaydırıldı
  (bbox_to_anchor x=0.95 -> 0.90).
- Ana başlık (ax.set_title) kaldırılmış olarak kaldı.
- Diğer tüm ayarlar (v35) aynı kaldı.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from pathlib import Path

# --- VERİ ---
OUTDIR = Path("outputs_plots")
OUTDIR.mkdir(parents=True, exist_ok=True)

print("Graph 4 (Conceptual Pie Chart - Ocean vs Pearls) engine starting...")

# --- 1. Veri Dilimlerini Ayarla ---
# GÖRSEL HİLE:
counts_for_drawing = [
    5,  # <-- HİLE. "Top 8" dilimi
    50, # Grup 1
    25, # Grup 2
    20, # Grup 3
    5   # Grup 4
]

# ETİKET HİLESİ:
true_percentages = [
    "0.04%", # <-- GERÇEK değer
    "50%",
    "25%",
    "20%",
    "5% (Others)"
]

# --- 2. Set Labels, Colors, and Explode ---

labels_legend = [
    f"Top 8 'Pearls' (Anomalies)\n(n=8) - [VISUALLY EXAGGERATED]",
    f"Group 1: 0.001% - 0.756% deviation\n(n=10291)",
    f"Group 2: 0.756% - 1.126% deviation\n(n=5146)",
    f"Group 3: 1.126% - 1.426% deviation\n(n=4116)",
    f"Group 4: > 1.426% deviation\n(n=1029)"
]

# v31 Renkleri
colors = [
    '#B19CD9',  # Yumuşak Mor (İnci - En "Soğuk")
    '#C2E0C6',  # Yumuşak Nane Yeşili (Grup 1)
    '#F7DC6F',  # Yumuşak Sarı (Grup 2)
    '#FAD5A5',  # Yumuşak Turuncu (Grup 3)
    '#F1948A'   # Yumuşak Kırmızı/Somon (Grup 4 - En "Sıcak")
]

# Patlatma
explode = [0.2, 0, 0, 0, 0]


# --- 3. Plot the Pie Chart ---
print("Creating conceptual pie chart...")

fig, ax = plt.subplots(figsize=(14, 10))
fig.patch.set_facecolor('white')

wedges, texts, autotexts = ax.pie(
    counts_for_drawing,
    autopct='',
    startangle=90,
    colors=colors,
    explode=explode,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.2},
    # pctdistance=0.8, # Varsayılanı kaldır, manuel ayarla
    radius=1.1
)

# --- 4. (v35 Ayarı) Etiketleri Manuel Olarak Yaz ---
for i, at in enumerate(autotexts):
    at.set_text(true_percentages[i]) # "0.04%", "50%" vb.
    at.set_color('black')
    at.set_fontweight('bold')
    
    wedge = wedges[i]
    ang_deg = (wedge.theta1 + wedge.theta2) / 2.0
    ang_rad = np.deg2rad(ang_deg)

    # 'Top 8' (0.04%) dilimini manuel olarak ayarla (i == 0)
    if i == 0:
        explode_distance = explode[0] * 1.1
        label_distance = 0.7 * 1.1  # (v35 ayarı: 0.7)
        total_radius = explode_distance + label_distance
        
        x = total_radius * np.cos(ang_rad)
        y = total_radius * np.sin(ang_rad)
        
        at.set_position((x, y))
        at.set_fontsize(13) # (v35 ayarı: 13)
        at.set_ha('center')
        at.set_va('center')
    
    # '50%' (i=1) ve '25%' (i=2)
    # (v34 ayarı: 0.60 - Merkeze yakın)
    elif i in [1, 2]:
        r = wedge.r * 0.60
        x = r * np.cos(ang_rad)
        y = r * np.sin(ang_rad)
        
        at.set_position((x, y))
        at.set_fontsize(14)
        at.set_ha('center')
        at.set_va('center')
        at.set_rotation(0) # Yatay kalsın
        
    # '20%' (i=3)
    # (v34 ayarı: 0.65 - Yeri iyi)
    elif i == 3:
        r = wedge.r * 0.65
        x = r * np.cos(ang_rad)
        y = r * np.sin(ang_rad)

        at.set_position((x, y))
        at.set_fontsize(14)
        at.set_ha('center')
        at.set_va('center')
        at.set_rotation(0) # Yatay kalsın
    
    # '5% (Others)' dilimini (i == 4)
    # (v34 ayarı: 0.78 - Az içeride, çapraz)
    elif i == 4:
        r = wedge.r * 0.78
        x = r * np.cos(ang_rad)
        y = r * np.sin(ang_rad)
        
        at.set_position((x, y))
        at.set_fontsize(14)
        at.set_ha('center')
        at.set_va('center')
        at.set_rotation(ang_deg) # Çapraz yap
        at.set_rotation_mode('anchor')


# --- 5. Add Legend and Title (TRANSLATED) ---
ax.legend(
    wedges,
    labels_legend, 
    title="Match Group Distribution\n(Total 20,590)",
    title_fontsize='14',
    loc="center left",
    bbox_to_anchor=(0.90, 0, 0.5, 1), # <-- GÜNCELLEME: x=0.95 -> 0.90 (Sola kaydı)
    fontsize=12
)

# (v36) Ana başlık kaldırıldı
# ax.set_title(
#     "Distribution of 20,590 Matches\n('Top 8 Pearls' vs 'Ocean' Data)",
#     fontsize=18,
#     fontweight='bold',
#     pad=20
# )

ax.axis('equal') # Dairenin yuvarlak kalmasını sağla

# --- 6. Save ---
save_path_png = OUTDIR / "Grafik_4_Pie_Chart_Pearls_vs_Ocean_v37.png" # v37
save_path_pdf = OUTDIR / "Grafik_4_Pie_Chart_Pearls_vs_Ocean_v37.pdf" # v37

fig.savefig(save_path_png, dpi=300, facecolor='white', bbox_inches='tight')
fig.savefig(save_path_pdf, facecolor='white', bbox_inches='tight')

print("\nGraph successfully created and saved:")
print(f"- {save_path_png.name}")
print(f"- {save_path_pdf.name}")