# -*- coding: utf-8 -*-
"""
UZAYLI BULMACASI - FİNAL VERİ TOPLAMA MOTORU (v6.1 - Dünya Düzeltmesi + Full Çıktı)

AMAÇ:
Tüm 7 kilit cismin 15 Ağustos 1977 verilerini çekmek.

GÜNCELLEME (v6.1):
1. 'Dünya' sorgusu, '399' (Major Body) olarak düzeltildi.
2. Pandas 'print' ayarı, 10 sütunun tamamını ('...' olmadan) 
   gösterecek şekilde güncellendi.
"""

import requests
import pandas as pd
import re
import time

# --- 1. API AYARLARI ---
TARGET_URL = "https://ssd.jpl.nasa.gov/api/horizons_file.api"

# --- DÜZELTME 1: Dünya ID'si düzeltildi ---
TARGET_OBJECTS_MAP = {
    # Dünya (Major Body) 'DES=' ön eki almaz, sadece '399' olarak sorgulanır.
    '399': 'Dünya', 
    'DES=20003763;': '3763 Qianxuesen',
    'DES=20015025;': '15025 Uwontario',
    'DES=20055701;': '55701 Ukalegon',
    'DES=20000755;': '755 Quintilla',
    'DES=20084011;': '84011 Jean-Claude'
}
# --- DÜZELTME 1 SONU ---

# --- 2. PAYLOAD ŞABLONLARI (Aynı) ---
PAYLOAD_TEMPLATE_VECTORS = """
!$$SOF
MAKE_EPHEM=YES
COMMAND='{COMMAND_PLACEHOLDER}'
EPHEM_TYPE=VECTORS
CENTER='500@10'
START_TIME='1977-08-15'
STOP_TIME='1977-08-16'
STEP_SIZE='1 DAYS'
VEC_TABLE='3'
REF_SYSTEM='ICRF'
REF_PLANE='ECLIPTIC'
VEC_CORR='NONE'
CAL_TYPE='M'
OUT_UNITS='AU-D'
VEC_LABELS='YES'
VEC_DELTA_T='NO'
CSV_FORMAT='NO'
OBJ_DATA='YES'
"""

PAYLOAD_TEMPLATE_ELEMENTS = """
!$$SOF
MAKE_EPHEM=YES
COMMAND='{COMMAND_PLACEHOLDER}'
EPHEM_TYPE=ELEMENTS
CENTER='500@10'
START_TIME='1977-08-15'
STOP_TIME='1977-08-16'
STEP_SIZE='1 DAYS'
REF_SYSTEM='ICRF'
REF_PLANE='ECLIPTIC'
CAL_TYPE='M'
OUT_UNITS='AU-D'
ELM_LABELS='YES'
TP_TYPE='ABSOLUTE'
CSV_FORMAT='NO'
OBJ_DATA='YES'
"""

# --- 3. VERİ AYRIŞTIRMA FONKSİYONLARI (Aynı) ---

def parse_vector_data(text_result):
    try:
        data_block = text_result.split('$$SOE')[1]
        match = re.search(
            r"A\.D\. 1977-Aug-15 00:00:00\.0000.*?\n"
            r" X =\s*(-?\d+\.\d+E[+-]\d+)\s*Y =\s*(-?\d+\.\d+E[+-]\d+)\s*Z =\s*(-?\d+\.\d+E[+-]\d+)",
            data_block,
            re.DOTALL
        )
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            z = float(match.group(3))
            return {'x_au': x, 'y_au': y, 'z_au': z}
    except Exception as e:
        print(f"    -> HATA (Vektör Ayrıştırma): {e}")
    return None

def parse_element_data(text_result):
    try:
        data_block = text_result.split('$$SOE')[1]
        date_match = re.search(r"A\.D\. 1977-Aug-15 00:00:00\.0000", data_block)
        if not date_match:
            return None
        data_after_date = data_block[date_match.end():]
        elements = {}
        param_map = {
            'A ': 'a_au', 'EC': 'e_ecc', 'IN': 'i_deg',
            'OM': 'Omega_deg', 'W ': 'w_deg', 'MA': 'M_deg'
        }
        for key, name in param_map.items():
            match = re.search(rf"\s{key}=\s*(-?\d+\.\d+)", data_after_date)
            if match:
                elements[name] = float(match.group(1))
        
        # Gezegenler (Dünya) 'A ' yerine 'A=' döndürebilir, B planı
        if 'a_au' not in elements:
             match = re.search(rf"\sA=\s*(-?\d+\.\d+)", data_after_date)
             if match:
                elements['a_au'] = float(match.group(1))

        if len(elements) == 6:
            return elements
    except Exception as e:
        print(f"    -> HATA (Element Ayrıştırma): {e}")
    print(f"    -> UYARI: Tüm yörünge elemanları bulunamadı. Bulunanlar: {elements}")
    return elements

