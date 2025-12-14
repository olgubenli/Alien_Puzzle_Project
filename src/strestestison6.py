# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 14:06:05 2025

@author: olgub
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- Veri Girişi (k=1'den k=7'ye Top 5 Analizinden) ---
k_values = [1, 2, 3, 4, 5, 6, 7]

# === Ana Kapı (Ukalegon) için Top 5 Rota Maliyetleri ===
ukalegon_data = {
    'Top 1 Route': [220.9343, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343],
    'Top 2 Route': [220.9343, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343],
    'Top 3 Route': [220.9923, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343],
    'Top 4 Route': [221.0013, 220.9923, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343],
    'Top 5 Route': [221.5633, 221.0013, 220.9343, 220.9343, 220.9343, 220.9343, 220.9343]
}
df_ukalegon = pd.DataFrame(ukalegon_data, index=k_values)

# === Ara Kapı (Jean-Claude) için Top 5 Rota Maliyetleri ===
jean_claude_data = {
    'Top 1 Route': [50.5587, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587],
    'Top 2 Route': [50.5587, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587],
    'Top 3 Route': [50.6257, 50.6257, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587],
    'Top 4 Route': [78.3427, 78.3427, 50.5587, 50.5587, 50.5587, 50.5587, 50.5587],
    'Top 5 Route': [142.4267, 142.4267, 50.6257, 50.5587, 50.5587, 50.5587, 50.5587]
}
df_jean_claude = pd.DataFrame(jean_claude_data, index=k_values)

# --- PİP Veri Hazırlığı (Sadece k=1 Anlık Fotoğrafı) ---
pip_x_labels = ['T1', 'T2', 'T3', 'T4', 'T5'] # PİP X-Ekseni
pip_ukalegon_y = [220.9343, 220.9343, 220.9923, 221.0013, 221.5633]
pip_jean_claude_y = [50.5587, 50.5587, 50.6257, 78.3427, 142.4267]


# --- Grafik Çizimi ---

# Yüksek kontrastlı ve farklı çizgi stillerine sahip palet
styles = {
    'Top 1 Route': {'color': '#0072B2', 'linestyle': '--', 'marker': 'o', 'zorder': 10, 'alpha': 0.8},
    'Top 2 Route': {'color': '#E69F00', 'linestyle': '--', 'marker': 's', 'zorder': 9, 'alpha': 0.8},
    'Top 3 Route': {'color': '#33BB55', 'linestyle': ':', 'marker': '^', 'zorder': 8, 'alpha': 0.8},
    'Top 4 Route': {'color': '#CC79A7', 'linestyle': (0, (5, 5)), 'marker': 'D', 'zorder': 7, 'alpha': 0.8},
    'Top 5 Route': {'color': '#D55E00', 'linestyle': '--', 'marker': 'x', 'zorder': 6, 'alpha': 0.8}
}
# PİP grafiğindeki noktalar için renk listesi
pip_colors = [styles[route]['color'] for route in styles]
pip_markers = [styles[route]['marker'] for route in styles]

# Markör Kaydırma (Dodging) Ayarları
dodge_width = 0.2
k_dodged = {
    'Top 1 Route': [k - (dodge_width * 2/3) for k in k_values],
    'Top 2 Route': [k - (dodge_width * 1/3) for k in k_values],
    'Top 3 Route': k_values,
    'Top 4 Route': [k + (dodge_width * 1/3) for k in k_values],
    'Top 5 Route': [k + (dodge_width * 2/3) for k in k_values]
}

# 1x2 (yanyana) bir figür oluştur
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 10))

# === GRAFİK 1: Ana Kapı (Ukalegon) ===

ax1.set_title('Primary Gateway (55701 Ukalegon)', fontsize=16)
ax1.set_xlabel('Number of Match Groups (k)', fontsize=14)
ax1.set_ylabel('Cost to Target', fontsize=14)

# Ana Grafiği Çiz (k=1-7 Evrimi)
for route in styles:
    style_copy = styles[route].copy()
    ax1.plot(k_dodged[route], df_ukalegon[route], 
             label=route,
             color=style_copy.get('color'), 
             linestyle=style_copy.get('linestyle'), 
             marker=style_copy.get('marker'),
             zorder=style_copy.get('zorder'),
             alpha=style_copy.get('alpha', 1.0))

# Ana Grafik Y-Eksenini "Zoomla" (220.8 - 221.7 aralığı)
ax1.set_ylim(220.8, 221.7) 
ax1.set_xticks(k_values)
ax1.legend(loc='upper right', fontsize=12)

# Manuel grid
ax1.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)
ax1.set_axisbelow(True)
for k in k_values:
    ax1.axvline(k, color='grey', linestyle='--', alpha=0.7, linewidth=0.8) 

# === GRAFİK 2: Ara Kapı (Jean-Claude) ===

ax2.set_title('Secondary Gateway (84011 Jean-Claude)', fontsize=16)
ax2.set_xlabel('Number of Match Groups (k)', fontsize=14)
ax2.set_ylabel('Cost to Target', fontsize=14)

# Ana Grafiği Çiz (k=1-7 Evrimi)
for route in styles:
    style_copy = styles[route].copy()
    ax2.plot(k_dodged[route], df_jean_claude[route], 
             label=route,
             color=style_copy.get('color'), 
             linestyle=style_copy.get('linestyle'), 
             marker=style_copy.get('marker'),
             zorder=style_copy.get('zorder'),
             alpha=style_copy.get('alpha', 1.0))

