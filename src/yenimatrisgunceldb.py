# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 16:38:54 2025
@author: olgub

--- UZAYLI BULMACASI FİNAL MOTORU (v4.2 - Tam Fiziksel Model) ---
Güncelleme: Tisserand/Lagrange analizine göre hedef kapılar güncellendi.
    - Birincil Ana Kapı: (55701) Ukalegon (L5 Kavşağı)
    - Ara Kapı: (84011) Jean-Claude (Hilda Rampası)
Güncelleme v4.2: Hibrit (0.0 maliyet) modeli kaldırıldı. 
Tüm "Eşleşme" adımları artık gerçek fiziksel maliyetleriyle hesaplanıyor.
"""

import heapq

# --- KULLICI AYARLARI VE VERİ GİRİŞİ ---
WEIGHTS = { 'wa': 1.0, 'we': 5.0, 'wi': 10.0, 'wT': 2.0 }
ALL_MATCHES_DATA = {
    "Eşleşme 1": {"Seçenek 1A": ["399", "364192 Qianruhu", "4716 Urey", "13441 Janmerlin"]},
    "Eşleşme 2": {"Seçenek 2A": ["399", "9588 Quesnay", "4257 Ubasti", "17195 Jimrichardson"]},
    "Eşleşme 3": {"Seçenek 3A": ["399", "52301 Qumran", "4632 Udagawa", "58424 Jamesdunlop"]},
    "Eşleşme 4": {"Seçenek 4A": ["399", "3513 Quqinyue", "55701 Ukalegon", "5255 Johnsophie"]},
    "Eşleşme 5": {"Seçenek 5A": ["399", "26940 Quientero", "19462 Ulissedini", "84011 Jean-Claude"]},
    "Eşleşme 6": {"Seçenek 6A": ["399", "52301 Qumran", "15025 Uwontario", "30030 Joycekong"]},
    "Eşleşme 7": {"Seçenek 7A": ["399", "2255 Qinghai", "233880 Urbanpriol", "101811 Jakobkaup"]},
    "Eşleşme 8": {"Seçenek 8A": ["399", "17438 Quasimodo", "16515 Usman'grad", "33889 Jengebo"]}
}

# === GÜNCELLENMİŞ HEDEF LİSTESİ (v4.1) ===
# Tisserand/Lagrange analizine göre yeni hedeflerimiz:
TARGET_ASTEROIDS = { 
    "55701 Ukalegon": "Birincil Ana Kapı",  # L5 Kavşağı (TJ=2.850)
    "84011 Jean-Claude": "Ara Kapı"            # Hilda Rampası (TJ=2.995)
}
# ===

# --- GÜNCELLENMİŞ VERİTABANI (v4.0) ---
ASTEROID_DB = {
    '399': {'a': 1.0000, 'e': 0.0167, 'i': 0.0000, 'T_J': 6.138},
    '364192 Qianruhu': {'a': 2.3914, 'e': 0.2037, 'i': 3.6357, 'T_J': 3.501},
    '4716 Urey': {'a': 3.1879, 'e': 0.1277, 'i': 10.1100, 'T_J': 3.161},
    '13441 Janmerlin': {'a': 2.6311, 'e': 0.2622, 'i': 11.9332, 'T_J': 3.320},
    '9588 Quesnay': {'a': 2.5879, 'e': 0.2141, 'i': 13.1807, 'T_J': 3.352},
    '4257 Ubasti': {'a': 1.6471, 'e': 0.4684, 'i': 40.7218, 'T_J': 3.913},
    '17195 Jimrichardson': {'a': 3.2244, 'e': 0.1120, 'i': 6.0845, 'T_J': 3.169},
    '52301 Qumran': {'a': 2.3137, 'e': 0.2288, 'i': 5.4007, 'T_J': 3.541},
    '4632 Udagawa': {'a': 2.2060, 'e': 0.1724, 'i': 6.4908, 'T_J': 3.633},
    '58424 Jamesdunlop': {'a': 2.5350, 'e': 0.1505, 'i': 4.6026, 'T_J': 3.428},
    '3513 Quqinyue': {'a': 2.6290, 'e': 0.0100, 'i': 2.6481, 'T_J': 3.399},
    '55701 Ukalegon': {'a': 5.1658, 'e': 0.1408, 'i': 20.9572, 'T_J': 2.850},
    '5255 Johnsophie': {'a': 2.6726, 'e': 0.0167, 'i': 11.6220, 'T_J': 3.351},
    '26940 Quientero': {'a': 2.6074, 'e': 0.1741, 'i': 15.4243, 'T_J': 3.361}, # Hata vermemesi için eklendi (Eşleşme 5)
    '19462 Ulissedini': {'a': 2.9093, 'e': 0.1040, 'i': 2.2213, 'T_J': 3.275},
    '84011 Jean-Claude': {'a': 4.0092, 'e': 0.2464, 'i': 4.0115, 'T_J': 2.995},
    '15025 Uwontario': {'a': 3.1976, 'e': 0.1082, 'i': 7.2771, 'T_J': 3.173},
    '30030 Joycekong': {'a': 2.5714, 'e': 0.1557, 'i': 4.3418, 'T_J': 3.415}, # Hata vermemesi için eklendi (Eşleşme 6)
    '2255 Qinghai': {'a': 3.1053, 'e': 0.1466, 'i': 14.1374, 'T_J': 3.158},
    '233880 Urbanpriol': {'a': 3.1907, 'e': 0.1641, 'i': 5.4938, 'T_J': 3.169},
    '101811 Jakobkaup': {'a': 2.3633, 'e': 0.3214, 'i': 22.1978, 'T_J': 3.383},
    '17438 Quasimodo': {'a': 2.3226, 'e': 0.1324, 'i': 3.3247, 'T_J': 3.563},
    '16515 Usman\'grad': {'a': 3.1639, 'e': 0.1749, 'i': 2.2403, 'T_J': 3.179},
    '33889 Jengebo': {'a': 2.2326, 'e': 0.1812, 'i': 6.5094, 'T_J': 3.611}
}

# --- ANALİZ MOTORU KODU ---
def calculate_cost(id1, id2, weights):
    # ID'lerin DB'de olup olmadığını kontrol et (Hata ayıklama için)
    if id1 not in ASTEROID_DB:
        print(f"HATA: {id1} ASTEROID_DB'de bulunamadı!")
        return float('inf')
    if id2 not in ASTEROID_DB:
        print(f"HATA: {id2} ASTEROID_DB'de bulunamadı!")
        return float('inf')
        
    p1, p2 = ASTEROID_DB[id1], ASTEROID_DB[id2]
    return (weights['wa'] * abs(p1['a'] - p2['a']) + weights['we'] * abs(p1['e'] - p2['e']) +
            weights['wi'] * abs(p1['i'] - p2['i']) + weights['wT'] * abs(p1['T_J'] - p2['T_J']))

def dijkstra(graph, start_node):
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0; previous_nodes = {node: None for node in graph}
    pq = [(0, start_node)]
    while pq:
        dist, current_node = heapq.heappop(pq)
        if dist > distances[current_node]: continue
        for neighbor, weight in graph[current_node].items():
            distance = dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance; previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    return distances, previous_nodes

# === YENİ METRO HARİTASI FONKSİYONU (ASTEROİD BAZLI) ===
def generate_asteroid_metro_map(final_routes, asteroid_graph, asteroid_to_match):
    print("\n\n--- UZAY YOLU METRO HARİTASI (Asteroid Bazlı) ---")
    print("Harita, ana kapılara giden en verimli rotaları oluşturan asteroidden asteroide sıçramaları gösterir.")
    print("Lejant: *ANA/ARA KAPI*\n")

    for target_key, (total_cost, path) in final_routes.items():
        # Hedef ismini etiketten (parantez içinden) alır
        target_name = TARGET_ASTEROIDS.get(path[-1], "Bilinmeyen Hedef") 
        
        print(f"--- {target_name.upper()} HATTI (Toplam Maliyet: {total_cost:.2f}) ---")

        line = ""
        for i in range(len(path) - 1):
            from_ast, to_ast = path[i], path[i+1]
            # Grafikten gerçek maliyeti al (artık 0.0 değil)
            cost = asteroid_graph[from_ast].get(to_ast, 0.0) 

            from_name = "DÜNYA" if from_ast == '399' else f"{from_ast}({asteroid_to_match.get(from_ast)})"
            line += f"[{from_name}] --({cost:.2f})--> "

        final_ast_name = f"{path[-1]}({asteroid_to_match.get(path[-1])})"
        line += f"*[ {path[-1]} ({target_name}) ]*"
        print(line + "\n")

    print("--- Harita Yorumu (v4.2 - Tam Fiziksel) ---")
    print(" - Bu harita, kodun 'Tam Fiziksel Model' ile bulduğu en verimli, çok duraklı rotaların gerçek adımlarını göstermektedir.")
    print(" - Maliyetler, rotayı oluşturan her bir sıçramanın (hop) bireysel ve gerçek maliyetidir.")
    print(" - Eşleşme içi '0.00' maliyet kuralı kaldırılmıştır.")

def main():
    print("Uzaylı Bulmacası Final Motoru (v4.2 - Tam Fiziksel Model)...")
    print("Kapı Hedefleri Güncellendi: Ukalegon (Ana), Jean-Claude (Ara)")

    match_names = list(ALL_MATCHES_DATA.keys())
    asteroid_to_match = {ast: m_name for m_name, m_data in ALL_MATCHES_DATA.items() for path in m_data.values() for ast in path if ast != '399'}

    print("'Tam Fiziksel Model' ağı oluşturuluyor (Hibrit kuralı kaldırıldı)...")
    
    # Koddaki tüm asteroidlerin (DB ve Maçlar) DB'de olduğundan emin ol
    all_known_asteroids = set(ASTEROID_DB.keys())
    for m_name, m_data in ALL_MATCHES_DATA.items():
        for path in m_data.values():
            for ast in path:
                all_known_asteroids.add(ast)

    asteroid_graph = {ast: {} for ast in all_known_asteroids if ast in ASTEROID_DB}

    # === TAM FİZİKSEL MODEL DEĞİŞİKLİĞİ (v4.2) ===
    # '0.0' maliyetli hibrit kuralı kaldırıldı.
    # Artık 'ALL_MATCHES_DATA' içindeki her adım, gerçek maliyetiyle hesaplanıyor.
    for m_name, m_data in ALL_MATCHES_DATA.items():
        for path in m_data.values():
            # 'path' içindeki tüm asteroidlerin DB'de olup olmadığını BAŞTAN KONTROL ET
            if not all(ast in ASTEROID_DB for ast in path):
                print(f"UYARI: {m_name} içindeki bazı asteroidler DB'de yok, atlanıyor: {path}")
                continue
            
            # 'path' geçerliyse, "Tam Fiziksel" mantığıyla her adımı (0. indis dahil) hesapla
            for i in range(len(path) - 1):
                from_ast, to_ast = path[i], path[i+1]
                # Gerçek maliyeti hesapla ve grafa ekle
                cost = calculate_cost(from_ast, to_ast, WEIGHTS)
                asteroid_graph[from_ast][to_ast] = cost
                # Not: Bu, 'path' tarafından tanımlanan tek yönlü bir yoldur.
                # Serbest uçuşlar (aşağıdaki döngü) bunu çift yönlü hale getirecektir.

    # === SERBEST UÇUŞ MODELİ (EŞLEŞMELER ARASI GEÇİŞ) ===
    # Bu bölüm, eşleşmeler arası 'serbest uçuş' maliyetlerini hesaplar.
    # Bu mantık değişmedi, hala gerekli.
    for i in range(len(match_names)):
        for j in range(i + 1, len(match_names)):
            m1_asteroids = [ast for path in ALL_MATCHES_DATA[match_names[i]].values() for ast in path if ast != '399' and ast in ASTEROID_DB]
            m2_asteroids = [ast for path in ALL_MATCHES_DATA[match_names[j]].values() for ast in path if ast != '399' and ast in ASTEROID_DB]
            for ast1 in m1_asteroids:
                for ast2 in m2_asteroids:
                    cost = calculate_cost(ast1, ast2, WEIGHTS)
                    if ast2 not in asteroid_graph[ast1] or cost < asteroid_graph[ast1][ast2]:
                        asteroid_graph[ast1][ast2] = cost; asteroid_graph[ast2][ast1] = cost

    print("Dijkstra algoritması çalıştırılıyor: Dünya'dan tüm hedeflere en verimli rotalar hesaplanıyor...")
    distances, previous_nodes = dijkstra(asteroid_graph, '399')

    final_routes_for_map = {}

    print("\n--- ANA ROTA KEŞİF SONUÇLARI (Güncellenmiş Kapılar) ---\n")
    for target_id, target_desc in TARGET_ASTEROIDS.items():
        print(f"[*] Hedef: {target_id} ({target_desc})")
        
        if target_id not in previous_nodes or distances.get(target_id, float('inf')) == float('inf'):
             print(f"  -> {target_id} için rota bulunamadı. DB'de, Eşleşmelerde eksik veya ulaşılamaz olabilir.")
             continue
             
        path = []; current_node = target_id
        while current_node: 
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        path.reverse()
        
        final_routes_for_map[f"{target_id} ({target_desc})"] = (distances.get(target_id, float('inf')), path)
        path_with_matches = [f"{ast}({asteroid_to_match.get(ast, 'Dünya')})" if ast != '399' else "Dünya" for ast in path]
        print(f"  -> En Düşük Toplam Maliyet: {distances.get(target_id, float('inf')):.4f}")
        print(f"  -> En Verimli Rota: {' -> '.join(path_with_matches)}\n")

    print("\n--- DÜNYA'DAN HER BİR ASTEROİDE EN VERİMLİ ROTALAR ---\n")
    all_other_targets = sorted(
        [ast for ast in asteroid_to_match.keys() if ast not in TARGET_ASTEROIDS], 
        key=lambda x: asteroid_to_match[x]
    )
    
    for target_asteroid in all_other_targets:
        parent_match = asteroid_to_match[target_asteroid]
        print(f"[*] Hedef Asteroid: {target_asteroid} ({parent_match})")
        
        if target_asteroid not in previous_nodes or distances.get(target_asteroid, float('inf')) == float('inf'):
             print(f"  -> {target_asteroid} için rota bulunamadı. DB'de veya Eşleşmelerde eksik olabilir.\n")
             continue
             
        path = []; current_node = target_asteroid
        while current_node: 
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        path.reverse()
        
        path_with_matches = [f"{ast}({asteroid_to_match.get(ast, 'Dünya')})" if ast != '399' else "Dünya" for ast in path]
        print(f"  -> En Düşük Toplam Maliyet: {distances.get(target_asteroid, float('inf')):.4f}")
        print(f"  -> En Verimli Rota: {' -> '.join(path_with_matches)}\n")

    print("\n--- DETAYLI ASTEROİD KALKIŞ MATRİSİ ---\n")
    for m_name, m_data in sorted(ALL_MATCHES_DATA.items()):
        print(f"========== {m_name} ==========")
        start_asteroids_in_match = [ast for path in m_data.values() for ast in path if ast != '399' and ast in ASTEROID_DB]
        
        if not start_asteroids_in_match:
            print(f"  ({m_name} için DB'de asteroid bulunamadı)")
            print("")
            continue

        for start_asteroid in start_asteroids_in_match:
            print(f"--- {start_asteroid} ({m_name}) Kalkışlı Rotalar ---")
            destinations = []
            # Grafikte bu asteroidden ÇIKIŞ maliyetlerini ara
            if start_asteroid in asteroid_graph:
                for target_asteroid, cost in asteroid_graph.get(start_asteroid, {}).items():
                    if cost > 0 and target_asteroid != '399':
                            destinations.append((target_asteroid, cost))
            
            sorted_destinations = sorted(destinations, key=lambda item: item[1])
            
            if not sorted_destinations: 
                print("  (Başka bir eşleşmeye verimli geçiş bulunamadı)")
            else:
                for dest_ast, cost in sorted_destinations[:5]:
                    dest_match = asteroid_to_match.get(dest_ast, "Bilinmiyor")
                    print(f"  -> {dest_ast} ({dest_match}): (Maliyet: {cost:.4f})")
            print("")

    generate_asteroid_metro_map(final_routes_for_map, asteroid_graph, asteroid_to_match)

if __name__ == "__main__":
    main()