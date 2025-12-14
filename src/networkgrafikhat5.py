import networkx as nx
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D 

# 1. Grafik Nesnesini Oluştur
G = nx.Graph()

# 2. Düğümleri (Gök Cisimleri) Tanımla (Aynı)
nodes_list = [
    ("Earth", {"type": "normal"}),
    ("3763 Qianxuesen (21)", {"type": "normal"}), 
    ("27827 Ukai(20)", {"type": "normal"}), 
    ("15025 Uwontario(34)", {"type": "normal"}), 
    ("23900 Urakawa(26)", {"type": "normal"}), 
    ("755 Quintilla(31)", {"type": "normal"}),
    ("55701 Ukalegon (4)", {"type": "ana_kapi"}),
    ("84011 Jean-Claude (5)", {"type": "ana_kapi"}),
]
G.add_nodes_from(nodes_list)

# 3. Kenarları (Bağlantılar) Tanımla (Aynı)
edges_list = [
    ('Earth', '3763 Qianxuesen (21)', {'weight': 76.94, 'type': 'ana_yol_turuncu'}), 
    ('3763 Qianxuesen (21)', '15025 Uwontario(34)', {'weight': 4.41, 'type': 'ana_yol_turuncu'}), 
    ('15025 Uwontario(34)', '55701 Ukalegon (4)', {'weight': 139.58, 'type': 'ana_yol_turuncu'}), 
    ('Earth', '755 Quintilla(31)', {'weight': 40.98, 'type': 'ara_yol_yesil'}), 
    ('755 Quintilla(31)', '84011 Jean-Claude (5)', {'weight': 9.58, 'type': 'ara_yol_yesil'}), 
    ('Earth', '27827 Ukai(20)', {'weight': 77.6983, 'type': 'diger'}), 
    ('Earth', '23900 Urakawa(26)', {'weight': 40.0838, 'type': 'diger'}), 
    ('27827 Ukai(20)', '3763 Qianxuesen (21)', {'weight': 1.4245, 'type': 'diger'}), 
    ('27827 Ukai(20)', '15025 Uwontario(34)', {'weight': 3.6608, 'type': 'diger'}),
    ('3763 Qianxuesen (21)', '23900 Urakawa(26)', {'weight': 39.051, 'type': 'diger'}), 
    ('23900 Urakawa(26)', '755 Quintilla(31)', {'weight': 1.4424, 'type': 'diger'}),
    ('23900 Urakawa(26)', '84011 Jean-Claude (5)', {'weight': 9.58, 'type': 'diger'}),
    ('23900 Urakawa(26)', '55701 Ukalegon (4)', {'weight': 180.8505, 'type': 'diger'}),
    ('55701 Ukalegon (4)', '84011 Jean-Claude (5)', {'weight': 171.4316, 'type': 'diger'}),
]
G.add_edges_from(edges_list)

# 4. Görsel Düzen (Layout) (Aynı)
pos = {
    'Earth': (0, 0),
    '23900 Urakawa(26)': (5, 5),
    '3763 Qianxuesen (21)': (3, 8), 
    '755 Quintilla(31)': (7, 2), 
    '27827 Ukai(20)': (3, 11),
    '15025 Uwontario(34)': (7, 9),
    '84011 Jean-Claude (5)': (10, 2),
    '55701 Ukalegon (4)': (10, 10),
}

# 5. Görselleştirme Ayarları (Aynı)
plt.figure(figsize=(16, 10))

color_main = '#FFC266' # Yumuşak turuncu
color_secondary = '#C1FFC1' # Yeşil (Aynı)

node_colors = ['gold' if G.nodes[node]['type'] == 'ana_kapi' else '#ADD8E6' for node in G.nodes()]
ana_yol_turuncu_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'ana_yol_turuncu'] 
ara_yol_yesil_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'ara_yol_yesil']
diger_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'diger']
edge_labels = nx.get_edge_attributes(G, 'weight')

