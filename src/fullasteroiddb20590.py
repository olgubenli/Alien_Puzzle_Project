# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 17:18:11 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 5 13:30:00 2025

@author: olgub

UZAYLI BULMACASI - GENİŞ VERİ TOPLAMA MOTORU (20590 Eşleşme)

Bu script, 'eslesme_sonuclari 20590.txt' adlı BÜYÜK metin dosyasını okur.
Dosyanın tam bir JSON olmadığını varsayarak, içindeki cisim isimlerini
Regex (Regular Expressions) kullanarak "avlar".
Bulunan tüm benzersiz cisimler için NASA JPL SBDB'den yörünge parametrelerini
çeker ve iki ayrı formatta kaydeder:
1. genisletilmis_asteroid_db2.json (Standart JSON)
2. fullasteroiddb20590.txt (Python sözlüğü formatında TXT)
"""

import json
import time
import re  # Regex kütüphanesi eklendi
import pprint  # Güzel çıktı (pretty-print) kütüphanesi eklendi
from pathlib import Path
from astroquery.jplsbdb import SBDB

# Google Colab'da ise indirme için
try:
    from google.colab import files
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

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
    print("--- Uzaylı Bulmacası GENİŞ Veri Toplama Motoru (20590 Eşleşme) ---")

    # ----- GİRDİ VE ÇIKTI DOSYALARI -----

    # === DÜZELTME BURADA ===
    # Colab'a yüklenen dosyanın adını doğrudan yazıyoruz.
    INPUT_FILE_PATH = 'eslesme_sonuclari 20590.txt'
    # =======================

    OUTPUT_JSON = 'genisletilmis_asteroid_db2.json'
    OUTPUT_TXT = 'fullasteroiddb20590.txt'
    # ------------------------------------

    print(f"'{INPUT_FILE_PATH}' dosyası okunuyor...")
    try:
        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"HATA: '{INPUT_FILE_PATH}' bulunamadı.")
        print("Lütfen dosya yolunu kontrol edip tekrar çalıştırın.")
        print("Dosyayı Colab'a (sol taraftaki 'Dosyalar' paneline) yüklediğinizden emin olun.")
        return
    except Exception as e:
        print(f"Dosya okunurken bir hata oluştu: {e}")
        return

    print("Dosya okundu. Cisim isimleri Regex ile çıkarılıyor...")

    # Strateji: Önce [...] içindeki tüm blokları bul,
    # sonra o blokların içindeki "..." tırnaklı metinleri al.
    all_names_set = set()

    # re.DOTALL, . (nokta) karakterinin yeni satırları da eşleştirmesini sağlar
    # Bu, çok satıra yayılmış listeler için önemlidir.
    array_contents = re.findall(r'\[(.*?)\]', file_content, re.DOTALL)

    if not array_contents:
        print("HATA: Dosyada [] ile çevrili hiçbir liste bulunamadı!")
        print("Regex deseni eşleşme bulamadı. Dosya formatı beklenenden farklı olabilir.")
        return

    print(f"Toplam {len(array_contents)} adet isim listesi (array) bloğu bulundu.")

    for content_block in array_contents:
        # Her blok içindeki tırnaklı metinleri bul
        names_in_block = re.findall(r'"(.*?)"', content_block)
        all_names_set.update(names_in_block)

    print(f"Toplam {len(all_names_set)} ham benzersiz cisim adı bulundu.")

    # 'Earth' ismini '399' ID'sine dönüştür
    final_unique_list_set = set()
    for name in all_names_set:
        if name.strip().lower() == 'earth':
            final_unique_list_set.add('399')
        else:
            final_unique_list_set.add(name.strip()) # Baştaki/sondaki boşlukları temizle

    sorted_unique_list = sorted(list(final_unique_list_set))
    print(f"İşlenecek son benzersiz liste: {len(sorted_unique_list)} cisim ('Earth' -> '399' dönüştürüldü).")

    new_asteroid_db = {}
    print("\nNASA JPL SBDB sorgulanıyor... (Bu işlem uzun sürebilir)")

    for i, ast_name_raw in enumerate(sorted_unique_list, start=1):
        print(f"\nİşleniyor: {i} / {len(sorted_unique_list)}: '{ast_name_raw}'")

        if ast_name_raw == '399':
            print("     -> '399' (Dünya) için sabit değerler kullanılacak.")
            data = {'a': 1.000, 'e': 0.0167, 'i': 0.00, 'T_J': 6.138}
        else:
            # İsim temizleme: (2006 QR1) gibi kısımları at
            if '(' in ast_name_raw and not ast_name_raw.startswith(('C/', 'P/')):
                search_name = ast_name_raw.split('(')[0].strip()
                print(f"     (Sorgu için temizlendi: '{search_name}')")
            else:
                search_name = ast_name_raw

            data = fetch_asteroid_data(search_name)
            time.sleep(0.1)  # API'ye saygılı olmak için sorgular arası bekleme

        if data:
            # Veritabanına orijinal, tam adıyla kaydet
            new_asteroid_db[ast_name_raw] = data

    print(f"\n--- Sorgulama Tamamlandı ---")
    print(f"{len(new_asteroid_db)} cisim için veritabanı başarıyla oluşturuldu.")

    # --- 1. ÇIKTI: JSON DOSYASI ---
    print("\nJSON dosyası oluşturuluyor...")
    try:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(new_asteroid_db, f, indent=4, ensure_ascii=False)
        print(f"BAŞARILI: JSON kaydedildi -> {OUTPUT_JSON}")
    except Exception as e:
        print(f"HATA: JSON yazılırken hata oluştu: {e}")

    # --- 2. ÇIKTI: TXT (PYTHON DICT) DOSYASI ---
    print("\nTXT (Python Dict) dosyası oluşturuluyor...")
    try:
        # pprint.pformat ile sözlüğü güzel formatlanmış bir string'e dönüştür
        db_string = pprint.pformat(new_asteroid_db, indent=4)

        with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
            f.write("ASTEROID_DB = ")  # Başına 'ASTEROID_DB = ' ekle
            f.write(db_string)
        print(f"BAŞARILI: TXT kaydedildi -> {OUTPUT_TXT}")
    except Exception as e:
        print(f"HATA: TXT yazılırken hata oluştu: {e}")

    # --- GOOGLE COLAB İNDİRME ---
    if IN_COLAB:
        print("\nGoogle Colab ortamı algılandı. Dosyalar indiriliyor...")
        try:
            files.download(OUTPUT_JSON)
            print(f"'{OUTPUT_JSON}' indirme için hazırlandı.")
        except Exception as e:
            print(f"'{OUTPUT_JSON}' indirilirken hata: {e}")

        try:
            files.download(OUTPUT_TXT)
            print(f"'{OUTPUT_TXT}' indirme için hazırlandı.")
        except Exception as e:
            print(f"'{OUTPUT_TXT}' indirilirken hata: {e}")

if __name__ == "__main__":
    main()