import sqlite3
import re
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. SETTINGS AND FILE PATHS ---

# Database (.db) file settings
DB_DOSYA_YOLU = r"C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\solar_system_analysis_with_distances.db"
DB_TABLO_ADI = "focused_meta_comparison_results"

# Physical Data (.txt) file settings (ONLY USED FOR GROUP B)
TXT_DOSYA_YOLU = r"C:\Users\olgub\OneDrive\Masaüstü\uzaylı bulmaca\kopya tarihler dosyalar - Copy\fullasteroiddb20590.txt"

# Column names
NAME_COLS = ['earth_object_name', 'q_object_name', 'u_object_name', 'j_object_name']
DIST_COLS = ['earth_object_dist', 'q_object_dist', 'u_object_dist', 'j_object_dist']


# --- 2. GROUP A (OUR FAMILY) DEFINITION AND EMBEDDED DATA ---
GRUP_A_RAW_NAMES = [
    "399", "364192 Qianruhu", "4716 Urey", "13441 Janmerlin",
    "399", "9588 Quesnay", "4257 Ubasti", "17195 Jimrichardson",
    "399", "52301 Qumran", "4632 Udagawa", "58424 Jamesdunlop",
    "399", "3513 Quqinyue", "55701 Ukalegon", "5255 Johnsophie",
    "399", "26940 Quientero", "19462 Ulissedini", "84011 Jean-Claude",
    "399", "52301 Qumran", "15025 Uwontario", "30030 Joycekong",
    "399", "2255 Qinghai", "233880 Urbanpriol", "101811 Jakobkaup",
    "399", "17438 Quasimodo", "16515 Usman'grad", "33889 Jengebo"
]
grup_a_set = set(GRUP_A_RAW_NAMES)
grup_a_id_set = {name.split(' ')[0] for name in grup_a_set}

print(f"--- PHYSICAL PROOF (WHY) ENGINE v15 (Label Update) STARTED ---")
print(f"Group A (Our Family) contains {len(grup_a_id_set)} ID references.")

# *** EMBEDDED PHYSICAL DATA FOR GROUP A ***
HARDCODED_GRUP_A_DATA = {
    '399': {'a': 1.0000, 'e': 0.0167, 'i': 0.0000, 'T_J': 6.138},
    '364192': {'a': 2.3914, 'e': 0.2037, 'i': 3.6357, 'T_J': 3.501},
    '4716': {'a': 3.1879, 'e': 0.1277, 'i': 10.1100, 'T_J': 3.161},
    '13441': {'a': 2.6311, 'e': 0.2622, 'i': 11.9332, 'T_J': 3.320},
    '9588': {'a': 2.5879, 'e': 0.2141, 'i': 13.1807, 'T_J': 3.352},
    '4257': {'a': 1.6471, 'e': 0.4684, 'i': 40.7218, 'T_J': 3.913},
    '17195': {'a': 3.2244, 'e': 0.1120, 'i': 6.0845, 'T_J': 3.169},
    '52301': {'a': 2.3137, 'e': 0.2288, 'i': 5.4007, 'T_J': 3.541},
    '4632': {'a': 2.2060, 'e': 0.1724, 'i': 6.4908, 'T_J': 3.633},
    '58424': {'a': 2.5350, 'e': 0.1505, 'i': 4.6026, 'T_J': 3.428},
    '3513': {'a': 2.6290, 'e': 0.0100, 'i': 2.6481, 'T_J': 3.399},
    '55701': {'a': 5.1658, 'e': 0.1408, 'i': 20.9572, 'T_J': 2.850},
    '5255': {'a': 2.6726, 'e': 0.0167, 'i': 11.6220, 'T_J': 3.351},
    '26940': {'a': 2.6074, 'e': 0.1741, 'i': 15.4243, 'T_J': 3.361},
    '19462': {'a': 2.9093, 'e': 0.1040, 'i': 2.2213, 'T_J': 3.275},
    '84011': {'a': 4.0092, 'e': 0.2464, 'i': 4.0115, 'T_J': 2.995},
    '15025': {'a': 3.1976, 'e': 0.1082, 'i': 7.2771, 'T_J': 3.173},
    '30030': {'a': 2.5714, 'e': 0.1557, 'i': 4.3418, 'T_J': 3.415},
    '2255': {'a': 3.1053, 'e': 0.1466, 'i': 14.1374, 'T_J': 3.158},
    '233880': {'a': 3.1907, 'e': 0.1641, 'i': 5.4938, 'T_J': 3.169},
    '101811': {'a': 2.3633, 'e': 0.3214, 'i': 22.1978, 'T_J': 3.383},
    '17438': {'a': 2.3226, 'e': 0.1324, 'i': 3.3247, 'T_J': 3.563},
    '16515': {'a': 3.1639, 'e': 0.1749, 'i': 2.2403, 'T_J': 3.179},
    '33889': {'a': 2.2326, 'e': 0.1812, 'i': 6.5094, 'T_J': 3.611}
}
print(f"Loaded {len(HARDCODED_GRUP_A_DATA)} hardcoded physical data entries for Group A.")


