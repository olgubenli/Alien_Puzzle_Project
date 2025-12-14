import sqlite3
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker # Y-Ekseni ara çizgileri için eklendi

# --- 1. AYARLAR VE VERİTABANI YOLU ---

# Veritabanı (.db) dosyası ayarları
DB_DOSYA_YOLU = r"C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\solar_system_analysis_with_distances.db"
DB_TABLO_ADI = "focused_meta_comparison_results"

# Sıralama için kullanılacak "anahtar" sütun
SORTING_COLUMN = "percentage_diff_of_5uj"

# Sütun isimleri (Ekran görüntüsüne göre doğrulandı)
NAME_COLS = ['earth_object_name', 'q_object_name', 'u_object_name', 'j_object_name']
DIST_COLS = ['earth_object_dist', 'q_object_dist', 'u_object_dist', 'j_object_dist']


def fetch_top_8_matches(db_path, table_name, sort_column):
    """
    Veritabanına bağlanır, 'percentage_diff_of_5uj' sütununa göre
    en iyi 8 eşleşmeyi (satırı) çeker ve 32 'object_dist' noktasını hazırlar.
    """
    print(f"--- 'AU Jump Profile' (Graph 3b) Data Engine v18 (Final Ticks) ---")
    print(f"Reading main database '{os.path.basename(db_path)}'...")
    
    plot_data_rows = []
    conn = None
    
    if not os.path.exists(db_path):
        print(f"!!! CRITICAL ERROR: Database file not found at: {db_path}")
        print("!!! Lütfen kodun 11. satırındaki DB_DOSYA_YOLU değişkenini kontrol et.")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # --- ANA SORGULAMA ---
        sql_query = f"""
            SELECT 
                {', '.join(NAME_COLS)}, 
                {', '.join(DIST_COLS)}
            FROM 
                {table_name}
            ORDER BY
                {sort_column} ASC
            LIMIT 8
        """
        
        print(f"Finding top 8 matches by sorting '{sort_column}'...")
        cursor.execute(sql_query)
        top_8_rows = cursor.fetchall()

        if not top_8_rows:
            print(f"!!! CRITICAL ERROR: No rows found in '{table_name}'.")
            return pd.DataFrame()
            
        if len(top_8_rows) < 8:
            print(f"  > WARNING: Found only {len(top_8_rows)} rows, expected 8.")

        # Bulunan 8 satırı işle
        for i, row in enumerate(top_8_rows):
            match_id_str = f"Match {i+1}"
            
            earth_dist = row[4]
            q_dist = row[5]
            u_dist = row[6]
            j_dist = row[7]
            
            # Veriyi Seaborn'un seveceği "long-form"a dönüştür
            plot_data_rows.append({'Match': match_id_str, 'Object Type': 'Earth (E)', 'Distance': earth_dist})
            plot_data_rows.append({'Match': match_id_str, 'Object Type': 'Q-Object', 'Distance': q_dist})
            plot_data_rows.append({'Match': match_id_str, 'Object Type': 'U-Object', 'Distance': u_dist})
            plot_data_rows.append({'Match': match_id_str, 'Object Type': 'J-Object', 'Distance': j_dist})
            
            print(f"  > Processed {match_id_str}: (E:{row[0]}, Q:{row[1]}, U:{row[2]}, J:{row[3]})")


        return pd.DataFrame(plot_data_rows)

    except sqlite3.Error as e:
        print(f"!!! DATABASE ERROR: {e}")
        print(f"!!! MUHTEMEL HATA: '{sort_column}' adında bir sütun bulunamadı.")
        return pd.DataFrame() 
    finally:
        if conn:
            conn.close()