# Ana Grafik Y-Eksenini "Hizala" (34.0 - 150.0 aralığı)
ax2.set_ylim(34.0, 150.0) 
ax2.set_xticks(k_values)
ax2.legend(loc='upper right', fontsize=12)

# Manuel grid
ax2.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)
ax2.set_axisbelow(True)
for k in k_values:
    ax2.axvline(k, color='grey', linestyle='--', alpha=0.7, linewidth=0.8)

# === Genel Başlık ve Kaydetme (PİP'lerden ÖNCE) ===
fig.suptitle('Network Resiliency Stress Test: Top 5 Routes', fontsize=22, fontweight='bold')
plt.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.08, wspace=0.25)


# *** PİP (k=1 Anlık Fotoğrafı) - "Presence Matrix" Mantığı ile Konumlandırma ***
# Koordinatlar [sol, alt, genişlik, yükseklik] (Tüm figüre göre 0-1 arası)

# --- SOL PİP ---
# Konum: sol grafiğin L-şekilli alanında
ax1_inset = fig.add_axes([0.28, 0.40, 0.15, 0.25]) 

# PİP içine 5 noktayı çiz
for i in range(len(pip_x_labels)):
    x_val_label = pip_x_labels[i]
    y_val = pip_ukalegon_y[i]
    ax1_inset.scatter(x_val_label, y_val, 
                      color=pip_colors[i], marker=pip_markers[i], s=50)
    
    if i <= 3: # İlk 4 nokta (T1-T4)
        ax1_inset.text(i + 0.1, y_val + 0.02, f"{y_val:.4f}", 
                       rotation=45, ha='left', va='bottom', fontsize=7, fontweight='bold')
    else: # 5. nokta (T5)
        ax1_inset.text(i - 0.15, y_val, f"{y_val:.4f}", 
                       rotation=0, ha='right', va='center', fontsize=7, fontweight='bold')

# PİP Eksen Ayarları
ax1_inset.set_ylim(220.75, 221.75)
ax1_inset.set_title('k=1 Top 5 Routes', fontsize=10)
ax1_inset.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ax1_inset.grid(True, linestyle=':', alpha=0.5)

# PİP çerçeve kalınlığını ayarla
for spine in ax1_inset.spines.values():
    spine.set_linewidth(2) 

# --- SAĞ PİP ---
# *** GÜNCELLEME: Konum "çok çok az" sağa kaydırıldı (0.80 -> 0.81) ***
ax2_inset = fig.add_axes([0.79, 0.40, 0.15, 0.25]) 

# PİP içine 5 noktayı çiz
for i in range(len(pip_x_labels)):
    x_val_label = pip_x_labels[i]
    y_val = pip_jean_claude_y[i]
    ax2_inset.scatter(x_val_label, y_val, 
                      color=pip_colors[i], marker=pip_markers[i], s=50)
                      
    if i <= 3: # İlk 4 nokta (T1-T4)
        ax2_inset.text(i + 0.1, y_val + 3, f"{y_val:.4f}", 
                       rotation=45, ha='left', va='bottom', fontsize=7, fontweight='bold')
    else: # 5. nokta (T5)
        ax2_inset.text(i - 0.15, y_val, f"{y_val:.4f}", 
                       rotation=0, ha='right', va='center', fontsize=7, fontweight='bold')
                      
# PİP Eksen Ayarları
ax2_inset.set_ylim(40.0, 160.0)
ax2_inset.set_title('k=1 Top 5 Routes', fontsize=10)
ax2_inset.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ax2_inset.grid(True, linestyle=':', alpha=0.5)

# PİP çerçeve kalınlığını ayarla
for spine in ax2_inset.spines.values():
    spine.set_linewidth(2) 


# === Dosyaya Kaydetme ===

# Grafikleri PNG ve PDF olarak kaydet
png_filename = 'Network_Resiliency_Stress_Test_Top5_k1_k7.png'
pdf_filename = 'Network_Resiliency_Stress_Test_Top5_k1_k7.pdf'
files_saved = 0

try:
    fig.savefig(png_filename, dpi=300)
    print(f"'{png_filename}' başarıyla kaydedildi.")
    files_saved += 1
except PermissionError:
    print(f"HATA: '{png_filename}' kaydedilemedi. Dosya başka bir programda açık olabilir.")
except Exception as e:
    print(f"'{png_filename}' kaydedilirken beklenmedik bir hata oluştu: {e}")

try:
    fig.savefig(pdf_filename, dpi=300)
    print(f"'{pdf_filename}' başarıyla kaydedildi.")
    files_saved += 1
except PermissionError:
    print(f"HATA: '{pdf_filename}' kaydedilemedi. Dosya başka bir programda açık olabilir (Adobe, Chrome vb.).")
except Exception as e:
    print(f"'{pdf_filename}' kaydedilirken beklenmedik bir hata oluştu: {e}")

if files_saved == 2:
    print("Grafikler başarıyla oluşturuldu ve PNG/PDF olarak kaydedildi.")
else:
    print("Grafik kaydetme işlemi tamamlandı (bazı hatalarla).")