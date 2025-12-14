# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 14:22:31 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 14:30:00 2025
@author: olgub

--- UZAYLI BULMACASI ODAKLANMIŞ MOTORU (v4.6 - Trojan-Kentaur Analizi) ---
AMAÇ: Belirlenen 6 Jüpiter Trojanı (veya benzeri) cisimden,
      '32532 Thereus' (Kentaur) hedefine olan spesifik "serbest uçuş"
      maliyetlerini hesaplamak ve veritabanına sadece bu 6 rotayı yazmak.
"""

import sqlite3
import time
import numpy as np  # np.float64 verisi için eklendi

# --- KULLICI AYARLARI VE VERİ GİRİŞİ ---
WEIGHTS = { 'wa': 1.0, 'we': 5.0, 'wi': 10.0, 'wT': 2.0 }
DB_FILE_NAME = "uzayli_bulmacasi_matrix.db" # Aynı DB dosyasını kullanıyoruz

# === v4.6 ODAKLANMIŞ 7 CİSİMLİK VERİTABANI ===
# Sadece analizi istenen 7 cismi içerir.
ASTEROID_DB = {
    # --- 6 Kaynak Cisim (Trojanlar ve benzerleri) ---
    '84011 Jean-Claude (2002 OB25)': {'a': 4.0092, 'e': 0.2464, 'i': 4.0115, 'T_J': 2.995},
    '55701 Ukalegon (1193 T-3)': {'a': 5.1658, 'e': 0.1408, 'i': 20.9572, 'T_J': 2.850},
    '169509 Jeffreyrobbins (2002 CV269)': {
        'T_J': 2.998,
        'a': np.float64(3.961324811124834),
        'e': 0.2555376257109717,
        'i': np.float64(3.328394895579154)
    },
    '25869 Jacoby (2000 JP70)': {'a': 3.9830, 'e': 0.1448, 'i': 16.9648, 'T_J': 2.962},
    '306001 Joanllaneras (2009 TD42)': {'a': 5.2502, 'e': 0.1542, 'i': 10.1184, 'T_J': 2.945},
    '5254 Ulysses (1986 V61)': {'a': 5.2213, 'e': 0.1212, 'i': 24.2002, 'T_J': 2.810},

    # --- 1 Hedef Cisim (Kentaur) ---
    '32532 Thereus (2001 PT13)': {
        'T_J': 3.117,
        'a': np.float64(10.63837380077479),
        'e': 0.1975930743332117,
        'i': np.float64(20.36740974623941)
    }
}
# ==================================


# --- ANALİZ MOTORU KODU ---

def calculate_cost(id1, id2, weights):
    """
    İki cisim ID'si arasında, verilen ağırlıklara göre maliyeti hesaplar.
    """
    if id1 not in ASTEROID_DB:
        print(f"HATA: {id1} ASTEROID_DB'de bulunamadı!")
        return float('inf')
    if id2 not in ASTEROID_DB:
        print(f"HATA: {id2} ASTEROID_DB'de bulunamadı!")
        return float('inf')
        
    p1, p2 = ASTEROID_DB[id1], ASTEROID_DB[id2]
    
    # Hata ayıklama için değerleri float'a çevir
    try:
        cost = (weights['wa'] * abs(float(p1['a']) - float(p2['a'])) +
                weights['we'] * abs(float(p1['e']) - float(p2['e'])) +
                weights['wi'] * abs(float(p1['i']) - float(p2['i'])) +
                weights['wT'] * abs(float(p1['T_J']) - float(p2['T_J'])))
        return cost
    except Exception as e:
        print(f"Hesaplama hatası ({id1} -> {id2}): {e}")
        return float('inf')

# Dijkstra ve Metro Haritası fonksiyonları bu odaklanmış
# analiz için gerekli olmadığından kaldırıldı.

def main():
    print(f"Uzaylı Bulmacası Motoru (v4.6 - Odaklanmış Trojan->Kentaur Analizi)...")
    print(f"Veritabanı dosyası '{DB_FILE_NAME}' güncellenecek...")

    # --- HESAPLAMA LİSTESİ ---
    # Sadece bu 6 rota hesaplanacak
    target_asteroid = '32532 Thereus (2001 PT13)'
    source_asteroids = [
        '84011 Jean-Claude (2002 OB25)',
        '55701 Ukalegon (1193 T-3)',
        '169509 Jeffreyrobbins (2002 CV269)',
        '25869 Jacoby (2000 JP70)',
        '306001 Joanllaneras (2009 TD42)',
        '5254 Ulysses (1986 V61)'
    ]
    # ---------------------------

    data_to_insert = []
    print(f"\nHedef: {target_asteroid}")
    print("Maliyetler hesaplanıyor...")
    
    start_time = time.time()

    # 1. Manuel olarak 6 maliyeti hesapla
    for from_ast in source_asteroids:
        # DB'de olup olmadıklarını kontrol et
        if from_ast not in ASTEROID_DB or target_asteroid not in ASTEROID_DB:
            print(f"HATA: '{from_ast}' veya '{target_asteroid}' DB'de bulunamadı. Atlanıyor.")
            continue
            
        cost = calculate_cost(from_ast, target_asteroid, WEIGHTS)
        data_to_insert.append((from_ast, target_asteroid, cost))
        
        # === KONSOL ÇIKTISI ===
        # Sonucu hemen konsola yazdır
        print(f"  -> {from_ast:<38}  Maliyet: {cost:<10.4f}")
        
    calc_time = time.time()
    print(f"\n{len(data_to_insert)} maliyet {calc_time - start_time:.4f} saniyede hesaplandı.")

    # 2. Veritabanı işlemlerini yap
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()

        # Tablonun var olduğundan emin ol (yoksa oluştur)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CostMatrix (
            From_Asteroid TEXT,
            To_Asteroid TEXT,
            Cost REAL,
            PRIMARY KEY (From_Asteroid, To_Asteroid)
        )
        """)
        
        # === KRİTİK ADIM ===
        # Eski matris verilerini (13.000+ satır olabilir) temizle
        print("Veritabanındaki eski veriler siliniyor...")
        cursor.execute("DELETE FROM CostMatrix")
        
        # Yeni 6 satırlık veriyi topluca ekle
        print(f"{len(data_to_insert)} satır veritabanına yazılıyor...")
        cursor.executemany("INSERT INTO CostMatrix (From_Asteroid, To_Asteroid, Cost) VALUES (?, ?, ?)", data_to_insert)
        
        conn.commit()
        
        end_time = time.time()
        print("\n" + "="*30)
        print("İŞLEM TAMAMLANDI")
        print(f"'{DB_FILE_NAME}' başarıyla güncellendi.")
        print("Veritabanı artık SADECE bu 6 rotayı içermektedir.")
        print(f"Toplam süre: {end_time - start_time:.4f} saniye.")
        print("="*30)

    except sqlite3.Error as e:
        print(f"SQLite hatası oluştu: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()