# --- 3. HELPER FUNCTIONS ---

def get_id_from_name(full_name):
    """
    "9588 Quesnay (1981 EF)" -> "9588"
    "Earth" or "399" -> "399"
    """
    if not full_name:
        return None
    if full_name == "399" or "Earth" in full_name:
        return "399"
    match = re.match(r'^(\d+)', full_name)
    if match:
        return match.group(1) 
    return full_name 

def load_physical_db_by_id(file_path):
    """
    Reads fullasteroiddb20590.txt and saves the data to a
    dictionary keyed by object ID (FOR GROUP B).
    """
    print(f"\nReading '{os.path.basename(file_path)}' (Group B) physical database (ID-Parser)...")
    
    name_pattern = re.compile(r"\'(.+?)\'\s*:\s*{")
    
    # *** YENİ: v13 DÜZELTMESİ (re.VERBOSE EKLENDİ) ***
    param_pattern = re.compile(r"""
        \'(a|e|i|T_J)\'      # 1: Key (a, e, i, T_J)
        \s*:\s* # Colon
        (?:np\.float64\()?  # Optional 'np.float64('
        \s*([\d\.-]+)       # 2: The number itself
    """, re.VERBOSE)

    physical_db_by_id = {} 
    current_full_name = None
    current_params = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                name_match = name_pattern.search(line)
                
                if name_match:
                    if current_full_name:
                        name_id = get_id_from_name(current_full_name)
                        if name_id and name_id not in physical_db_by_id:
                            physical_db_by_id[name_id] = current_params
                    current_full_name = name_match.group(1)
                    current_params = {'a': None, 'e': None, 'i': None, 'T_J': None}
                
                if current_full_name:
                    all_params_on_line = param_pattern.finditer(line)
                    for param_match in all_params_on_line:
                        key = param_match.group(1)
                        try:
                            value = float(param_match.group(2))
                            current_params[key] = value
                        except (ValueError, IndexError): pass 
                    
                    if '}' in line:
                        name_id = get_id_from_name(current_full_name)
                        if name_id and name_id not in physical_db_by_id:
                            physical_db_by_id[name_id] = current_params
                        current_full_name = None 
                        current_params = {}

        if current_full_name:
            name_id = get_id_from_name(current_full_name)
            if name_id and name_id not in physical_db_by_id:
                physical_db_by_id[name_id] = current_params

        print(f"Success: Loaded {len(physical_db_by_id)} physical data entries (ID-based) for Group B.")
        return physical_db_by_id

    except FileNotFoundError:
        print(f"!!! ERROR: Physical DB file not found: {file_path}")
        return None
    except Exception as e:
        print(f"!!! ERROR: A general error occurred while reading Physical DB (ID-Parser): {e}")
        return None

