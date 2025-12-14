# -*- coding: utf-8 -*-
"""
Created on Mon Nov 3 09:50:48 2025

@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov 2 22:10:00 2025
@author: olgub

--- UZAYLI BULMACASI FİNAL MOTORU (v4.5 - Tam Matris Veritabanı) ---
AMAÇ: TÜM BENZERSİZ asteroidleri almak ve aralarındaki TÜM OLASI (N x N) 
      "serbest uçuş" maliyetlerini hesaplayıp bir sqlite veritabanına yazmak.
      Bu, manuel kontrol ve analiz için bir ana referans tablosudur.
"""

import heapq
import sqlite3
import itertools
import time

# --- KULLICI AYARLARI VE VERİ GİRİŞİ ---
WEIGHTS = { 'wa': 1.0, 'we': 5.0, 'wi': 10.0, 'wT': 2.0 }
# DOSYA ADI BURADA GÜNCELLENDİ
DB_FILE_NAME = "uzayli_bulmacasi_matrixson.db"

# === k=7 (TÜM 117+ ASTEROİD) VERİTABANI - GÜNCELLENDİ ===
# Bu, tüm benzersiz asteroidleri içeren tam listedir.
ASTEROID_DB = {
    '399': {'a': 1.0000, 'e': 0.0167, 'i': 0.0000, 'T_J': 6.138},
    '100229 Jeanbailly': {'a': 3.9437, 'e': 0.2392, 'i': 4.7576, 'T_J': 3.004},
    '100434 Jinyilian': {'a': 2.6501, 'e': 0.2051, 'i': 17.1464, 'T_J': 3.298},
    '10072 Uruguay': {'a': 2.2776, 'e': 0.1051, 'i': 3.7369, 'T_J': 3.598},
    '101811 Jakobkaup': {'a': 2.3633, 'e': 0.3214, 'i': 22.1978, 'T_J': 3.383},
    '10930 Jinyong': {'a': 3.0503, 'e': 0.1061, 'i': 10.2412, 'T_J': 3.204},
    '11593 Uchikawa': {'a': 2.2152, 'e': 0.0938, 'i': 2.5946, 'T_J': 3.647},
    '120481 Johannwalter': {'a': 2.4009, 'e': 0.1987, 'i': 2.1222, 'T_J': 3.498},
    '121007 Jiaxingnanhu': {'a': 2.2764, 'e': 0.3306, 'i': 11.0074, 'T_J': 3.511},
    '12360 Unilandes': {'a': 3.2115, 'e': 0.1895, 'i': 2.3786, 'T_J': 3.162},
    '1239 Queteleta': {'a': 2.6624, 'e': 0.2305, 'i': 1.6571, 'T_J': 3.346},
    '13069 Umbertoeco': {'a': 2.3716, 'e': 0.2482, 'i': 7.3340, 'T_J': 3.491},
    '13192 Quine': {'a': 2.2880, 'e': 0.1435, 'i': 0.6644, 'T_J': 3.587},
    '13441 Janmerlin': {'a': 2.6311, 'e': 0.2622, 'i': 11.9332, 'T_J': 3.320},
    '1351 Uzbekistania': {'a': 3.1949, 'e': 0.0692, 'i': 9.6435, 'T_J': 3.170},
    '15025 Uwontario': {'a': 3.1976, 'e': 0.1082, 'i': 7.2771, 'T_J': 3.173},
    '16012 Jamierubin': {'a': 2.4207, 'e': 0.1653, 'i': 2.3078, 'T_J': 3.494},
    '16356 Univbalttech': {'a': 3.1607, 'e': 0.1131, 'i': 2.7826, 'T_J': 3.193},
    "16515 Usman'grad": {'a': 3.1639, 'e': 0.1749, 'i': 2.2403, 'T_J': 3.179},
    '169509 Jeffreyrobbins': {'a': 3.9613, 'e': 0.2555, 'i': 3.3284, 'T_J': 2.998},
    '32532 Thereus': {'a': 10.6384, 'e': 0.1976, 'i': 20.3674, 'T_J': 3.117},
    '17195 Jimrichardson': {'a': 3.2244, 'e': 0.1120, 'i': 6.0845, 'T_J': 3.169},
    '17438 Quasimodo': {'a': 2.3226, 'e': 0.1324, 'i': 3.3247, 'T_J': 3.563},
    '177415 Queloz': {'a': 2.6078, 'e': 0.1339, 'i': 9.3169, 'T_J': 3.380},
    '18376 Quirk': {'a': 2.7234, 'e': 0.2342, 'i': 10.5041, 'T_J': 3.294},
    '187447 Johnmester': {'a': 2.7082, 'e': 0.2186, 'i': 15.0393, 'T_J': 3.281},
    '19462 Ulissedini': {'a': 2.9093, 'e': 0.1040, 'i': 2.2213, 'T_J': 3.275},
    '199947 Qaidam': {'a': 2.6355, 'e': 0.2906, 'i': 16.2917, 'T_J': 3.282},
    '20278 Qileihang': {'a': 2.4294, 'e': 0.1337, 'i': 3.3173, 'T_J': 3.494},
    '207723 Jiansanjiang': {'a': 2.3398, 'e': 0.0487, 'i': 3.6667, 'T_J': 3.561},
    '21559 Jingyuanluo': {'a': 2.6175, 'e': 0.2465, 'i': 11.0931, 'T_J': 3.337},
    '2255 Qinghai': {'a': 3.1053, 'e': 0.1466, 'i': 14.1374, 'T_J': 3.158},
    '233880 Urbanpriol': {'a': 3.1907, 'e': 0.1641, 'i': 5.4938, 'T_J': 3.169},
    '236909 Jakoberwin': {'a': 3.1087, 'e': 0.0818, 'i': 1.3555, 'T_J': 3.214},
    '23900 Urakawa': {'a': 2.7863, 'e': 0.0360, 'i': 3.2581, 'T_J': 3.328},
    '24214 Jonchristo': {'a': 3.0379, 'e': 0.1193, 'i': 0.9102, 'T_J': 3.230},
    '25129 Uranoscope': {'a': 2.2641, 'e': 0.1999, 'i': 6.2217, 'T_J': 3.583},
    '25138 Jaumann': {'a': 2.6612, 'e': 0.1074, 'i': 3.5149, 'T_J': 3.375},
    '25415 Jocelyn': {'a': 2.3319, 'e': 0.0535, 'i': 2.9675, 'T_J': 3.567},
    '25869 Jacoby': {'a': 3.9830, 'e': 0.1448, 'i': 16.9648, 'T_J': 2.962},
    '25988 Janesuh': {'a': 2.6282, 'e': 0.1818, 'i': 4.7463, 'T_J': 3.373},
    '2617 Jiangxi': {'a': 3.1509, 'e': 0.2385, 'i': 12.9685, 'T_J': 3.124},
    '26891 Johnbutler': {'a': 1.9334, 'e': 0.0448, 'i': 17.1233, 'T_J': 3.855},
    '26940 Quintero': {'a': 2.2480, 'e': 0.1397, 'i': 8.6049, 'T_J': 3.602},
    '27048 Jangong': {'a': 2.3524, 'e': 0.0957, 'i': 6.6569, 'T_J': 3.542},
    '27301 Joeingalls': {'a': 2.2333, 'e': 0.0919, 'i': 6.4062, 'T_J': 3.627},
    '27790 Urashimataro': {'a': 3.1699, 'e': 0.0612, 'i': 10.2571, 'T_J': 3.175},
    '27827 Ukai': {'a': 2.7533, 'e': 0.1085, 'i': 6.9860, 'T_J': 3.325},
    '279037 Utezimmer': {'a': 2.8116, 'e': 0.1173, 'i': 4.3230, 'T_J': 3.307},
    '28125 Juliomiguez': {'a': 2.2754, 'e': 0.0879, 'i': 3.9975, 'T_J': 3.601},
    '28275 Quoc-Bao': {'a': 2.9770, 'e': 0.0828, 'i': 1.4043, 'T_J': 3.255},
    '283279 Qianweichang': {'a': 2.5892, 'e': 0.0922, 'i': 11.2971, 'T_J': 3.387},
    '2868 Upupa': {'a': 2.8138, 'e': 0.1776, 'i': 7.5483, 'T_J': 3.284},
    '290001 Uebersax': {'a': 3.0448, 'e': 0.2255, 'i': 17.4028, 'T_J': 3.131},
    '29189 Udinsk': {'a': 3.1049, 'e': 0.2390, 'i': 9.9862, 'T_J': 3.153},
    '29950 Uppili': {'a': 2.4444, 'e': 0.1589, 'i': 3.5231, 'T_J': 3.480},
    '30030 Joycekang': {'a': 2.4381, 'e': 0.1544, 'i': 2.6624, 'T_J': 3.485},
    '3010 Ushakov': {'a': 3.2298, 'e': 0.1641, 'i': 2.0365, 'T_J': 3.164},
    '306001 Joanllaneras': {'a': 5.2502, 'e': 0.1542, 'i': 10.1184, 'T_J': 2.945},
    '31988 Jasonfiacco': {'a': 2.2442, 'e': 0.1584, 'i': 2.2393, 'T_J': 3.615},
    '3335 Quanzhou': {'a': 2.6102, 'e': 0.1269, 'i': 13.3191, 'T_J': 3.361},
    '33487 Jeanpierrerivet': {'a': 2.2668, 'e': 0.0901, 'i': 4.9155, 'T_J': 3.605},
    '336877 Qifaren': {'a': 2.7022, 'e': 0.0604, 'i': 13.0173, 'T_J': 3.327},
    '33889 Jengebo': {'a': 2.2326, 'e': 0.1812, 'i': 6.5094, 'T_J': 3.611},
    '34204 Quryshi': {'a': 2.7118, 'e': 0.0965, 'i': 6.9226, 'T_J': 3.345},
    '3468 Urgenta': {'a': 3.0202, 'e': 0.0786, 'i': 10.9987, 'T_J': 3.214},
    '34862 Utkarshtandon': {'a': 2.9889, 'e': 0.1464, 'i': 5.4428, 'T_J': 3.234},
    '3513 Quqinyue': {'a': 2.6290, 'e': 0.0100, 'i': 2.6481, 'T_J': 3.399},
    '364192 Qianruhu': {'a': 2.3914, 'e': 0.2037, 'i': 3.6357, 'T_J': 3.501},
    '364636 Ulrikeecker': {'a': 2.2349, 'e': 0.1513, 'i': 4.1185, 'T_J': 3.621},
    '3722 Urata': {'a': 2.2356, 'e': 0.2000, 'i': 6.4611, 'T_J': 3.604},
    '3763 Qianxuesen': {'a': 2.2528, 'e': 0.1043, 'i': 7.0195, 'T_J': 3.609},
    '38431 Jeffbeck': {'a': 2.7029, 'e': 0.1278, 'i': 9.9731, 'T_J': 3.333},
    '3876 Quaide': {'a': 3.0188, 'e': 0.0846, 'i': 11.2439, 'T_J': 3.212},
    '39415 Janeausten': {'a': 3.9421, 'e': 0.2020, 'i': 2.3820, 'T_J': 3.023},
    "4139 Ul'yanin": {'a': 3.1458, 'e': 0.1637, 'i': 1.5925, 'T_J': 3.188},
    '4257 Ubasti': {'a': 1.6471, 'e': 0.4684, 'i': 40.7218, 'T_J': 3.913},
    '42614 Ubaldina': {'a': 2.2445, 'e': 0.0779, 'i': 1.2494, 'T_J': 3.628},
    '43574 Joyharjo': {'a': 2.6093, 'e': 0.2125, 'i': 5.1302, 'T_J': 3.373},
    '4372 Quincy': {'a': 2.9325, 'e': 0.1258, 'i': 1.5034, 'T_J': 3.263},
    '44011 Juubichi': {'a': 3.0611, 'e': 0.0777, 'i': 8.6256, 'T_J': 3.212},
    '4632 Udagawa': {'a': 2.2060, 'e': 0.1724, 'i': 6.4908, 'T_J': 3.633},
    '4716 Urey': {'a': 3.1879, 'e': 0.1277, 'i': 10.1100, 'T_J': 3.161},
    '4761 Urrutia': {'a': 2.3392, 'e': 0.2162, 'i': 25.5694, 'T_J': 3.406},
    '47708 Jimhamilton': {'a': 2.9710, 'e': 0.0722, 'i': 10.3380, 'T_J': 3.234},
    '49294 Jacqclairnoens': {'a': 2.3462, 'e': 0.2756, 'i': 3.1009, 'T_J': 3.507},
    '50000 Quaoar': {'a': 43.1477, 'e': 0.0358, 'i': 7.9914, 'T_J': 5.820},
    '501 Urhixidur': {'a': 3.1633, 'e': 0.1419, 'i': 20.8349, 'T_J': 3.088},
    '52260 Ureshino': {'a': 2.3974, 'e': 0.2192, 'i': 24.8998, 'T_J': 3.372},
    '52301 Qumran': {'a': 2.3137, 'e': 0.2288, 'i': 5.4007, 'T_J': 3.541},
    '5254 Ulysses': {'a': 5.2213, 'e': 0.1212, 'i': 24.2002, 'T_J': 2.810},
    '5255 Johnsophie': {'a': 2.6726, 'e': 0.0167, 'i': 11.6220, 'T_J': 3.351},
    '5565 Ukyounodaibu': {'a': 2.8086, 'e': 0.2176, 'i': 10.3128, 'T_J': 3.264},
    '55701 Ukalegon': {'a': 5.1658, 'e': 0.1408, 'i': 20.9572, 'T_J': 2.850},
    '58098 Quirrenbach': {'a': 1.9243, 'e': 0.0824, 'i': 22.8399, 'T_J': 3.821},
    '58424 Jamesdunlop': {'a': 2.5350, 'e': 0.1505, 'i': 4.6026, 'T_J': 3.428},
    '5865 Qualytemocrina': {'a': 2.4076, 'e': 0.1303, 'i': 7.6224, 'T_J': 3.498},
    '5900 Jensen': {'a': 3.1530, 'e': 0.2090, 'i': 9.0566, 'T_J': 3.154},
    '5964 Johnjunkins': {'a': 3.0555, 'e': 0.3086, 'i': 3.3950, 'T_J': 3.158},
    '596543 Ubu': {'a': 3.0424, 'e': 0.1968, 'i': 1.7746, 'T_J': 3.209},
    '602922 Juhaszgyula': {'a': 3.1945, 'e': 0.1461, 'i': 9.1682, 'T_J': 3.159},
    '6063 Jason': {'a': 2.2199, 'e': 0.7625, 'i': 4.9616, 'T_J': 3.186},
    '6137 Johnfletcher': {'a': 3.2151, 'e': 0.0629, 'i': 15.4246, 'T_J': 3.131},
    '6171 Uttorp': {'a': 2.2156, 'e': 0.1001, 'i': 3.0375, 'T_J': 3.645},
    '6249 Jennifer': {'a': 1.9144, 'e': 0.1420, 'i': 28.1060, 'T_J': 3.777},
    '7290 Johnrather': {'a': 2.5575, 'e': 0.2290, 'i': 24.7349, 'T_J': 3.274},
    '7342 Uchinoura': {'a': 2.6988, 'e': 0.1029, 'i': 13.8822, 'T_J': 3.319},
    '755 Quintilla': {'a': 3.1942, 'e': 0.1293, 'i': 3.2309, 'T_J': 3.180},
    '78652 Quero': {'a': 2.6071, 'e': 0.1292, 'i': 7.5815, 'T_J': 3.387},
    '8073 Johnharmon': {'a': 2.5937, 'e': 0.1671, 'i': 12.7204, 'T_J': 3.364},
    '84011 Jean-Claude': {'a': 4.0092, 'e': 0.2464, 'i': 4.0115, 'T_J': 2.995},
    '8755 Querquedula': {'a': 3.2198, 'e': 0.1439, 'i': 1.3842, 'T_J': 3.172},
    '90918 Jasinski': {'a': 2.3074, 'e': 0.1620, 'i': 4.2075, 'T_J': 3.566},
    '9519 Jeffkeck': {'a': 2.5668, 'e': 0.0829, 'i': 4.5140, 'T_J': 3.423},
    '9588 Quesnay': {'a': 2.5879, 'e': 0.2141, 'i': 13.1807, 'T_J': 3.352},
    '96327 Ullmann': {'a': 1.9527, 'e': 0.0777, 'i': 22.8200, 'T_J': 3.791},
    '9657 Ucka': {'a': 3.1376, 'e': 0.1774, 'i': 0.8933, 'T_J': 3.187},
    '9720 Ulfbirgitta': {'a': 2.9357, 'e': 0.1053, 'i': 11.9447, 'T_J': 3.234},
    'C/1946 P1': {'a': -1477.9, 'e': 1.0008, 'i': 56.9646, 'T_J': 0.717},
}
# ==================================