# 6. Grafiği Çizdirme (Aynı)
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=node_colors, edgecolors='black')
nx.draw_networkx_edges(G, pos, edgelist=ana_yol_turuncu_edges, width=4, edge_color=color_main, alpha=1.0) 
nx.draw_networkx_edges(G, pos, edgelist=ara_yol_yesil_edges, width=4, edge_color=color_secondary, alpha=1.0) 
nx.draw_networkx_edges(G, pos, edgelist=diger_edges, width=1, edge_color='black', style='dashed', alpha=0.5)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
label_pos = pos.copy() 
label_pos['3763 Qianxuesen (21)'] = (pos['3763 Qianxuesen (21)'][0], pos['3763 Qianxuesen (21)'][1] - 0.7)
label_pos['23900 Urakawa(26)'] = (pos['23900 Urakawa(26)'][0], pos['23900 Urakawa(26)'][1] + 0.7)
label_pos['27827 Ukai(20)'] = (pos['27827 Ukai(20)'][0], pos['27827 Ukai(20)'][1] + 0.7) 
label_pos['15025 Uwontario(34)'] = (pos['15025 Uwontario(34)'][0], pos['15025 Uwontario(34)'][1] + 0.7) 
label_pos['55701 Ukalegon (4)'] = (pos['55701 Ukalegon (4)'][0], pos['55701 Ukalegon (4)'][1] + 0.7) 
label_pos['84011 Jean-Claude (5)'] = (pos['84011 Jean-Claude (5)'][0], pos['84011 Jean-Claude (5)'][1] - 0.7)
label_pos['755 Quintilla(31)'] = (pos['755 Quintilla(31)'][0], pos['755 Quintilla(31)'][1] - 0.7) 
outside_list = [
    '55701 Ukalegon (4)', '84011 Jean-Claude (5)', '755 Quintilla(31)', 
    '27827 Ukai(20)', '15025 Uwontario(34)',
    '3763 Qianxuesen (21)', '23900 Urakawa(26)'
]
inside_labels = {node: node for node in G.nodes() if node not in outside_list}
nx.draw_networkx_labels(G, pos, labels=inside_labels, font_size=10, font_weight='bold')
outside_labels = {node: node for node in G.nodes() if node in outside_list}
nx.draw_networkx_labels(G, label_pos, labels=outside_labels, font_size=10, font_weight='bold')

# --- YILDIZLAR VE KAPI ETİKETLERİ (Aynı) ---
star_ukalegon_pos = (label_pos['55701 Ukalegon (4)'][0], label_pos['55701 Ukalegon (4)'][1] + 0.5)
star_jean_pos = (label_pos['84011 Jean-Claude (5)'][0], label_pos['84011 Jean-Claude (5)'][1] - 0.5)

plt.plot(star_ukalegon_pos[0], star_ukalegon_pos[1], marker='*', markersize=20, 
         markerfacecolor=color_main, markeredgecolor='black') 
plt.plot(star_jean_pos[0], star_jean_pos[1], marker='*', markersize=20, 
         markerfacecolor=color_secondary, markeredgecolor='black') 

plt.text(star_ukalegon_pos[0], star_ukalegon_pos[1] + 0.3, 'Main Gate', 
         fontweight='bold', ha='center', fontsize=10)
plt.text(star_jean_pos[0], star_jean_pos[1] - 0.5, 'Secondary Gate', 
         fontweight='bold', ha='center', fontsize=10)
# --- Bitti ---

# 7. Son Ayarlamalar ve Kaydetme (Aynı)
plt.axis('off')
plt.tight_layout()

# --- LEJANT BÖLÜMÜ (GÜNCELLENDİ) ---
legend_elements = [
    Line2D([0], [0], color=color_main, lw=4, label='Main network connection road'), 
    Line2D([0], [0], color=color_secondary, lw=4, label='Secondary network connection road'),
    # YENİ EKLENDİ:
    Line2D([0], [0], color='black', lw=1, linestyle='dashed', label='Other network connection roads')
]
plt.legend(handles=legend_elements, loc='upper left', frameon=False, fontsize=12) 
# --- Bitti ---

# 7a. Kayıt Yolu Tanımla (Aynı)
base_path = r"C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy"
output_folder = "output plots"
output_dir = os.path.join(base_path, output_folder) 

# 7b. Klasörü Kontrol Et ve Oluştur (Aynı)
os.makedirs(output_dir, exist_ok=True)

# 7c. Dosyaları Belirtilen Yola Kaydet (Aynı)
png_path = os.path.join(output_dir, "makale_grafik.png")
pdf_path = os.path.join(output_dir, "makale_grafik.pdf")

plt.savefig(png_path, dpi=300, format='png', bbox_inches='tight')
plt.savefig(pdf_path, format='pdf', bbox_inches='tight')

# Grafiği ekranda göster
plt.show()

# Kullanıcıya bilgi ver
print(f"Grafikler (LEJANT GÜNCELLENDİ) başarıyla şu konuma kaydedildi:\n{output_dir}")