def process_database(db_path, grup_a_id_set, hardcoded_grup_a_data, grup_b_physical_data):
    """
    Processes the main .db, separates Group A/B by ID, and
    uses embedded data for Group A and .txt data for Group B.
    """
    print(f"\nReading main database '{os.path.basename(db_path)}'...")
    
    all_db_full_names = set() 
    plot_data_rows = []
    
    db_grup_a_full_names = set() 
    db_grup_b_full_names = set() 
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Read all rows into memory
        sorgu = f"SELECT {', '.join(NAME_COLS + DIST_COLS)} FROM {DB_TABLO_ADI}"
        cursor.execute(sorgu)
        all_rows = cursor.fetchall()
        print(f"Read {len(all_rows)} match rows from the database.")

        # 2. Create Group A and Group B (The Rest) based on ID
        for row in all_rows:
            for i in range(len(NAME_COLS)):
                all_db_full_names.add(row[i])
        all_db_full_names.discard(None) 
        
        print(f"Found {len(all_db_full_names)} unique objects in the database.")
        
        for full_db_name in all_db_full_names:
            name_id = get_id_from_name(full_db_name)
            if name_id in grup_a_id_set:
                db_grup_a_full_names.add(full_db_name)
            else:
                db_grup_b_full_names.add(full_db_name)

        print(f"Group A (Family) matched with {len(db_grup_a_full_names)} objects (by ID).")
        print(f"Group B (The Rest) consists of {len(db_grup_b_full_names)} unique objects.")
        
        if not db_grup_a_full_names:
             print("!!! CRITICAL ERROR: 'Group A' IDs did not match.")
        else:
             print("--- DEBUG: ID Match Report (DB) SUCCESSFUL ---")

        # 4. Populate Data Buckets: a, e, i, T_J (by ID)
        print("Processing physical parameters (a, e, i, T_J) by ID...")
        
        # *** EMBEDDED DATA FOR GROUP A ***
        grup_a_fiziksel_veri_bulundu = 0
        for name_id in grup_a_id_set: 
            if name_id in hardcoded_grup_a_data:
                params = hardcoded_grup_a_data[name_id]
                if params['a'] is not None:
                    plot_data_rows.append({'value': float(params['a']), 'parameter': 'Semi-major axis (AU)', 'group': 'Group A'})
                    grup_a_fiziksel_veri_bulundu += 1
                if params['e'] is not None:
                    plot_data_rows.append({'value': float(params['e']), 'parameter': 'e (Eccentricity)', 'group': 'Group A'})
                if params['i'] is not None:
                    plot_data_rows.append({'value': float(params['i']), 'parameter': 'i (Inclination °)', 'group': 'Group A'})
                if params['T_J'] is not None:
                    plot_data_rows.append({'value': float(params['T_J']), 'parameter': 'T_J (Tisserand)', 'group': 'Group A'})

        if grup_a_fiziksel_veri_bulundu == 0:
             print("!!! WARNING: Physical data (a, e, i, T_J) NOT FOUND for Group A.")
        else:
             print(f"--- DEBUG: Successfully processed {grup_a_fiziksel_veri_bulundu} hardcoded physical data entries for Group A. ---")
             
        # *** .TXT DATA FOR GROUP B ***
        for full_name in db_grup_b_full_names:
            name_id = get_id_from_name(full_name)
            if name_id in grup_b_physical_data: 
                params = grup_b_physical_data[name_id]
                if params['a'] is not None:
                    plot_data_rows.append({'value': float(params['a']), 'parameter': 'Semi-major axis (AU)', 'group': 'Group B'})
                if params['e'] is not None:
                    plot_data_rows.append({'value': float(params['e']), 'parameter': 'e (Eccentricity)', 'group': 'Group B'})
                if params['i'] is not None:
                    plot_data_rows.append({'value': float(params['i']), 'parameter': 'i (Inclination °)', 'group': 'Group B'})
                if params['T_J'] is not None:
                    plot_data_rows.append({'value': float(params['T_J']), 'parameter': 'T_J (Tisserand)', 'group': 'Group B'})
        
        # 5. Populate Data Buckets: object_dist
        print("Processing distance parameter (object_dist)...")
        dist_count_a = 0
        dist_count_b = 0
        for row in all_rows:
            for i in range(len(NAME_COLS)):
                name = row[i]       
                dist = row[i + len(NAME_COLS)] 
                
                if name in db_grup_a_full_names and dist is not None:
                    # *** GÜNCELLENDİ v15 ***
                    plot_data_rows.append({'value': float(dist), 'parameter': 'object_dist (Distance)(AU)', 'group': 'Group A'})
                    dist_count_a += 1
                elif name in db_grup_b_full_names and dist is not None:
                    # *** GÜNCELLENDİ v15 ***
                    plot_data_rows.append({'value': float(dist), 'parameter': 'object_dist (Distance)(AU)', 'group': 'Group B'})
                    dist_count_b += 1
                        
        print(f"Found {dist_count_a} object_dist records for Group A.")
        print(f"Found {dist_count_b} object_dist records for Group B.")
        
        return pd.DataFrame(plot_data_rows)

    except sqlite3.Error as e:
        print(f"!!! DATABASE ERROR: {e}")
        return pd.DataFrame() 
    finally:
        if conn:
            conn.close()

