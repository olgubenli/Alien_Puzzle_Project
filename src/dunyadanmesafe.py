# -*- coding: utf-8 -*-
"""
Created on Sat Nov 29 18:21:00 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Updated for Specific Pairwise Distances on 1977-08-15
Output: dunyadanmesafe.pdf
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# 1 AU (Astronomik Birim) kaç kilometre
AU_KM = 149597870.7

def kepler_denklemini_coz(M_deg, e):
    """
    Kepler'in Denklemini (M = E - e*sin(E)) sayısal olarak çözer.
    """
    M_rad = np.radians(M_deg)
    E_rad = M_rad
    for _ in range(10):
        f = E_rad - e * np.sin(E_rad) - M_rad
        f_prime = 1 - e * np.cos(E_rad)
        E_rad = E_rad - f / f_prime
    return E_rad

def elemanlari_koordinata_cevir(elemanlar, E_rad):
    """
    Yörünge elemanlarını 3D (x, y, z) koordinatlarına çevirir.
    """
    a = elemanlar['a']
    e = elemanlar['e']
    i_rad = np.radians(elemanlar['i'])
    OM_rad = np.radians(elemanlar['om'])
    w_rad = np.radians(elemanlar['w'])

    x_prime = a * (np.cos(E_rad) - e)
    y_prime = a * np.sqrt(1 - e**2) * np.sin(E_rad)

    x = (np.cos(OM_rad) * np.cos(w_rad) - np.sin(OM_rad) * np.sin(w_rad) * np.cos(i_rad)) * x_prime + \
        (-np.cos(OM_rad) * np.sin(w_rad) - np.sin(OM_rad) * np.cos(w_rad) * np.cos(i_rad)) * y_prime
    
    y = (np.sin(OM_rad) * np.cos(w_rad) + np.cos(OM_rad) * np.sin(w_rad) * np.cos(i_rad)) * x_prime + \
        (-np.sin(OM_rad) * np.sin(w_rad) + np.cos(OM_rad) * np.cos(w_rad) * np.cos(i_rad)) * y_prime
    
    z = (np.sin(w_rad) * np.sin(i_rad)) * x_prime + \
        (np.cos(w_rad) * np.sin(i_rad)) * y_prime
    
    return np.array([x, y, z])

def pozisyon_bul(isim, veri_sozlugu):
    """
    Verilen ismin 1977 verilerinden (x,y,z) konumunu döndürür.
    """
    elemanlar = veri_sozlugu[isim]
    E_rad = kepler_denklemini_coz(elemanlar['M'], elemanlar['e'])
    return elemanlari_koordinata_cevir(elemanlar, E_rad)

if __name__ == "__main__":

    # 15 Ağustos 1977 Verileri
    VERI_1977 = {
        'Earth (399)': {'a': 1.001, 'e': 0.0160, 'i': 0.0017, 'om': 14.699, 'w': 86.166, 'M': 222.738},
        'Qianxuesen (3624)': {'a': 2.252, 'e': 0.1050, 'i': 7.0331, 'om': 23.524, 'w': 168.455, 'M': 213.252},
        'Ukai (5229)': {'a': 2.754, 'e': 0.1075, 'i': 6.9828, 'om': 81.519, 'w': 332.997, 'M': 169.331},
        'Urakawa (5558)': {'a': 2.785, 'e': 0.0366, 'i': 3.2642, 'om': 275.323, 'w': 12.340, 'M': 245.843},
        'Quintilla (5289)': {'a': 3.164, 'e': 0.1564, 'i': 3.2269, 'om': 177.636, 'w': 44.958, 'M': 83.284},
        'Uwontario (4198)': {'a': 3.191, 'e': 0.1217, 'i': 7.3445, 'om': 33.766, 'w': 53.827, 'M': 66.134},
        'Jean-Claude (84011)': {'a': 3.946, 'e': 0.2618, 'i': 4.0828, 'om': 10.051, 'w': 46.754, 'M': 234.320},
        'Jeffreyrobbins (169509)': {'a': 3.957, 'e': 0.2571, 'i': 3.3512, 'om': 40.582, 'w': 7.698, 'M': 35.764},
        'Jacoby (25869)': {'a': 3.964, 'e': 0.1446, 'i': 17.0161, 'om': 250.812, 'w': 256.296, 'M': 76.848},
        'Joanllaneas (30601)': {'a': 5.191, 'e': 0.1542, 'i': 10.1370, 'om': 111.213, 'w': 293.278, 'M': 99.278},
        'Ukalegon (55701)': {'a': 5.197, 'e': 0.1400, 'i': 20.9370, 'om': 227.419, 'w': 104.764, 'M': 32.697},
        'Ulysses (5254)': {'a': 5.233, 'e': 0.1213, 'i': 24.1977, 'om': 76.054, 'w': 341.870, 'M': 81.760},
        'Thereus (32532)': {'a': 10.703, 'e': 0.1937, 'i': 20.3389, 'om': 205.311, 'w': 87.320, 'M': 136.444}
    }

    # İstenilen 9 özel çift (Tuple listesi: Cisim 1, Cisim 2)
    # Sözlükteki tam adlarıyla eşleşmelidir.
    pairs_to_calculate = [
        ('Earth (399)', 'Qianxuesen (3624)'),       # 1
        ('Qianxuesen (3624)', 'Uwontario (4198)'),  # 2
        ('Earth (399)', 'Uwontario (4198)'),        # 3
        ('Uwontario (4198)', 'Ukalegon (55701)'),   # 4
        ('Earth (399)', 'Ukalegon (55701)'),        # 5
        ('Qianxuesen (3624)', 'Ukalegon (55701)'),  # 6
        ('Earth (399)', 'Quintilla (5289)'),        # 7
        ('Quintilla (5289)', 'Jean-Claude (84011)'),# 8
        ('Earth (399)', 'Jean-Claude (84011)')      # 9
    ]

    results_list = []

    print(f"--- SPECIFIC PAIR DISTANCES (1977-08-15) ---\n")

    for p1_name, p2_name in pairs_to_calculate:
        # Konumları hesapla
        pos1 = pozisyon_bul(p1_name, VERI_1977)
        pos2 = pozisyon_bul(p2_name, VERI_1977)
        
        # 3D Mesafeyi hesapla
        mesafe_au = np.linalg.norm(pos1 - pos2)
        mesafe_km = mesafe_au * AU_KM
        
        # Etiket ismi oluştur (Örn: Earth - Qianxuesen)
        # Parantez içindeki sayıları görsel sadelik için grafikte temizleyelim
        label_name = f"{p1_name.split(' ')[0]} - {p2_name.split(' ')[0]}"
        
        print(f"{label_name:35} : {mesafe_au:.4f} AU")
        
        results_list.append((label_name, mesafe_au))

    # --- GRAFİK ---
    
    # Küçükten büyüğe sırala (görsel olarak daha iyi okunur)
    results_list.sort(key=lambda x: x[1])
    
    pair_names = [item[0] for item in results_list]
    distances = [item[1] for item in results_list]

    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.barh(pair_names, distances, 
                   color='#FA8072',   # Somon rengi
                   alpha=0.8,
                   edgecolor='black')

    # İngilizce Etiketler
    ax.set_xlabel('Actual Distance (AU) on 1977-08-15', fontsize=12, fontweight='bold')
    ax.set_title('Inter-Body Distances (1977 Configuration)', fontsize=14, fontweight='bold')
    
    # Eksen sınırlarını ayarla
    max_val = max(distances)
    ax.set_xlim(0, max_val * 1.15)

    # Değerleri barların ucuna yaz
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, 
                bar.get_y() + bar.get_height()/2, 
                f'{width:.3f} AU', 
                va='center', ha='left', fontsize=10, fontweight='bold', color='black')

    fig.tight_layout()

    # --- KAYIT ---
    
    parent_dir = r'C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca'
    data_folder_name = 'kopya tarihler dosyalar - Copy'
    output_folder_name = 'output plots'
    
    full_output_dir = os.path.join(parent_dir, data_folder_name, output_folder_name)
    os.makedirs(full_output_dir, exist_ok=True)
    
    # İstenilen dosya adı: dunyadanmesafe.pdf
    save_filename_base = 'dunyadanmesafe'
    
    save_path_pdf = os.path.join(full_output_dir, save_filename_base + '.pdf')
    save_path_png = os.path.join(full_output_dir, save_filename_base + '.png') # Yedek olarak PNG de alalım

    try:
        fig.savefig(save_path_pdf, bbox_inches='tight')
        fig.savefig(save_path_png, bbox_inches='tight', dpi=300)
        
        print(f"\n--- SUCCESS ---")
        print(f"PDF Saved: {save_path_pdf}")
        print(f"PNG Saved: {save_path_png}")
        
    except Exception as e:
        print(f"Error saving file: {e}")

    plt.close(fig)
    