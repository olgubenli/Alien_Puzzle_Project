# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 14:06:23 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 14:00:00 2025

@author: olgub

İstenen İki Cisim için (Jeffreyrobbins & Thereus)
JPL SBDB'den Veri Çekme Scripti.
"""

import json
import time
import pprint  # Güzel çıktı için
from astroquery.jplsbdb import SBDB

def to_float(x, unit=None):
    """Astropy Quantity / str / float -> float (opsiyonel birim dönüştürme ile)."""
    try:
        # Astropy Quantity ise
        if hasattr(x, 'to'):
            return x.to(unit).value if unit else x.value
        # str ise
        if isinstance(x, str):
            return float(x.strip())
        # zaten sayısal ise
        return float(x)
    except Exception:
        return None

def fetch_asteroid_data(ast_name):
    """
    NASA JPL SBDB'den tek bir cismin yörünge parametrelerini çeker.
    (Senin kodundan kopyalandı)
    """
    try:
        sbdb = SBDB.query(ast_name, full_precision=True)

        orbit = sbdb.get('orbit')
        if not orbit:
            print(f"     -> HATA: '{ast_name}' için 'orbit' verisi bulunamadı.")
            return None

        elems = orbit.get('elements', {})
        if not elems:
            print(f"     -> HATA: '{ast_name}' için 'elements' verisi bulunamadı.")
            return None

        a = to_float(elems.get('a'), unit='AU')  # yarı-büyük eksen (AU)
        e = to_float(elems.get('e'))  # dışmerkezlik (birimsiz)
        i = to_float(elems.get('i'))  # eğim (deg)
        t_jup_raw = orbit.get('t_jup')  # Jüpiter Tisserand
        T_J = to_float(t_jup_raw) if t_jup_raw is not None else None

        if a is None:
            print(f"     -> HATA: '{ast_name}' için 'a' değeri alınamadı.")
            return None

        print(f"     -> BAŞARILI: '{ast_name}' için veri çekildi.")
        return {'a': a, 'e': e, 'i': i, 'T_J': T_J}

    except Exception as e:
        print(f"     -> HATA: '{ast_name}' sorgulanırken hata oluştu: {e}")
        return None

def main():
    print("--- JPL SBDB Veri Çekme (Sadece 2 Hedef Cisim) ---")
    
    # Sadece bu iki cismi sorgulayacağız
    target_list = [
        "169509 Jeffreyrobbins (2002 CV269)",
        "32532 Thereus (2001 PT13)"
    ]
    
    # Çıktı dosyası adı
    OUTPUT_JSON = "iki_cisim_db.json"
    
    new_asteroid_db = {}
    # Konsola güzel basmak için pretty-printer
    pp = pprint.PrettyPrinter(indent=4)

    print(f"Toplam {len(target_list)} hedef cisim için sorgulama başlıyor...\n")

    for ast_name_raw in target_list:
        print(f"İşleniyor: '{ast_name_raw}'")

        # Orijinal script'teki isim temizleme mantığını uygula
        # (Parantez içindeki kısmı at)
        if '(' in ast_name_raw and not ast_name_raw.startswith(('C/', 'P/')):
            search_name = ast_name_raw.split('(')[0].strip()
            print(f"     (Sorgu için temizlendi: '{search_name}')")
        else:
            search_name = ast_name_raw
        
        # Veriyi çek
        data = fetch_asteroid_data(search_name)
        time.sleep(0.1) # API'ye nazik davran

        if data:
            # Veritabanına orijinal, tam adıyla kaydet
            new_asteroid_db[ast_name_raw] = data
        
        print("-" * 20)
    
    print("\n--- Sorgulama Tamamlandı ---")

    if not new_asteroid_db:
        print("Hiçbir cisim için veri alınamadı.")
        return

    # --- 1. İsteğin: Konsola Çıktı Ver ---
    print("\n✅ KONSOL ÇIKTISI (Veritabanı İçeriği):")
    pp.pprint(new_asteroid_db)
    
    # --- 2. İsteğin: Yeni .db (JSON) Dosyası Oluştur ---
    print(f"\nJSON dosyası oluşturuluyor: {OUTPUT_JSON}")
    try:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(new_asteroid_db, f, indent=4, ensure_ascii=False)
        print(f"✅ BAŞARILI: JSON kaydedildi -> {OUTPUT_JSON}")
    except Exception as e:
        print(f"❌ HATA: JSON yazılırken hata oluştu: {e}")

if __name__ == "__main__":
    main()