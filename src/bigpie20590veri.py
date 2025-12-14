# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 10:04:51 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 20:25:31 2025
@author: olgub

v_Pie_Analysis:
- Bu kod bir grafik ÇİZMEZ.
- Veritabanına bağlanır, "Top 8" ("İnciler") listesini bulur.
- Geri kalan 20.582 veriyi ("Okyanus") ayırır.
- "Okyanus" verisinin istatistiksel dökümünü (Min, Max, Medyan, Yüzdelikler)
  hesaplar ve Pie Chart tasarımı için öneriler sunar.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from io import StringIO # Gerekli değil ama iyi pratiktir

print("Pie Chart Analiz Motoru (Veri Toplama) başlatılıyor...")

# --- 1. Veritabanı ve Eşleşme Listesi Ayarları ---
db_path = r'C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy\solar_system_analysis_with_distances.db'
table_name = 'focused_meta_comparison_results'
column_to_analyze = 'percentage_diff_of_5uj'

# Bizim "Top 8" (k=1) Eşleşme Listemiz (Q, U, J sırasıyla)
k1_matches_list = [
    ('364192', '4716', '13441'),      # Eşleşme 1
    ('9588', '4257', '17195'),        # Eşleşme 2
    ('52301', '4632', '58424'),       # Eşleşme 3
    ('3513', '55701', '5255'),        # Eşleşme 4
    ('26940', '19462', '84011'),      # Eşleşme 5
    ('52301', '15025', '30030'),      # Eşleşme 6 (Qumran tekrar)
    ('2255', '233880', '101811'),     # Eşleşme 7
    ('17438', '16515', '33889')       # Eşleşme 8
]

# Veritabanı dosyasının varlığını kontrol et
if not os.path.exists(db_path):
    print(f"HATA: Veritabanı dosyası bulunamadı. Kontrol edilen yol: {db_path}")
else:
    print(f"Veritabanı bulundu: {db_path}")
    conn = None
    try:
        # --- 2. Veri Çekme ---
        conn = sqlite3.connect(db_path)
        print(f"'{table_name}' tablosuna bağlanıldı.")

        # Adım 1: "Okyanus" verisini çek (Tüm 20,590+ aday)
        print("Adım 1: 'Okyanus' (tüm adaylar) verisi çekiliyor...")
        query_ocean = f"SELECT {column_to_analyze} FROM {table_name}"
        df_ocean = pd.read_sql_query(query_ocean, conn)
        ocean_data = df_ocean[column_to_analyze].dropna()
        total_count = len(ocean_data)
        print(f"-> Toplam {total_count} adet '% sapma' değeri bulundu.")

        # Adım 2: "İnciler" verisini çek (Bizim Top 8)
        print("Adım 2: 'İnciler' (Bizim Top 8) verisi aranıyor...")
        pearl_data = []
        base_query = f"""
            SELECT {column_to_analyze} 
            FROM {table_name} 
            WHERE 
                q_object_name LIKE ? AND 
                u_object_name LIKE ? AND 
                j_object_name LIKE ?
        """
        cursor = conn.cursor()
        
        for i, (q, u, j) in enumerate(k1_matches_list):
            q_like = f"{q}%"
            u_like = f"{u}%"
            j_like = f"{j}%"
            
            cursor.execute(base_query, (q_like, u_like, j_like))
            result = cursor.fetchone()
            
            if result:
                pearl_data.append(result[0])
                print(f"  -> Eşleşme {i+1} ({q}...) bulundu! Sapma: {result[0]}")
            else:
                print(f"  -> UYARI: Eşleşme {i+1} ({q}...) veritabanında bulunamadı.")
        
        print(f"-> {len(pearl_data)} adet 'Top 8' eşleşme verisi başarıyla çekildi.")

        # --- 3. Veri Ayırma ve İstatistiksel Analiz ---
        print("\nAdım 3: Veri ayırma ve istatistiksel analiz yapılıyor...")
        
        # "İnciler" (Top 8) Analizi
        # 'set' kullanarak olası dublikatları (örn 52301) temizle
        sorted_pearls = sorted(list(set(pearl_data))) 
        print("\n--- 'İnciler' (Top 8) Analizi ---")
        print(f"{len(sorted_pearls)} adet EŞSİZ 'İnci' bulundu (Pie Chart Dilimleri):")
        for i, val in enumerate(sorted_pearls):
            # Değerleri yüksek hassasiyetle yazdır
            print(f"  İnci {i+1}: {val:.10f}%") 

        # "Okyanus" (Kalanlar) Analizi
        # Tüm veriden (ocean_data) inci verilerini (pearl_data) çıkar
        ocean_data_remaining = ocean_data[~ocean_data.isin(pearl_data)]
        remaining_count = len(ocean_data_remaining)
        
        print(f"\n--- 'Okyanus' (Kalan {remaining_count}) Analizi ---")
        
        if not ocean_data_remaining.empty:
            # İstenen yüzdelik dilimleri hesapla
            stats = ocean_data_remaining.describe(percentiles=[.5, .75, .90, .95])
            
            print(f"  En Küçük (Min): {stats['min']:.10f}%")
            print(f"  Ortalama (Mean): {stats['mean']:.10f}%")
            print(f"  Tam Ortası (Median / 50%): {stats['50%']:.10f}%")
            print(f"  75. Yüzdelik Dilim: {stats['75%']:.10f}%")
            print(f"  90. Yüzdelik Dilim: {stats['90%']:.10f}%")
            print(f"  95. Yüzdelik Dilim: {stats['95%']:.10f}%")
            print(f"  En Büyük (Max): {stats['max']:.10f}%")
            
            print("\nPie Chart Grupları için Fikir/Öneri:")
            print("====================================")
            print("Veri bu istatistiklere göre gruplanabilir:")
            print(f"Dilim 1-{len(sorted_pearls)}: 'Top {len(sorted_pearls)}' (her biri ayrı, < {stats['min']:.10f}%)")
            print(f"Dilim {len(sorted_pearls)+1}: '{stats['min']:.3f}% - {stats['50%']:.3f}%' (Kalanların ~%50'si)")
            print(f"Dilim {len(sorted_pearls)+2}: '{stats['50%']:.3f}% - {stats['75%']:.3f}%' (Kalanların ~%25'i)")
            print(f"Dilim {len(sorted_pearls)+3}: '{stats['75%']:.3f}% - {stats['95%']:.3f}%' (Kalanların ~%20'si)")
            print(f"Dilim {len(sorted_pearls)+4}: '> {stats['95%']:.3f}%' (Kalanların ~%5'i)")
            
        else:
            print("HATA: Kalan 'Okyanus' verisi boş.")

    except sqlite3.Error as e:
        print(f"SQLite HATA: {e}")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")
    finally:
        if conn:
            conn.close()
            print("\nVeritabanı bağlantısı kapatıldı.")