def create_jump_profile_plot(df):
    """
    Toplanan 32 noktayı (8 eşleşme x 4 cisim) kullanarak
    'AU Atlama Profili' (stripplot) grafiğini çizer.
    v18 GÜNCELLEMESİ: Beyaz arka plan, kesikli paneller, yeni renk paleti
                     VE ONDALIKLI Y-EKSENİ (MINOR TICKS).
    """
    if df.empty:
        print("!!! ERROR: No data found for plotting. Cannot create Graph 3b.")
        return

    print("\n--- GENERATING PLOT (Graph 3b - v18 Final Ticks) ---")
    
    # Beyaz arka plan grid'i
    sns.set_theme(style="whitegrid")
    
    plt.figure(figsize=(16, 9))
    
    # Referans görsellerdeki Mavi, Turuncu, Yeşil ve 4. olarak Kırmızı
    new_palette = {
        'Earth (E)': '#D62728',  # Kırmızı (Vurgu)
        'Q-Object':  '#1F77B4',  # Mavi
        'U-Object':  '#FF7F0E',  # Turuncu
        'J-Object':  '#2CA02C'   # Yeşil
    }
    
    ax = sns.stripplot(
        data=df,
        x='Match',
        y='Distance',
        hue='Object Type',
        dodge=True,
        jitter=0,                    
        s=8,
        marker='D',
        palette=new_palette 
    )
    
    # Başlıklar ve etiketler
    # Başlığı ve Eksenleri güncelledim
    ax.set_xlabel('Match ID', fontsize=14)
    ax.set_ylabel('Distance (AU)', fontsize=14) # 'Distance (AU)' değil, 'object_dist' olmalı
    
    # Y eksenini 0'dan başlat
    ax.set_ylim(bottom=0)
    
    # Efsaneyi (Legend) grafiğin dışına taşı
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    # --- GÜNCELLEME v18: Y-EKSENİ (TICK) AYARLARI ---
    
    # 1. Ana (Major) aralıkları her 0.5'te bir ayarla (0, 0.5, 1.0, 1.5...)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    
    # 2. Ara (Minor) aralıkları her 0.1'de bir ayarla (1.1, 1.2...)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    
    # 3. Ana (Major) grid çizgilerini ayarla (beyaz arka planda)
    ax.yaxis.grid(True, which='major', linestyle='--', linewidth=0.7, color='gray', alpha=0.9)
    
    # 4. Ara (Minor) grid çizgilerini etkinleştir (çok daha soluk)
    #    Bu, senin 1.1, 1.2, 1.3... çizgilerini ekleyecek
    ax.yaxis.grid(True, which='minor', linestyle=':', linewidth=0.5, color='gray', alpha=0.5)
    
    # X eksenindeki "Match 1" vb. grid'ini (dikey) kapat
    ax.xaxis.grid(False) 
    
    # --- v17 Panel Çizgileri (Bu kalacak) ---
    line_positions = [i + 0.5 for i in range(7)] 
    for pos in line_positions:
        ax.axvline(pos, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    plt.tight_layout()

    # --- Dosyaya Kaydetme (PNG ve PDF) ---
    output_filename_png = 'Plot_3b_AU_Jump_Profile_Panel_v18.png' 
    output_filename_pdf = 'Plot_3b_AU_Jump_Profile_Panel_v18.pdf' 
    
    try:
        plt.savefig(output_filename_png, dpi=300, bbox_inches='tight')
        print(f"\nSuccess! Plot saved as '{output_filename_png}'.")
    except Exception as e:
        print(f"\n!!! ERROR: Failed to save PNG file: {e}")
        
    try:
        plt.savefig(output_filename_pdf, dpi=300, bbox_inches='tight')
        print(f"Success! Plot saved as '{output_filename_pdf}'.")
    except Exception as e:
        print(f"\n!!! ERROR: Failed to save PDF file: {e}")

    plt.show()


# --- 4. ANA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    
    # 1. Veritabanından 8 eşleşmenin verisini çek
    final_df = fetch_top_8_matches(DB_DOSYA_YOLU, DB_TABLO_ADI, SORTING_COLUMN)
    
    # 2. Grafiği oluştur
    create_jump_profile_plot(final_df)