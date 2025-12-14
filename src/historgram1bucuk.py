import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3
import os

print("Grafik 3.1 (Matematiksel Kanıt - Histogram) motoru başlatılıyor...")

# --- 1. Veritabanı ve Eşleşme Listesi Ayarları ---

db_path = r'C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy\solar_system_analysis_with_distances.db'
table_name = 'focused_meta_comparison_results'
column_to_plot = 'percentage_diff_of_5uj'

# Bizim "Top 8" (k=1) Eşleşme Listemiz (Q, U, J sırasıyla)
k1_matches_list = [
    ('364192', '4716', '13441'),      # Eşleşme 1
    ('9588', '4257', '17195'),        # Eşleşme 2
    ('52301', '4632', '58424'),        # Eşleşme 3
    ('3513', '55701', '5255'),         # Eşleşme 4
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
        query_ocean = f"SELECT {column_to_plot} FROM {table_name}"
        df_ocean = pd.read_sql_query(query_ocean, conn)
        ocean_data = df_ocean[column_to_plot].dropna()
        print(f"-> {len(ocean_data)} adet '% sapma' değeri bulundu.")

        # Adım 2: "İnciler" verisini çek (Bizim Top 8)
        print("Adım 2: 'İnciler' (Bizim Top 8) verisi aranıyor...")
        pearl_data = []
        base_query = f"""
            SELECT {column_to_plot} 
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
                print(f"  -> Eşleşme {i+1} ({q}...) bulundu! Sapma: {result[0]:.6f}")
            else:
                print(f"  -> UYARI: Eşleşme {i+1} ({q}...) veritabanında bulunamadı.")
        
        print(f"-> {len(pearl_data)} adet 'Top 8' eşleşme verisi başarıyla çekildi.")

        # --- 3. Histogramı Çizme ---
        if not ocean_data.empty:
            print("Adım 3: Histogram oluşturuluyor (Logaritmik Ölçek)...")
            plt.figure(figsize=(14, 8))
            
            ocean_data_positive = ocean_data[ocean_data > 0]
            if ocean_data_positive.empty:
                print("HATA: Çizilecek pozitif veri yok.")
            else:
                min_val = ocean_data_positive.min()
                max_val = ocean_data_positive.max()
                
                logbins = np.logspace(np.log10(min_val), np.log10(max_val), 100)
                
                # Katman 1: "Okyanus" (Tüm adaylar)
                plt.hist(ocean_data_positive, bins=logbins, alpha=0.8, 
                         label=f"Other 20,582 Matches (n={len(ocean_data_positive)})", 
                         color='#483D8B') # Koyu Lacivert/Indigo (DarkSlateBlue)
                
                # Katman 2: "İnciler" (Bizim Top 8)
                if pearl_data:
                    sorted_pearls = sorted(pearl_data)
                    i = 0
                    label_added = False 
                    
                    print("Adım 3a: 'İnciler' (Top 8) 'yayma metodu' ile çiziliyor ve değerler yazılıyor...")
                    
                    while i < len(sorted_pearls):
                        val = sorted_pearls[i]
                        label = f"k=1 Matched Objects (n=8)" if not label_added else ""
                        
                        # Küme (cluster) kontrolü
                        if (i + 1 < len(sorted_pearls)) and (sorted_pearls[i+1] / val < 1.001): 
                            val1 = sorted_pearls[i]
                            val2 = sorted_pearls[i+1]
                            print(f"  -> Küme bulundu! {val1:.6f} ve {val2:.6f} yayılıyor...")
                            
                            jitter_factor_left = 0.995 
                            jitter_factor_right = 1.005 

                            plt.axvline(val1 * jitter_factor_left, color='#E24A33', linestyle='--', linewidth=2, label=label, alpha=0.8)
                            label_added = True 
                            plt.axvline(val2 * jitter_factor_right, color='#E24A33', linestyle='--', linewidth=2, alpha=0.8) 
                            
                            current_ylim = plt.ylim()
                            text_y_pos = 10**(np.log10(current_ylim[1]) * 0.9) 
                            
                            plt.text(val1 * jitter_factor_left, text_y_pos, f"{val1:.5f}", 
                                     color='#E24A33', fontsize=8, ha='right', va='center', rotation=90, alpha=0.9)
                            plt.text(val2 * jitter_factor_right, text_y_pos, f"{val2:.5f}", 
                                     color='#E24A33', fontsize=8, ha='left', va='center', rotation=90, alpha=0.9)
                            
                            i += 2 
                        else:
                            plt.axvline(val, color='#E24A33', linestyle='--', linewidth=2, label=label, alpha=0.8)
                            label_added = True 
                            i += 1
                
                # --- 4. Estetik Ayarlar ---
                plt.xscale('log') 
                plt.yscale('log') 
                
                # Başlıklar
                plt.xlabel('% Percentage Deviation - Logarithmic Scale', fontsize=12)
                plt.ylabel('Object Formula Matched Number - Logarithmic Scale', fontsize=12)
                
                plt.legend()
                plt.grid(True, which="both", ls="--", alpha=0.5)
                
                # === Dosyaya Kaydetme (PNG ve PDF) ===
                
                png_filename = 'Grafik_3_1_Matematiksel_Kanit_Histogram.png'
                pdf_filename = 'Grafik_3_1_Matematiksel_Kanit_Histogram.pdf' # PDF dosyası
                files_saved = 0
                
                try:
                    plt.savefig(png_filename, dpi=300)
                    print(f"'{png_filename}' başarıyla kaydedildi.")
                    files_saved += 1
                except PermissionError:
                    print(f"HATA: '{png_filename}' kaydedilemedi. Dosya başka bir programda açık olabilir.")
                except Exception as e:
                    print(f"'{png_filename}' kaydedilirken beklenmedik bir hata oluştu: {e}")
                
                try:
                    plt.savefig(pdf_filename, dpi=300) # PDF olarak kaydet
                    print(f"'{pdf_filename}' başarıyla kaydedildi.")
                    files_saved += 1
                except PermissionError:
                    print(f"HATA: '{pdf_filename}' kaydedilemedi. Dosya başka bir programda açık olabilir (Adobe, Chrome vb.).")
                except Exception as e:
                    print(f"'{pdf_filename}' kaydedilirken beklenmedik bir hata oluştu: {e}")

                if files_saved == 2:
                    print("\nGrafikler başarıyla oluşturuldu ve PNG/PDF olarak kaydedildi.")
                else:
                    print("\nGrafik kaydetme işlemi tamamlandı (bazı hatalarla).")
                
                # plt.show() 

        else:
            print("HATA: Veritabanından veri çekilemedi, histogram çizilemiyor.")

    except sqlite3.Error as e:
        print(f"SQLite HATA: {e}")
    except Exception as e:
            print(f"Beklenmedik bir hata oluştu: {e}")
    finally:
        if conn:
            conn.close()
            print("Veritabanı bağlantısı kapatıldı.")