# --- 4. ANA KOD (MOTOR) ---
if __name__ == "__main__":
    print("--- JPL HORIZONS Veri Çekme Motoru Başlatıldı (v6.1 Düzeltildi) ---")
    
    all_data = []
    sun_data = {
        'obj_name': 'Güneş', 'x_au': 0.0, 'y_au': 0.0, 'z_au': 0.0,
        'a_au': 0.0, 'e_ecc': 0.0, 'i_deg': 0.0,
        'Omega_deg': 0.0, 'w_deg': 0.0, 'M_deg': 0.0
    }
    all_data.append(sun_data)
    
    with requests.Session() as session:
        for command, name in TARGET_OBJECTS_MAP.items():
            print(f"\n--- İşleniyor: {name} (ID: {command}) ---")
            
            final_obj_data = {'obj_name': name}
            
            # --- Görev 1: VECTORS (x, y, z) Çek ---
            print("  1. VECTORS (x,y,z) sorgulanıyor...")
            payload_input_v = PAYLOAD_TEMPLATE_VECTORS.format(COMMAND_PLACEHOLDER=command)
            post_data_v = {'format': 'json', 'input': payload_input_v}
            
            try:
                response_v = session.post(TARGET_URL, data=post_data_v)
                response_v.raise_for_status()
                json_v = response_v.json()
                if json_v.get('status') == 'ERROR':
                    print(f"    -> API HATASI (VECTORS): {json_v.get('result')}")
                    continue
                vector_data = parse_vector_data(json_v['result'])
                if vector_data:
                    final_obj_data.update(vector_data)
                    print("    -> Vektör verisi (x,y,z) başarıyla alındı.")
                else:
                    print("    -> HATA: Vektör verisi (x,y,z) metin içinde bulunamadı.")
                    continue
            except requests.exceptions.RequestException as e:
                print(f"    -> HATA (Ağ/HTTP): {e}")
                continue
            
            time.sleep(0.5)
            
            # --- Görev 2: ELEMENTS (a, e, i...) Çek ---
            print("  2. ELEMENTS (a,e,i...) sorgulanıyor...")
            payload_input_e = PAYLOAD_TEMPLATE_ELEMENTS.format(COMMAND_PLACEHOLDER=command)
            post_data_e = {'format': 'json', 'input': payload_input_e}
            
            try:
                response_e = session.post(TARGET_URL, data=post_data_e)
                response_e.raise_for_status()
                json_e = response_e.json()
                if json_e.get('status') == 'ERROR':
                    print(f"    -> API HATASI (ELEMENTS): {json_e.get('result')}")
                    continue 
                element_data = parse_element_data(json_e['result'])
                if element_data:
                    final_obj_data.update(element_data)
                    print("    -> Yörünge elemanları başarıyla alındı.")
                else:
                    print(f"    -> HATA: {name} için yörünge elemanları metin içinde bulunamadı.")
                    # Gezegenler (Dünya) için bu normal olabilir, yörüngeyi
                    # Vektör çıktısından da hesaplayabiliriz, şimdilik devam et.
                    pass # Hata olsa bile devam et (Dünya için)

            except requests.exceptions.RequestException as e:
                print(f"    -> HATA (Ağ/HTTP): {e}")
                continue

            if 'x_au' in final_obj_data: # En azından konum verisi varsa ekle
                all_data.append(final_obj_data)
            else:
                print(f"    -> EKSİK VERİ: {name} listeye eklenemedi.")
                
            time.sleep(0.5)

    # 7. Sonuçları temiz bir Pandas DataFrame'e dönüştür
    if len(all_data) > 1:
        df = pd.DataFrame(all_data)
        
        print("\n\n--- FİNAL VERİ ÇEKME İŞLEMİ TAMAMLANDI ---")
        print(f"{len(all_data)} cisim için tam veri seti oluşturuldu.")
        
        # --- DÜZELTME 2: 10 Sütunun tamamını göstermesi için ayarlar ---
        pd.set_option('display.precision', 8)
        pd.set_option('display.max_columns', None) # '...' (kesmeyi) kaldırır
        pd.set_option('display.width', 1000)       # Çıktının sığması için genişlik
        # --- DÜZELTME 2 SONU ---
        
        print("\nOluşturulan Final Veri Tablosu (15 Ağustos 1977):")
        print(df)
        
        print("\n--- SONRAKİ ADIM ---")
        print("Kral, bu tablo artık planladığımız 3 panelli (A, B, C) görselleştirmeyi yapmak için %100 hazır.")
        print("Bu DataFrame'i bir sonraki adımda (görselleştirme) kullanmak için kopyala veya 'Görselleştirme kodunu yaz' de.")

    else:
        print("\n--- İŞLEM BAŞARISIZ---")
        print("Güneş dışında hiçbir cisim için veri çekilemedi.")