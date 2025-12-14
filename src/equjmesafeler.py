# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 09:56:04 2025

@author: olgub
"""

# ... (importlar aynı kalacak: pandas, sqlite3, os, time) ...
from google.colab import drive
drive.mount('/content/drive') # Google Drive'ı Colab'a bağla

import pandas as pd
import sqlite3
import os
import time 
# import math # Bu scriptte math kullanmıyoruz, ama kalabilir
# import re # Bu scriptte re kullanmıyoruz, ama kalabilir

# ===== KULLANICI AYARLARI =====
BASE_FOLDER_PATH = "/content/drive/MyDrive/UzayliBulmacaKlasoru" 

# === DEĞİŞİKLİK BURADA ===
DB_FILE_NAME = "solar_system_analysis_with_distances.db" # SENİN VERDİĞİN DOSYA ADI
# ==========================

DB_FILE_PATH = os.path.join(BASE_FOLDER_PATH, DB_FILE_NAME)
TARGET_DATE_FOR_COL_NAME = "19770815" 
# ==============================

# Veritabanındaki anlık uzaklık sütununun tam adı
INSTANT_DIST_COL_DB = f"instant_sun_dist_au_{TARGET_DATE_FOR_COL_NAME}"

# fetch_valid_distances_from_db, create_and_populate_diff_table 
# fonksiyonlarının TANIMLARI BİR ÖNCEKİ KODDAKİ GİBİ AYNI KALACAK.
# ... (fonksiyon tanımlarını buraya kopyala veya bir önceki koddan al) ...
# Sadece __main__ bloğunu aşağıya ekliyorum:

def fetch_valid_distances_from_db(conn, letter):
    """
    Belirli bir harfe ait cisimlerin adlarını, kategorilerini ve geçerli 
    (NULL olmayan) anlık Güneş uzaklıklarını veritabanından çeker.
    """
    cursor = conn.cursor()
    query = f"""
    SELECT object_name, category, {INSTANT_DIST_COL_DB}
    FROM celestial_objects
    WHERE source_letter = ? 
      AND {INSTANT_DIST_COL_DB} IS NOT NULL 
      AND category IN ('Asteroid', 'Planet', 'Natural Satellite', 'Dwarf Planet', 'Artificial Satellite')
    """
    cursor.execute(query, (letter.upper(),))
    results = [{"name": row[0], "category": row[1], "dist": row[2]} for row in cursor.fetchall()]
    print(f"'{letter}' harfi için veritabanından {len(results)} adet geçerli uzaklık verisi çekildi.")
    return results

def create_and_populate_diff_table(conn, list1, list2, table_name_suffix, letter1_char, letter2_char):
    """
    İki cisim listesi arasındaki tüm uzaklık farklarını hesaplar
    ve bunları veritabanında yeni bir tabloya yazar.
    """
    table_name = f"distance_differences{table_name_suffix}"
    col_obj1_name = f"{letter1_char.lower()}_object_name"
    col_obj1_cat = f"{letter1_char.lower()}_object_category"
    col_obj1_dist = f"{letter1_char.lower()}_object_dist"
    col_obj2_name = f"{letter2_char.lower()}_object_name"
    col_obj2_cat = f"{letter2_char.lower()}_object_category"
    col_obj2_dist = f"{letter2_char.lower()}_object_dist"

    cursor = conn.cursor()
    print(f"\n'{table_name}' tablosu hazırlanıyor...")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
    CREATE TABLE {table_name} (
        {col_obj1_name} TEXT, {col_obj1_cat} TEXT, {col_obj1_dist} REAL,
        {col_obj2_name} TEXT, {col_obj2_cat} TEXT, {col_obj2_dist} REAL,
        abs_distance_difference_au REAL
    )""")
    conn.commit()
    print(f"'{table_name}' tablosu oluşturuldu (veya sıfırlandı).")

    if not list1 or not list2:
        print(f"  '{table_name_suffix}' için listelerden biri boş, fark tablosu boş kalacak.")
        return

    total_combinations = len(list1) * len(list2)
    print(f"  '{table_name_suffix}' için {total_combinations:,} uzaklık farkı hesaplanıp tabloya eklenecek...")
    count = 0
    milestone_step = max(1, total_combinations // 20) if total_combinations > 0 else 1 
    data_to_insert = []
    for item1 in list1:
        for item2 in list2:
            abs_diff = abs(item1["dist"] - item2["dist"])
            data_to_insert.append((
                item1["name"], item1["category"], item1["dist"],
                item2["name"], item2["category"], item2["dist"], abs_diff))
            count += 1
            if total_combinations > 5000 and count % milestone_step == 0:
                 print(f"    {table_name_suffix} farkları: {count}/{total_combinations} ({count*100/total_combinations:.0f}%) hesaplandı...")
    if data_to_insert:
        sql_insert = f"""
        INSERT INTO {table_name} (
            {col_obj1_name}, {col_obj1_cat}, {col_obj1_dist},
            {col_obj2_name}, {col_obj2_cat}, {col_obj2_dist},
            abs_distance_difference_au
        ) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.executemany(sql_insert, data_to_insert)
        conn.commit()
    print(f"  '{table_name}' tablosuna {count} kayıt eklendi.")

if __name__ == "__main__":
    if not os.path.exists(DB_FILE_PATH):
        print(f"HATA: Veritabanı dosyası '{DB_FILE_PATH}' bulunamadı. Lütfen önce Excel'den veri aktarma script'ini çalıştırın ve dosya adının doğru olduğundan emin olun.")
    else:
        conn = sqlite3.connect(DB_FILE_PATH)
        start_time_total = time.time()

        print("E harfi için veriler çekiliyor...")
        e_objects_with_dist = fetch_valid_distances_from_db(conn, "E")
        print("Q harfi için veriler çekiliyor...")
        q_objects_with_dist = fetch_valid_distances_from_db(conn, "Q")
        
        if e_objects_with_dist and q_objects_with_dist:
            create_and_populate_diff_table(conn, e_objects_with_dist, q_objects_with_dist, "_EQ", "E", "Q")
        else:
            print("E veya Q harfi için yeterli veri bulunamadı, E-Q farkları tablosu oluşturulamıyor/boş olacak.")

        print("\nU harfi için veriler çekiliyor...")
        u_objects_with_dist = fetch_valid_distances_from_db(conn, "U")
        print("J harfi için veriler çekiliyor...")
        j_objects_with_dist = fetch_valid_distances_from_db(conn, "J")

        if u_objects_with_dist and j_objects_with_dist:
            create_and_populate_diff_table(conn, u_objects_with_dist, j_objects_with_dist, "_UJ", "U", "J")
        else:
            print("U veya J harfi için yeterli veri bulunamadı, U-J farkları tablosu oluşturulamıyor/boş olacak.")

        conn.close()
        end_time_total = time.time()
        print(f"\nİlk aşama (fark tabloları oluşturma) tamamlandı. Toplam süre: {(end_time_total - start_time_total):.2f} saniye.")
        print(f"Sonuçlar '{DB_FILE_PATH}' içindeki 'distance_differences_EQ' ve 'distance_differences_UJ' tablolarına kaydedildi.")