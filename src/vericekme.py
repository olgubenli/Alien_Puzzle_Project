# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 09:53:11 2025

@author: olgub
"""

# -*- coding: utf-8 -*-

# ====== Otomatik bağımlılık kurulumu (Colab/Jupyter/CLI) ======
import sys, subprocess, importlib

def ensure(pkg, import_name=None, version=None):
    modname = import_name or pkg
    try:
        importlib.import_module(modname)
    except ImportError:
        to_install = f"{pkg}{version or ''}"
        print(f"[deps] {to_install} kuruluyor...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", to_install])
            importlib.invalidate_caches()
        except Exception as e:
            print(f"[deps] UYARI: {to_install} kurulamadı: {e}")

# Gerekli paketleri sırayla doğrula/kur
ensure("requests")
ensure("pandas")
ensure("beautifulsoup4", import_name="bs4")
ensure("urllib3")
ensure("openpyxl")
ensure("astroquery")
ensure("tqdm")

# ====== İçe aktarımlar ======
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import math
from datetime import datetime, timedelta
import os
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

try:
    from astroquery.jplhorizons import Horizons
    ASTROQUERY_AVAILABLE = True
    print("Astroquery başarıyla yüklendi ve import edildi.")
except (ModuleNotFoundError, ImportError):
    ASTROQUERY_AVAILABLE = False
    print("UYARI: 'astroquery' kütüphanesi bulunamadı veya import edilemedi.")

# ================ KAYNAKLAR ================
LS_API_BODIES = "https://api.le-systeme-solaire.net/rest/bodies/"
MPC_ASTEROID_URL = "https://minorplanetcenter.net/iau/lists/MPNames.html"
SBDB_API_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"

# ================ STATİK LİSTELER ================
PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
DWARF_PLANETS = ["Pluto", "Ceres", "Eris", "Makemake", "Haumea", "Gonggong", "Sedna"]
GAS_DUST_CLOUDS = ["Horsehead Nebula", "Orion Nebula", "Ursa Major Molecular Cloud", "Jabbah Nebula"]
ARTIFICIAL_SATS = ["Voyager 1", "Voyager 2", "Pioneer 10", "Pioneer 11", "Cassini", "Juno",
                   "James Webb Space Telescope", "Hubble Space Telescope", "New Horizons", "ISS"]
OORT_CLOUD_OBJECTS = ["90377 Sedna", "2012 VP113"]
BRIGHT_STARS = ["Sirius", "Canopus", "Arcturus", "Vega", "Capella", "Rigel", "Procyon", "Achernar", "Betelgeuse", "Antares"]

ASTEROID_OC_CLASSES = {"apo", "amo", "ate", "atira", "iap", "hyp", "imb", "mcb", "pha", "nea", "mba", "omb", "tjN", "tja", "ast"}

session = requests.Session()
session.headers.update({
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))

def get_horizons_id_candidate(object_name_or_id, is_major=False, is_asteroid_number=False):
    query_id = str(object_name_or_id).strip()
    if is_major:
        if query_id.lower() == "mercury": return "199"
        elif query_id.lower() == "venus": return "299"
        elif query_id.lower() == "earth": return "399"
        elif query_id.lower() == "mars": return "499"
        elif query_id.lower() == "jupiter": return "599"
        elif query_id.lower() == "saturn": return "699"
        elif query_id.lower() == "uranus": return "799"
        elif query_id.lower() == "neptune": return "899"
        elif query_id.lower() == "pluto": return "999"
        elif query_id.lower() == "ceres": return "1;"
        return query_id
    elif is_asteroid_number:
        if query_id.isdigit() and not query_id.endswith(';'): return query_id + ';'
        return query_id
    else:
        name_cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', query_id).strip()
        if name_cleaned.isdigit() and not name_cleaned.endswith(';'): return name_cleaned + ';'
        match_num_name = re.match(r"^\s*(\d+)\s+.*", name_cleaned)
        if match_num_name: return match_num_name.group(1) + ';'
        return name_cleaned

def get_instantaneous_distance_to_sun(horizons_id_candidate, target_date_str):
    if not ASTROQUERY_AVAILABLE or not horizons_id_candidate: return None
    try:
        target_dt_obj = datetime.strptime(target_date_str, '%Y-%m-%d')
        start_dt_obj = target_dt_obj - timedelta(days=1)
        epochs_dict = {'start': start_dt_obj.strftime('%Y-%m-%d'), 'stop': target_dt_obj.strftime('%Y-%m-%d'), 'step': '1d'}
        obj = Horizons(id=horizons_id_candidate, location='@sun', epochs=epochs_dict, id_type=None)
        eph = obj.ephemerides(cache=False)
        if eph and 'r' in eph.colnames and 'datetime_str' in eph.colnames:
            target_date_horizons_format = target_dt_obj.strftime('%Y-%b-%d')
            if len(eph) >= 2 and eph['datetime_str'][-1].startswith(target_date_horizons_format):
                return eph['r'][-1]
            elif len(eph) == 1 and eph['datetime_str'][0].startswith(target_date_horizons_format):
                return eph['r'][0]
        return None
    except Exception:
        return None

def fetch_sbdb_object_details(identifier, by_name=False):
    fullname_val, oc_val, orbit_distances, horizons_id_candidate = None, "", (None, None, None), None
    if not identifier: return fullname_val, oc_val, orbit_distances, horizons_id_candidate
    try:
        key = "sstr" if by_name else "des"
        r_detail = session.get(SBDB_API_URL, params={key: identifier}, timeout=30)
        if r_detail.status_code == 200:
            detail_data = r_detail.json()
            if detail_data.get("object"):
                obj_dict = detail_data["object"]
                fullname_val = str(obj_dict.get("fullname") or obj_dict.get("shortname") or obj_dict.get("name")).strip()
                if not by_name: horizons_id_candidate = get_horizons_id_candidate(identifier, is_asteroid_number=True)
                elif fullname_val:
                    match_num_name = re.match(r"^\s*(\d+).*", fullname_val)
                    if match_num_name: horizons_id_candidate = get_horizons_id_candidate(match_num_name.group(1), is_asteroid_number=True)
                    else: horizons_id_candidate = get_horizons_id_candidate(fullname_val)
                else: horizons_id_candidate = get_horizons_id_candidate(identifier)
                if obj_dict.get("orbit_class"): oc_val = str(obj_dict["orbit_class"].get("code", "")).lower().strip()
                if detail_data.get("orbit") and detail_data["orbit"].get("elements"):
                    elements = detail_data["orbit"]["elements"]
                    q = next((el.get("value") for el in elements if el.get("name") == "q"), None)
                    Q = next((el.get("value") for el in elements if el.get("name") == "Q"), None)
                    a = next((el.get("value") for el in elements if el.get("name") == "a"), None)
                    if q and a and not Q:
                        try: Q = f"{(2 * float(a) - float(q)):.6f}"
                        except: pass
                    orbit_distances = (q, Q, a)
    except Exception: pass
    return fullname_val, oc_val, orbit_distances, horizons_id_candidate

def get_sbdb_list(letter):
    out, processed_identifiers = [], set()
    try:
        object_list = session.get(SBDB_API_URL, params={"sstr": f"{letter}*"}, timeout=45).json().get("list", [])
        for obj_summary in object_list:
            pdes_identifier = obj_summary.get("pdes")
            if not pdes_identifier or pdes_identifier in processed_identifiers: continue
            processed_identifiers.add(pdes_identifier)
            time.sleep(0.05)
            fullname, oc_val, distances, hid_candidate = fetch_sbdb_object_details(pdes_identifier, by_name=False)
            if fullname and (oc_val in ASTEROID_OC_CLASSES): out.append((fullname, distances, hid_candidate))
    except (requests.exceptions.RequestException, ValueError): pass
    return sorted(out, key=lambda x: x[0])

def get_mpc_list_with_ids(letter):
    mpc_names_only = []
    try:
        soup = BeautifulSoup(session.get(MPC_ASTEROID_URL, timeout=30).text, 'html.parser')
        pre_tag = soup.find('pre')
        if pre_tag:
            regex = r"^\s*\(\s*\d+\s*\)\s+(" + re.escape(letter) + r"[A-Za-z0-9\s\-']*?)(?:\s+\([^\)]*\)|=.*)?\s*$"
            for line in pre_tag.text.splitlines():
                match = re.match(regex, line, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    parts = name.split()
                    if len(parts) > 1 and len(parts) % 2 == 0:
                        mid = len(parts) // 2
                        if " ".join(parts[:mid]) == " ".join(parts[mid:]): name = " ".join(parts[:mid])
                    if name.upper().startswith(letter.upper()): mpc_names_only.append(name)
            mpc_names_only = sorted(list(set(mpc_names_only)))
    except Exception: return []
    asteroids_with_ids = []
    for name_from_mpc in mpc_names_only:
        fullname, _, distances, hid_candidate = fetch_sbdb_object_details(name_from_mpc, by_name=True)
        asteroids_with_ids.append((fullname or name_from_mpc, distances, hid_candidate))
        time.sleep(0.05)
    return asteroids_with_ids

def fetch_ls_moons(letter):
    try:
        bodies = session.get(LS_API_BODIES, headers={"Authorization": "Bearer 311015de-d0a6-49d4-ad1f-2f178f6c6a7f"}, timeout=30).json().get("bodies", [])
        return sorted(list(set([b["englishName"] for b in bodies if not b.get("isPlanet") and b.get("aroundPlanet") and b.get("englishName") and b["englishName"].upper().startswith(letter.upper())])))
    except Exception: return []

def get_clean_name(fullname):
    if not isinstance(fullname, str): return ""
    name = re.sub(r'\s*\([^)]*\)\s*$', '', fullname).strip()
    name = re.sub(r'<[^>]+>', '', name).strip()
    name = re.sub(r'^\d+\s+', '', name).strip()
    return name

def collect_all(letter):
    L_upper = letter.upper()
    all_data = [get_mpc_list_with_ids(L_upper), get_sbdb_list(L_upper)]
    unique_asteroids_dict = {}
    for data_list in all_data:
        for fullname, distances, hid_candidate in data_list:
            clean_name_key = get_clean_name(fullname)
            if clean_name_key:
                if clean_name_key not in unique_asteroids_dict or \
                   (unique_asteroids_dict[clean_name_key][1] == (None,None,None) and distances != (None,None,None)) or \
                   (not unique_asteroids_dict[clean_name_key][2] and hid_candidate):
                    unique_asteroids_dict[clean_name_key] = (fullname, distances, hid_candidate)
                elif fullname and unique_asteroids_dict[clean_name_key][0] and len(fullname) > len(unique_asteroids_dict[clean_name_key][0]):
                    unique_asteroids_dict[clean_name_key] = (fullname, distances, hid_candidate)
    
    def prepare_list_with_hid(item_names_list, is_major_body=False):
        return [(name, (None,None,None), get_horizons_id_candidate(name, is_major=is_major_body)) for name in item_names_list if name.upper().startswith(L_upper)]

    return {
        "Asteroids (Unique)": sorted(unique_asteroids_dict.values(), key=lambda x: (get_clean_name(x[0]), x[0])),
        "Planets": prepare_list_with_hid(PLANETS, is_major_body=True),
        "Dwarf Planets": prepare_list_with_hid(DWARF_PLANETS, is_major_body=True),
        "Natural Satellites": prepare_list_with_hid(fetch_ls_moons(L_upper)),
        "Artificial Satellites": prepare_list_with_hid(ARTIFICIAL_SATS),
        "Stars": [(s, (None,None,None), None) for s in BRIGHT_STARS if s.upper().startswith(L_upper)],
        "Gas & Dust Clouds": [(gdc, (None,None,None), None) for gdc in GAS_DUST_CLOUDS if gdc.upper().startswith(L_upper)],
        "Oort Cloud Objects": [(o, (None,None,None), None) for o in OORT_CLOUD_OBJECTS if o.upper().startswith(L_upper)],
    }

def write_excel(letter, data, target_date_str):
    # ===== DEĞİŞİKLİK BURADA =====
    output_path = "AstroData6/"
    # =============================
    os.makedirs(output_path, exist_ok=True)
    filename = f"{output_path}{letter.upper()}_solar_system_objects_{target_date_str}.xlsx"
    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            for cat, items in data.items():
                if not items: continue
                safe_cat_name = re.sub(r'[\\/*?:\[\]]', '_', cat)[:31]
                columns = ["Object", "Perihelion_AU", "Aphelion_AU", "Semi_Major_Axis_AU", "HORIZONS_ID_Candidate", f"Instant_Sun_Dist_AU_{target_date_str}"]
                df_data = []
                item_iterator = tqdm(items, desc=f"'{cat}' ({letter}-{target_date_str})", unit=" obj", leave=False)
                for item_name, orbital_params, hid_candidate in item_iterator:
                    q, Q, a = orbital_params or (None, None, None)
                    inst_dist_val = get_instantaneous_distance_to_sun(hid_candidate, target_date_str) if hid_candidate else None
                    df_data.append([item_name, q or "N/A", Q or "N/A", a or "N/A", hid_candidate or "N/A",
                                  f"{inst_dist_val:.6f}" if inst_dist_val is not None else "N/A"])
                    if ASTROQUERY_AVAILABLE and hid_candidate: time.sleep(0.1)
                
                df = pd.DataFrame(df_data, columns=columns)
                df.to_excel(writer, sheet_name=safe_cat_name, index=False)
                worksheet = writer.sheets[safe_cat_name]
                for col_letter, width in zip(['A', 'B', 'C', 'D', 'E', 'F'], [35, 20, 20, 25, 30, 30]):
                    worksheet.column_dimensions[col_letter].width = width
        return filename
    except Exception as e:
        print(f"Excel yazma hatası ({letter}-{target_date_str}): {e}")
        return None

def process_letter_for_date(args):
    letter_to_search, target_date_str = args
    process_id = os.getpid()
    print(f"[{process_id}] İşlem başladı: Harf='{letter_to_search}', Tarih='{target_date_str}'")
    start_time = time.time()
    try:
        collected_data = collect_all(letter_to_search)
        output_file = write_excel(letter_to_search, collected_data, target_date_str)
        end_time = time.time()
        result_message = f"Başarıyla tamamlandı. Süre: {end_time - start_time:.2f} sn. Dosya: {output_file}" if output_file else "Hatalarla tamamlandı."
        print(f"[{process_id}] İşlem bitti: Harf='{letter_to_search}', Tarih='{target_date_str}'. {result_message}")
        return output_file
    except Exception as e:
        end_time = time.time()
        error_message = f"İşlem sırasında beklenmedik bir hata oluştu: {e}"
        print(f"[{process_id}] İşlem çöktü: Harf='{letter_to_search}', Tarih='{target_date_str}'. Süre: {end_time - start_time:.2f} sn. Hata: {error_message}")
        return None

# =========================================================
# ANA ÇALIŞTIRMA BLOĞU (PARALEL)
# =========================================================
if __name__ == "__main__":
    # ---- GÖREVLERİNİ BURADAN GÜNCELLE ----
    
    # 1. İşlenecek tarihleri bir liste olarak tanımla
    dates_to_process = [
        '1980-04-29', '1982-07-01', '1984-01-20', '1985-11-06', '1987-02-26'
    ]

    # 2. İşlenecek harfleri tanımla
    letters_to_process = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # 3. Tüm tarih ve harf kombinasyonlarından görev listesini otomatik oluştur
    tasks = [(letter, date_str) for date_str in dates_to_process for letter in letters_to_process]
    
    # ------------------------------------

    # RAM sorunlarını önlemek için çekirdek sayısını manuel olarak giriyoruz.
    num_processes = 6
    
    print(f"Toplam {len(tasks)} görev, {num_processes} çekirdek kullanılarak paralel olarak çalıştırılacak.")
    print("-" * 50)
    
    overall_start = time.time()

    # İşlem havuzu (Pool) oluştur
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_letter_for_date, tasks)

    overall_end = time.time()
    
    print("-" * 50)
    print(f"\n>>>>> TÜM İŞLEMLER TAMAMLANDI! <<<<<")
    print(f"Başarıyla tamamlanan dosyalar: {[res for res in results if res]}")
    print(f"Toplam geçen süre: {(overall_end - overall_start) / 3600:.2f} saat.")