# --- ANALİZ MOTORU KODU ---

def calculate_cost(id1, id2, weights):
    if id1 not in ASTEROID_DB:
        print(f"HATA: {id1} ASTEROID_DB'de bulunamadı!")
        return float('inf')
    if id2 not in ASTEROID_DB:
        print(f"HATA: {id2} ASTEROID_DB'de bulunamadı!")
        return float('inf')
        
    p1, p2 = ASTEROID_DB[id1], ASTEROID_DB[id2]
    return (weights['wa'] * abs(p1['a'] - p2['a']) + weights['we'] * abs(p1['e'] - p2['e']) +
            weights['wi'] * abs(p1['i'] - p2['i']) + weights['wT'] * abs(p1['T_J'] - p2['T_J']))

# Bu fonksiyon artık bu kodda kullanılmıyor ama referans olarak kalabilir
def dijkstra(graph, start_node):
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    previous_nodes = {node: None for node in graph}
    pq = [(0, start_node)]
    
    while pq:
        dist, current_node = heapq.heappop(pq)
        
        if dist > distances[current_node]: continue
        
        for neighbor, weight in graph[current_node].items():
            distance = dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
                
    return distances, previous_nodes

# Bu fonksiyon artık bu kodda kullanılmıyor ama referans olarak kalabilir
def generate_asteroid_metro_map(final_routes, asteroid_graph, asteroid_to_match):
    print("\n\n--- UZAY YOLU METRO HARİTASI ---")
    pass 