def create_violin_plots(df):
    """
    Plots the 5 violin plots using the prepared DataFrame.
    v15: Updated 'object_dist' label.
    """
    if df.empty:
        print("!!! ERROR: No data found for plotting.")
        return

    print("\n--- GENERATING PLOTS ---")
    
    sns.set_theme(style="whitegrid", rc={"axes.facecolor": (0.9, 0.9, 0.9)})
    
    # *** GÜNCELLENDİ v15 ***
    parameters_to_plot = [
        'Semi-major axis (AU)', 
        'e (Eccentricity)', 
        'i (Inclination °)', 
        'T_J (Tisserand)',  # THE GOLDEN SHOT
        'object_dist (Distance)(AU)'
    ]
    
    fig, axes = plt.subplots(nrows=len(parameters_to_plot), ncols=1, 
                             figsize=(14, 28), sharey=False)
    
    fig.suptitle('Group A (k=1) vs Group B (The Rest) Comparison\n(v14 - Final Filters)', 
                 fontsize=22, y=1.03)

    for i, param in enumerate(parameters_to_plot):
        ax = axes[i]
        
        param_df = df[df['parameter'] == param].copy() 
        
        # --- Filter for 'a (AU)' (v9 fix) ---
        if param == 'Semi-major axis (AU)':
            param_df = param_df[param_df['value'] <= 10]
            param_df = param_df[param_df['value'] >= 0]
            
        # --- Filter for 'object_dist (Distance)' (v10 fix) ---
        # *** GÜNCELLENDİ v15 ***
        if param == 'object_dist (Distance)(AU)':
            param_df = param_df[param_df['value'] <= 10] 
            param_df = param_df[param_df['value'] >= 0]
            
        # *** YENİ: v14 DÜZELTMESİ (Inclination GRAFİĞİ İÇİN FİLTRELEME) ***
        if param == 'i (Inclination °)':
            # Aykırı değeri (150+) atıp 0-75 arasına odaklan
            param_df = param_df[param_df['value'] <= 75] 
            param_df = param_df[param_df['value'] >= 0]
            
        # Check for data after filtering
        if param_df.empty or len(param_df['group'].unique()) < 2:
            print(f"Warning: Not enough data to plot for '{param}' (Group A or B may be missing post-filter).")
            ax.set_title(f"{param} - NOT ENOUGH DATA", color='red')
            continue

        sns.violinplot(
            data=param_df, 
            x='parameter', y='value', hue='group',
            split=True, inner='quartile',
            palette={'Group A': '#FF5733', 'Group B': '#335BFF'},
            hue_order=['Group A', 'Group B'], 
            ax=ax
        )
        
        if param == 'T_J (Tisserand)':
            ax.axhline(y=3.0, color='red', linestyle='--', linewidth=2, label='Main Belt Limit (T_J=3)')
            ax.axhline(y=2.0, color='green', linestyle='--', linewidth=2, label='Centaur Limit (T_J=2)')
            ax.legend(loc='upper right')
            
        ax.set_title(f'{param} Distribution', fontsize=16)
        ax.set_xlabel('')
        ax.set_ylabel('Value', fontsize=12)
        
        if i == 0:
            ax.legend(title='Group', loc='upper right')
        else:
            if ax.get_legend():
                ax.get_legend().remove()

    plt.tight_layout(rect=[0, 0, 1, 1]) 
    
    output_filename_png = 'Plot_3a_Physical_Comparison_Violin.png'
    output_filename_pdf = 'Plot_3a_Physical_Comparison_Violin.pdf'
    
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


# --- 4. MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # 1. Load .txt data for Group B
    grup_b_fiziksel_veri = load_physical_db_by_id(TXT_DOSYA_YOLU)
    
    if grup_b_fiziksel_veri:
        # 2. Run the main processing function
        final_df = process_database(
            DB_DOSYA_YOLU, 
            grup_a_id_set, 
            HARDCODED_GRUP_A_DATA,  # Embedded Group A Data
            grup_b_fiziksel_veri    # .txt Group B Data
        )
        # 3. Plot the results
        create_violin_plots(final_df)
    else:
        print("Physical DB (ID-Parser) could not be loaded. Halting operation.")