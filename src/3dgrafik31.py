# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 15:08:14 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 14:57:19 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
ALIEN PUZZLE - FINAL VISUALIZATION ENGINE
v2.35 (Adjusted Step Ratios - Main Route 3)

İstekler:
- Ana Rota '3' (Uwontario->Ukalegon) anotasyonu daha da geri çekilerek
  Uwontario noktasına yaklaştırıldı (%35'ten %20'ye düşürüldü).
- Diğer tüm ayarlar aynı kaldı.
"""

import io, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mpl_toolkits.mplot3d import Axes3D  # noqa
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch

# ---------- 3D Arrow (with head) ----------
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = (np.array(xs), np.array(ys), np.array(zs))
    def draw(self, renderer):
        xs, ys, zs = self._verts3d
        x2d, y2d, z2d = proj3d.proj_transform(xs, ys, zs, self.axes.get_proj())
        self.set_positions((x2d[0], y2d[0]), (x2d[1], y2d[1]))
        super().draw(renderer)
    def do_3d_projection(self, renderer=None):
        xs, ys, zs = self._verts3d
        x2d, y2d, z2d = proj3d.proj_transform(xs, ys, zs, self.axes.get_proj())
        self.set_positions((x2d[0], y2d[0]), (x2d[1], y2d[1]))
        return float(np.min(z2d))

def arrow3d(ax, start, end, color='purple', lw=1.2, mutation_scale=12, alpha=0.95, zorder=9):
    xs, ys, zs = [start[0], end[0]], [start[1], end[1]], [start[2], end[2]]
    patch = Arrow3D(
        xs, ys, zs,
        arrowstyle='-|>', mutation_scale=mutation_scale,
        lw=lw, color=color, alpha=alpha, zorder=zorder,
        path_effects=[pe.withStroke(linewidth=lw+0.9, foreground='black', alpha=0.95)]
    )
    ax.add_artist(patch)
    return patch

# ---------- Data ----------
data_csv = """
obj_name;x_au;y_au;z_au;a_au;e_ecc;i_deg;Omega_deg;w_deg;M_deg
Güneş;0.00000000;0.00000000;0.00000000;0.00000000;0.00000000;0.00000000;0.00000000;0.00000000;0.00000000
Dünya;0.80215124;-0.61830007;-0.00002419;1.00087715;1.60456670;1.72882694;1.46999297;8.61662775;2.22738286
3763 Qianxuesen;1.90336034;1.55136270;0.08176297;2.25234532;0.10508688;7.03311580;0.40381656;2.93988455;3.72147395
15025 Uwontario;-2.98911212;0.66638291;0.28554255;3.19066077;0.12175342;7.34454125;3.37663553;0.93952520;1.15421570
55701 Ukalegon;4.34259832;1.30493985;0.88558169;5.19662994;0.14001388;20.9370897;3.97014457;1.82860822;5.70774783
755 Quintilla;2.56936580;-1.87700564;0.09976281;3.16411998;0.15649329;3.22691829;3.09986326;0.78479207;1.45366432
84011 Jean-Claude;0.08623737;-4.67806678;-0.32987103;3.94605557;0.26187243;4.08286650;1.75437890;0.81604818;4.08906954
"""
df = pd.read_csv(io.StringIO(data_csv), sep=';')
df.loc[df['obj_name']=='Dünya', ['a_au','e_ecc','i_deg','Omega_deg','w_deg','M_deg']] = [1.0, 0.0167, 0.0005, 0.0, 102.9, 0.0]

# ---------- Orbit ----------
def get_orbit_coords(a, e, i_deg, Omega_deg, w_deg, n_points=360):
    if a == 0 or e >= 1: 
        return np.array([]), np.array([]), np.array([])
    i = np.radians(i_deg); Omega = np.radians(Omega_deg); w = np.radians(w_deg)
    nu = np.linspace(0, 2*np.pi, n_points)
    p = a*(1-e**2); r = p/(1+e*np.cos(nu))
    x_p, y_p = r*np.cos(nu), r*np.sin(nu)
    x = (x_p*(np.cos(w)*np.cos(Omega) - np.sin(w)*np.cos(i)*np.sin(Omega)) -
         y_p*(np.sin(w)*np.cos(Omega) + np.cos(w)*np.cos(i)*np.sin(Omega)))
    y = (x_p*(np.cos(w)*np.sin(Omega) + np.sin(w)*np.cos(i)*np.cos(Omega)) +
         y_p*(np.cos(w)*np.cos(i)*np.cos(Omega) - np.sin(w)*np.sin(Omega)))
    z = (x_p*(np.sin(w)*np.sin(i)) + y_p*(np.cos(w)*np.sin(i)))
    return x, y, z

# ---------- Styles / Routes ----------
route_main = ['Dünya','3763 Qianxuesen','15025 Uwontario','55701 Ukalegon']
route_side = ['Dünya','755 Quintilla','84011 Jean-Claude']
STYLES = {
    'Güneş':{'marker':'o','color':'yellow','size':150,'label':'Sun'},
    'Dünya':{'marker':'o','color':'blue','size':70,'label':'Earth'},
    '55701 Ukalegon':{'marker':'*','color':'goldenrod','size':120,'label':'Ukalegon (Main Gate)'},
    '84011 Jean-Claude':{'marker':'*','color':'red','size':120,'label':'Jean-Claude (Secondary Gate)'},
    '3763 Qianxuesen':{'marker':'o','color':'magenta','size':30,'label':'3763 Qianxuesen'},
    '15025 Uwontario':{'marker':'o','color':'black','size':30,'label':'15025 Uwontario'},
    '755 Quintilla':{'marker':'o','color':'green','size':30,'label':'755 Quintilla'},
}
AX_LIMIT=5; VIEW_ANGLE=(30,45)

# --- Relative label offsets (dx, dy, dz) ---
REL_LABEL_OFFSETS = {
    '84011 Jean-Claude': (-0.5,  0.0, +0.5),
    'Dünya':             ( 0.0,  0.0, +1.00),
    '55701 Ukalegon':    ( 0.0,  0.0, -1.50),
}
ARROW_SCALE = 12
ARROW_LW    = 1.2
ARROW_COLOR = 'purple'

# ---------- Axis ----------
def setup_ax(ax):
    ax.set_facecolor('white'); ax.grid(True)
    ax.set_xlabel('X Axis (AU)'); ax.set_ylabel('Y Axis (AU)'); ax.set_zlabel('Z Axis (AU)')
    ax.set_xlim([-AX_LIMIT,AX_LIMIT]); ax.set_ylim([-AX_LIMIT,AX_LIMIT]); ax.set_zlim([-AX_LIMIT,AX_LIMIT])
    ax.set_box_aspect([1,1,1]); ax.view_init(*VIEW_ANGLE)
    try: ax.set_proj_type('ortho')
    except Exception: pass

# ---------- Figure ----------
fig = plt.figure(figsize=(12,10)); plt.style.use('default')
ax = fig.add_subplot(1,1,1, projection='3d')
setup_ax(ax)

# Routes
route_main_coords = df[df['obj_name'].isin(route_main)].set_index('obj_name').loc[route_main][['x_au','y_au','z_au']].values
route_side_coords = df[df['obj_name'].isin(route_side)].set_index('obj_name').loc[route_side][['x_au','y_au','z_au']].values
ax.plot(*route_main_coords.T, color='purple', linestyle='--', linewidth=2, label=None)
ax.plot(*route_main_coords.T, color='orange', linestyle='-', linewidth=2.5, label='Main Connection Network Route')
ax.plot(*route_side_coords.T, color='green', linestyle=':', linewidth=2, label=None)
ax.plot(*route_side_coords.T, color='lime', linestyle='-', linewidth=2, label='Secondary Connection Network Route')


# ---------- Rota Adım Anotasyonları (Oklar + Sayılar) ----------

# --- Ayarlar ---
ANNOTATION_ARROW_LENGTH_AU = 0.5 # Küçük yön oklarının AU cinsinden uzunluğu
ANNOTATION_ARROW_COLOR = 'black'
ANNOTATION_ARROW_LW = 1.5
ANNOTATION_ARROW_MUTATION_SCALE = 10 # Ok başı büyüklüğü

# Sayı metni stili
ANNOTATION_TEXT_OFFSET = np.array([0.0, 0.0, 0.2]) # Sayıyı Z'de 0.2 AU yukarı kaldır
ANNOTATION_TEXT_STYLE = {
    'color': 'white',
    'fontsize': 10,
    'fontweight': 'bold',
    'ha': 'center',
    'va': 'center',
    'path_effects': [pe.withStroke(linewidth=2.5, foreground='black', alpha=1.0)],
    'zorder': 20 # Her şeyin üstünde görünmesi için
}

# --- YENİ: Özel Konumlandırma Yüzdeleri ---
# Her adımın segment üzerinde nerede duracağını belirler (0.5 = tam orta)
CUSTOM_INTERP_RATIOS = {
    # 0.5'ten büyük = Bitiş noktasına (Qianxuesen'e) yakın
    'main_1': 0.65, 
    # 0.5 = Tam orta
    'main_2': 0.5,  
    # 0.5'ten küçük = Başlangıç noktasına (Uwontario'ya) yakın
    'main_3': 0.20, # Uwontario'ya daha da yaklaştırmak için %20'ye düşürüldü
    'side_1': 0.5,
    'side_2': 0.5,
}

# --- 1. Ana Rota (Dünya -> Qianxuesen -> Uwontario -> Ukalegon) ---
for i in range(len(route_main_coords) - 1):
    start_point = route_main_coords[i]
    end_point   = route_main_coords[i+1]
    label = str(i + 1)
    
    # Rota segmenti için özel yüzdeyi al (varsayılan: 0.5)
    key = f'main_{label}'
    interp_ratio = CUSTOM_INTERP_RATIOS.get(key, 0.5)
    
    # Segmentin orta noktası yerine YÜZDELİ noktasını hesapla
    interp_point = (1.0 - interp_ratio) * start_point + interp_ratio * end_point
    
    # Yön vektörü
    segment_vector = end_point - start_point
    unit_vector = segment_vector / np.linalg.norm(segment_vector)
    
    # Ok başlangıç/bitiş noktaları (yeni interp_point etrafında)
    arrow_start = interp_point - (unit_vector * ANNOTATION_ARROW_LENGTH_AU / 2.0)
    arrow_end   = interp_point + (unit_vector * ANNOTATION_ARROW_LENGTH_AU / 2.0)
    
    # Oku çiz
    arrow3d(ax, 
            start=arrow_start, 
            end=arrow_end, 
            color=ANNOTATION_ARROW_COLOR, 
            lw=ANNOTATION_ARROW_LW, 
            mutation_scale=ANNOTATION_ARROW_MUTATION_SCALE, 
            alpha=1.0, 
            zorder=19)
    
    # Sayı metnini çiz (yeni interp_point + Z ofseti)
    text_pos = interp_point + ANNOTATION_TEXT_OFFSET
    ax.text(text_pos[0], text_pos[1], text_pos[2], label, **ANNOTATION_TEXT_STYLE)

# --- 2. Yan Rota (Dünya -> Quintilla -> Jean-Claude) ---
for i in range(len(route_side_coords) - 1):
    start_point = route_side_coords[i]
    end_point   = route_side_coords[i+1]
    label = str(i + 1)
    
    # Rota segmenti için özel yüzdeyi al (varsayılan: 0.5)
    key = f'side_{label}'
    interp_ratio = CUSTOM_INTERP_RATIOS.get(key, 0.5)
    
    # Yüzdeli noktayı hesapla
    interp_point = (1.0 - interp_ratio) * start_point + interp_ratio * end_point
    
    # Vektör
    segment_vector = end_point - start_point
    unit_vector = segment_vector / np.linalg.norm(segment_vector)
    
    # Ok başlangıç/bitiş
    arrow_start = interp_point - (unit_vector * ANNOTATION_ARROW_LENGTH_AU / 2.0)
    arrow_end   = interp_point + (unit_vector * ANNOTATION_ARROW_LENGTH_AU / 2.0)
    
    # Oku çiz
    arrow3d(ax, 
            start=arrow_start, 
            end=arrow_end, 
            color=ANNOTATION_ARROW_COLOR, 
            lw=ANNOTATION_ARROW_LW, 
            mutation_scale=ANNOTATION_ARROW_MUTATION_SCALE, 
            alpha=1.0, 
            zorder=19)
    
    # Sayı metnini çiz
    text_pos = interp_point + ANNOTATION_TEXT_OFFSET
    ax.text(text_pos[0], text_pos[1], text_pos[2], label, **ANNOTATION_TEXT_STYLE)

# -----------------------------------------------------------------


# Orbit thickness settings
dfp = df[df['obj_name']!='Güneş']
min_a, max_a = dfp['a_au'].min(), dfp['a_au'].max()
range_a = max(max_a-min_a, 1e-9)
LW_MIN, LW_MAX = 0.7, 1.7; ALPHA_MIN, ALPHA_MAX = 0.3, 0.8

# Draw loop
for _, row in df.iterrows():
    name=row['obj_name']; sty=STYLES.get(name, {'marker':'o','color':'gray','size':20,'label':name})
    x,y,z = row['x_au'], row['y_au'], row['z_au']

    # marker + glow
    glow_mult = 4.0 if name=='Güneş' else 3.0
    glow_alpha = 0.30 if name=='Güneş' else 0.15
    ax.scatter(x,y,z, marker=sty['marker'], color=sty['color'], s=sty['size']*glow_mult, alpha=glow_alpha, depthshade=True)

    # Cisim noktaları (lejand için)
    ax.scatter(x,y,z, marker=sty['marker'], color=sty['color'], s=sty['size'],
               edgecolor='black', linewidths=1.2 if name!='Dünya' else 1.5,
               depthshade=True, label=sty['label']) 

    # label & arrow (relative)
    if name in REL_LABEL_OFFSETS:
        dx,dy,dz = REL_LABEL_OFFSETS[name]
        xt, yt, zt = x+dx, y+dy, z+dz
        txt_color = 'red' if 'Gate' in sty['label'] else ('blue'if name=='Dünya' else 'black')
        ax.text(xt, yt, zt, sty['label'], color=txt_color, ha='center', va='center',
                path_effects=[pe.withStroke(linewidth=2.2, foreground='white', alpha=0.95)], zorder=10)
        arrow3d(ax, start=(xt,yt,zt), end=(x,y,z),
                color=ARROW_COLOR, lw=ARROW_LW, mutation_scale=ARROW_SCALE, alpha=0.95, zorder=9)

    # orbits
    a,e,i = row['a_au'], row['e_ecc'], row['i_deg']; O,w = row['Omega_deg'], row['w_deg']
    xo,yo,zo = get_orbit_coords(a,e,i,O,w)
    if xo.any():
        norm_a = (a-min_a)/range_a
        lw = LW_MIN + norm_a*(LW_MAX-LW_MIN)
        alpha = ALPHA_MIN + norm_a*(ALPHA_MAX-ALPHA_MIN)
        color = 'khaki' if name=='55701 Ukalegon' else sty['color']

        # İstenilen üç nesnenin yörüngelerine özel legend etiketi ver
        orbit_label = None
        if name == '3763 Qianxuesen':
            orbit_label = "3763 Qianxuesen's Orbit"
        elif name == '15025 Uwontario':
            orbit_label = "15025 Uwontario's Orbit"
        elif name == '755 Quintilla':
            orbit_label = "755 Quintilla's Orbit"

        ax.plot(xo,yo,zo, color=color, linestyle='--', linewidth=lw, alpha=alpha, label=orbit_label)

# Legend (unique)
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='upper left', facecolor='white', framealpha=0.7)

plt.tight_layout()

# Save
save_directory = 'C:/Users/olgub/OneDrive/Masaüstü/uzaylı bulmaca/kopya tarihler dosyalar - Copy'
# Yeni versiyon numarası ile kaydedelim
png = os.path.join(save_directory, 'Alien_Puzzle_SINGLE_PLOT_v2_35_AdjustedStepRatio_Main3.png')
pdf = os.path.join(save_directory, 'Alien_Puzzle_SINGLE_PLOT_v2_35_AdjustedStepRatio_Main3.pdf')
print(f"\nFiles are being saved to: {save_directory}")
try:
    plt.savefig(png, dpi=300, bbox_inches='tight', facecolor='white'); print("PNG saved:", png)
    plt.savefig(pdf, bbox_inches='tight', facecolor='white'); print("PDF saved:", pdf)
except FileNotFoundError:
    print("ERROR: Directory not found:", save_directory)
except Exception as e:
    print("ERROR:", e)

print("\nVisual created successfully.")
plt.show()