def main():
    print(f"Uzaylı Bulmacası Motoru (v4.5 - Tam Matris DB Oluşturucu)...")
    print(f"Veritabanı dosyası '{DB_FILE_NAME}' oluşturuluyor/güncelleniyor...")

    conn = None
    try:
        # 1. Veritabanına bağlan
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()

        # 2. Tabloyu oluştur (eğer yoksa)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CostMatrix (
            From_Asteroid TEXT,
            To_Asteroid TEXT,
            Cost REAL,
            PRIMARY KEY (From_Asteroid, To_Asteroid)
        )
        """)
        
        # 3. Hızlı sorgular için indeks oluştur (eğer yoksa)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_from_to ON CostMatrix (From_Asteroid, To_Asteroid)")
        
        # 4. Benzersiz asteroid ID listesini al
        asteroid_ids = list(ASTEROID_DB.keys())
        num_asteroids = len(asteroid_ids)
        total_calcs = num_asteroids * num_asteroids
        
        print(f"**{num_asteroids}** benzersiz asteroid bulundu.")
        print(f"Toplam {total_calcs} olası maliyet hesaplanacak (N x N)...")
        
        start_time = time.time()
        
        data_to_insert = []
        
        # 5. N x N matrisini hesapla
        for (from_ast, to_ast) in itertools.product(asteroid_ids, repeat=2):
            if from_ast == to_ast:
                cost = 0.0
            else:
                cost = calculate_cost(from_ast, to_ast, WEIGHTS)
                
            data_to_insert.append((from_ast, to_ast, cost))
            
        calc_time = time.time()
        print(f"Tüm {len(data_to_insert)} maliyet {calc_time - start_time:.2f} saniyede hesaplandı.")
        
        # 6. Veritabanını temizle ve tüm veriyi topluca ekle
        print("Eski veriler siliniyor (varsa)...")
        cursor.execute("DELETE FROM CostMatrix")
        
        print(f"{len(data_to_insert)} satır veritabanına yazılıyor...")
        cursor.executemany("INSERT INTO CostMatrix (From_Asteroid, To_Asteroid, Cost) VALUES (?, ?, ?)", data_to_insert)
        
        # 7. Değişiklikleri kaydet
        conn.commit()
        
        end_time = time.time()
        print("\n" + "="*30)
        print("İŞLEM TAMAMLANDI")
        print(f"'{DB_FILE_NAME}' başarıyla oluşturuldu.")
        print(f"Toplam süre: {end_time - start_time:.2f} saniye.")
        print("="*30)
        print("\nManuel kontrol için 'DB Browser for SQLite' gibi bir araçla")
        print(f"bu '{DB_FILE_NAME}' dosyasını açabilirsin.")

    except sqlite3.Error as e:
        print(f"SQLite hatası oluştu: {e}")
        if conn:
            conn.rollback() 
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()