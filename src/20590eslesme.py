import sqlite3
import json
import sys
import os

# --- AYARLAR ---

# Veritabanı dosyasının tam yolu
db_path = r'C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy\solar_system_analysis_with_distances.db'

# Çıktı .txt dosyasının adı (kodun çalıştığı dizine kaydeder)
output_txt_path = 'eslesme_sonuclari.txt'

# Veritabanı ve sorgu detayları
table_name = 'focused_meta_comparison_results'
sort_column = 'percentage_diff_of_5uj'

# --- DÜZELTME BURADA YAPILDI ---
# Sütun adı 'q_object_nmae' yerine 'q_object_name' olarak güncellendi.
columns_to_select = ['earth_object_name', 'q_object_name', 'u_object_name', 'j_object_name']

# --- AYARLAR SONU ---


def check_db_exists(path):
    """Veritabanı dosyasının var olup olmadığını kontrol eder."""
    if not os.path.exists(path):
        print(f"--- HATA ---")
        print(f"Veritabanı dosyası bulunamadı!")
        print(f"Aranan yol: {path}")
        print("Lütfen koddaki 'db_path' değişkenini kontrol et.")
        return False
    return True

def run_query():
    """Veritabanı sorgusunu çalıştırır ve sonuçları formatlar."""
    
    if not check_db_exists(db_path):
        sys.exit() # Dosya yoksa programı durdur

    print(f"Veritabanına bağlanılıyor: {db_path}")
    
    # SQL sorgusunu dinamik olarak oluşturalım
    sql_query = f"""
    SELECT {', '.join(columns_to_select)}
    FROM {table_name}
    ORDER BY {sort_column} ASC
    """
    
    results_dict = {}
    conn = None  # Bağlantıyı 'finally' bloğunda kapatabilmek için dışarıda tanımla
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Sorgu çalıştırılıyor (Bu işlem veri büyüklüğüne göre zaman alabilir)...")
        cursor.execute(sql_query)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("Veritabanında hiç veri bulunamadı.")
            return  # Veri yoksa fonksiyondan çık
            
        print(f"Toplam {len(rows)} eşleşme bulundu. Formatlanıyor...")
        
        # Tüm veriyi istenen sözlük yapısına dök
        for index, row in enumerate(rows, start=1):
            data_list = list(row)  # Gelen tuple'ı listeye çevir
            match_key = f"Eşleşme {index}"
            option_key = f"Seçenek {index}A"
            results_dict[match_key] = {option_key: data_list}
            
    except sqlite3.Error as e:
        print(f"--- SQLite Hatası ---: {e}")
        # Hata devam ederse ipucu ver
        if "no such column" in str(e):
             print("\n*** HATA İPUCU ***")
             print(f"Sorgu '{e}' hatası verdi.")
             print(f"'columns_to_select' listesindeki ({columns_to_select}) bir sütun adı")
             print(f"({table_name}) tablosunda bulunamadı.")
             print("Lütfen DB dosyasını (DB Browser gibi) bir araçla açıp sütun adlarını tekrar kontrol et.")
             print("*****************\n")
        sys.exit()  # Hata varsa programı durdur
        
    finally:
        if conn:
            conn.close()
            print("Veritabanı bağlantısı kapatıldı.")
            
    if not results_dict:
        print("İşlenecek sonuç bulunamadı.")
        return

    # --- 1. Konsol Çıktısı (İlk 10) ---
    print("\n--- Konsol Çıktısı (İlk 10 Eşleşme) ---")
    count = 0
    for key, value in results_dict.items():
        if count >= 10:
            break
        # json.dumps ile güzel formatlama ve Türkçe karakter desteği (ensure_ascii=False)
        line = f'"{key}": {json.dumps(value, ensure_ascii=False)},'
        print(line)
        count += 1
    if len(results_dict) > 10:
        print("... (devamı dosyada)")
    print("------------------------------------------\n")
    
    # --- 2. Dosya Çıktısı (Tümü) ---
    print(f"Tüm {len(results_dict)} eşleşme '{output_txt_path}' dosyasına yazdırılıyor...")
    
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            # Tüm sözlüğü tek seferde, güzel formatlanmış (indent=4) 
            # ve Türkçe karakter destekli (ensure_ascii=False) JSON olarak yaz.
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
            
        print(f"İşlem tamamlandı. Dosya kaydedildi: {output_txt_path}")
        
    except IOError as e:
        print(f"--- Dosya Yazma Hatası ---: {e}")

# Ana programı çalıştır
if __name__ == "__main__":
    run_query()