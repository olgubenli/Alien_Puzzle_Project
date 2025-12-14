# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 19:15:00 2025
@author: olgub

AMAC: 6 Rota için 3'lü Karşılaştırma:
1. MT: Fiziksel Mesafe (AU)
2. FT: Formül Maliyeti (Score)
3. EFF: Verimlilik (Cost per AU) -> (FT / MT)
"""

import matplotlib.pyplot as plt
import numpy as np
import os

if __name__ == "__main__":

    # --- VERİLER ---
    routes = ['Route 1', 'Route 2', 'Route 3', 'Route 4', 'Route 5', 'Route 6']
    
    route_descriptions = [
        "1: Earth -> Querquedula -> Jacoby -> Thereus",
        "2: Earth -> Quoc-Bao -> Ulysses -> Thereus",
        "3: Earth -> Quintilla -> Jean-Claude -> Thereus",
        "4: Earth -> Quincy -> Joanllaneras -> Thereus",
        "5: Earth -> Qianxuesen -> Uwontario -> Ukalegon -> Thereus",
        "6: Earth -> Quintilla -> Jeffreyrobbins -> Thereus"
    ]

    # MT (Mesafe) ve FT (Maliyet)
    mt_values = np.array([22.23, 21.81, 22.67, 21.27, 26.29, 18.00])
    ft_values = np.array([220.88, 298.15, 221.24, 220.95, 233.12, 221.31])

    # EFF: VERİMLİLİK (Cost per AU) -> Düşük olan daha iyi
    # Formül: FT / MT
    eff_values = ft_values / mt_values

    # --- GRAFİK AYARLARI ---
    x = np.arange(len(routes))
    width = 0.25  # Barlar 3 tane olacağı için genişliği kıstık

    fig, ax1 = plt.subplots(figsize=(15, 9))

    # --- 1. BAR: MT (SOL EKSEN) ---
    color_mt = '#FFB7B2' # Somon
    rects1 = ax1.bar(x - width, mt_values, width, label='MT: Distance (AU)', 
                     color=color_mt, hatch='//', edgecolor='#555555')
    
    ax1.set_xlabel('Routes', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Physical Distance (AU)', fontsize=12, fontweight='bold', color='#B22222')
    ax1.tick_params(axis='y', labelcolor='#B22222')
    ax1.set_ylim(0, 35)

    # --- 2. BAR: FT (SAĞ EKSEN - 1) ---
    ax2 = ax1.twinx()
    color_ft = '#C7CEEA' # Mavi
    rects2 = ax2.bar(x, ft_values, width, label='FT: Formula Cost', 
                     color=color_ft, hatch='xx', edgecolor='#555555')
    
    ax2.set_ylabel('Total Formula Cost', fontsize=12, fontweight='bold', color='#483D8B')
    ax2.tick_params(axis='y', labelcolor='#483D8B')
    ax2.set_ylim(0, 350)

    # --- 3. BAR: EFF (SAĞ EKSEN - 2 / OFFSET) ---
    # Matplotlib'de 3. eksen için "parasite axis" tekniği
    ax3 = ax1.twinx()
    
    # Sağ ekseni biraz dışarı itiyoruz (Offset)
    ax3.spines["right"].set_position(("axes", 1.08))
    
    color_eff = '#B5EAD7' # Yeşil (Verimlilik Rengi)
    rects3 = ax3.bar(x + width, eff_values, width, label='EFF: Cost per AU (FT/MT)', 
                     color=color_eff, hatch='..', edgecolor='#555555')

    ax3.set_ylabel('Efficiency (Cost / AU)', fontsize=12, fontweight='bold', color='#2E8B57')
    ax3.tick_params(axis='y', labelcolor='#2E8B57')
    ax3.set_ylim(0, 20) # Verimlilik skalası

    # --- BAŞLIK VE LEJANT ---
    plt.title('Triple Comparison: Distance vs Cost vs Efficiency (Lower EFF is Better)', fontsize=14, fontweight='bold', pad=20)
    
    # 3 Lejantı Birleştir
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    
    ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, 
               loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=10)

    # X Ekseni
    ax1.set_xticks(x)
    ax1.set_xticklabels(routes, fontsize=11, fontweight='bold')

    # --- DEĞERLERİ YAZDIRMA ---
    def autolabel(rects, ax, suffix=""):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}{suffix}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

    autolabel(rects1, ax1)
    autolabel(rects2, ax2)
    autolabel(rects3, ax3)

    # --- AÇIKLAMALAR ---
    desc_text = "Route Details:\n" + "\n".join(route_descriptions)
    plt.figtext(0.15, 0.02, desc_text, fontsize=9, 
                bbox={"facecolor":"#F0F0F0", "alpha":0.8, "pad":10})

    fig.tight_layout()
    plt.subplots_adjust(bottom=0.30, right=0.85) # Sağ tarafı 3. eksen için açtık

    # --- KAYIT ---
    parent_dir = r'C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca'
    data_folder_name = 'kopya tarihler dosyalar - Copy'
    output_folder_name = 'output plots'
    full_output_dir = os.path.join(parent_dir, data_folder_name, output_folder_name)
    os.makedirs(full_output_dir, exist_ok=True)
    
    filename = 'route_comparison_Triple_Efficiency'
    fig.savefig(os.path.join(full_output_dir, filename + '.png'), dpi=300)
    fig.savefig(os.path.join(full_output_dir, filename + '.pdf'))

    print(f"Grafik kaydedildi: {os.path.join(full_output_dir, filename + '.png')}")
    print("\n--- HESAPLANAN VERİMLİLİK DEĞERLERİ (FT / MT) ---")
    for i, r in enumerate(routes):
        print(f"{r}: {eff_values[i]:.4f} (Daha düşük = Daha Verimli)")