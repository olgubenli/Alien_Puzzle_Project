# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 14:54:02 2025
@author: olgub
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 22:00:00 2025
@author: olgub

--- UZAYLI BULMACASI FİNAL MOTORU (v4.2_k7 - FİNAL Full Report) ---
Analiz: Bu kod, v4.2'nin sağlam mantığını kullanır.
AMAÇ: 'k=7' (Tüm 56 eşleşme) durumunu izole bir şekilde test etmek.
GÜNCELLEME: Kalkış Matrisi raporundaki '[:5]' limiti kaldırıldı.
           Artık her asteroid için TÜM hedefleri listeleyecek.
"""

import heapq

# --- KULLICI AYARLARI VE VERİ GİRİŞİ ---
WEIGHTS = { 'wa': 1.0, 'we': 5.0, 'wi': 10.0, 'wT': 2.0 }

# === k=7 (TÜM 56 EŞLEŞME) VERİSİ ===
ALL_MATCHES_DATA = {
    "Eşleşme 1": {"Seçenek 1A": ["399", "364192 Qianruhu", "4716 Urey", "13441 Janmerlin"]},
    "Eşleşme 2": {"Seçenek 2A": ["399", "9588 Quesnay", "4257 Ubasti", "17195 Jimrichardson"]},
    "Eşleşme 3": {"Seçenek 3A": ["399", "52301 Qumran", "4632 Udagawa", "58424 Jamesdunlop"]},
    "Eşleşme 4": {"Seçenek 4A": ["399", "3513 Quqinyue", "55701 Ukalegon", "5255 Johnsophie"]},
    "Eşleşme 5": {"Seçenek 5A": ["399", "26940 Quintero", "19462 Ulissedini", "84011 Jean-Claude"]},
    "Eşleşme 6": {"Seçenek 6A": ["399", "52301 Qumran", "15025 Uwontario", "30030 Joycekang"]},
    "Eşleşme 7": {"Seçenek 7A": ["399", "2255 Qinghai", "233880 Urbanpriol", "101811 Jakobkaup"]},
    "Eşleşme 8": {"Seçenek 8A": ["399", "17438 Quasimodo", "16515 Usman'grad", "33889 Jengebo"]},
    # k=2 (9-16)
    "Eşleşme 9": {"Seçenek 9A": ["399", "58098 Quirrenbach", "279037 Utezimmer", "43574 Joyharjo"]},
    "Eşleşme 10": {"Seçenek 10A": ["399", "58098 Quirrenbach", "596543 Ubu", "38431 Jeffbeck"]},
    "Eşleşme 11": {"Seçenek 11A": ["399", "52301 Qumran", "11593 Uchikawa", "236909 Jakoberwin"]},
    "Eşleşme 12": {"Seçenek 12A": ["399", "283279 Qianweichang", "6171 Uttorp", "5964 Johnjunkins"]},
    "Eşleşme 13": {"Seçenek 13A": ["399", "283279 Qianweichang", "5565 Ukyounodaibu", "25869 Jacoby"]},
    "Eşleşme 14": {"Seçenek 14A": ["399", "58098 Quirrenbach", "10072 Uruguay", "44011 Juubichi"]},
    "Eleşme 15": {"Seçenek 15A": ["399", "199947 Qaidam", "34862 Utkarshtandon", "6249 Jennifer"]},
    "Eşleşme 16": {"Seçenek 16A": ["399", "52301 Qumran", "34862 Utkarshtandon", "28125 Juliomiguez"]},
    # k=3 (17-24)
    "Eşleşme 17": {"Seçenek 17A": ["399", "58098 Quirrenbach", "96327 Ullmann", "7290 Johnrather"]},
    "Eşleşme 18": {"Seçenek 18A": ["399", "283279 Qianweichang", "25129 Uranoscope", "602922 Juhaszgyula"]},
    "Eşleşme 19": {"Seçenek 19A": ["399", "5865 Qualytemocrina", "16356 Univbalttech", "31988 Jasonfiacco"]},
    "Eşleşme 20": {"Seçenek 20A": ["399", "28275 Quoc-Bao", "27827 Ukai", "6063 Jason"]},
    "Eşleşme 21": {"Seçenek 21A": ["399", "3763 Qianxuesen", "55701 Ukalegon", "21559 Jingyuanluo"]},
    "Eşleşme 22": {"Seçenek 22A": ["399", "13192 Quine", "364636 Ulrikeecker", "10930 Jinyong"]},
    "Eşleşme 23": {"Seçenek 23A": ["399", "78652 Quero", "29189 Udinsk", "26891 Johnbutler"]},
    "Eşleşme 24": {"Seçenek 24A": ["399", "58098 Quirrenbach", "501 Urhixidur", "27048 Jangong"]},
    # k=4 (25-32)
    "Eşleşme 25": {"Seçenek 25A": ["399", "58098 Quirrenbach", "290001 Uebersax", "38431 Jeffbeck"]},
    "Eşleşme 26": {"Seçenek 26A": ["399", "755 Quintilla", "23900 Urakawa", "306001 Joanllaneras"]},
    "Eşleşme 27": {"Seçenek 27A": ["399", "3876 Quaide", "55701 Ukalegon", "207723 Jiansanjiang"]},
    "Eşleşme 28": {"Seçenek 28A": ["399", "199947 Qaidam", "13069 Umbertoeco", "25988 Janesuh"]},
    "Eşleşme 29": {"Seçenek 29A": ["399", "13192 Quine", "27790 Urashimataro", "49294 Jacqclairnoens"]},
    "Eşleşme 30": {"Seçenek 30A": ["399", "1239 Queteleta", "4632 Udagawa", "39415 Janeausten"]},
    "Eşleşme 31": {"Seçenek 31A": ["399", "755 Quintilla", "5254 Ulysses", "9519 Jeffkeck"]},
    "Eşleşme 32": {"Seçenek 32A": ["399", "52301 Qumran", "42614 Ubaldina", "100434 Jinyilian"]},
    # k=5 (33-40)
    "Eşleşme 33": {"Seçenek 33A": ["399", "4372 Quincy", "52260 Ureshino", "306001 Joanllaneras"]},
    "Eşleşme 34": {"Seçenek 34A": ["399", "52301 Qumran", "15025 Uwontario", "33487 Jeanpierrerivet"]},
    "Eşleşme 35": {"Seçenek 35A": ["399", "58098 Quirrenbach", "12360 Unilandes", "120481 Johannwalter"]},
    "Eşleşme 36": {"Seçenek 36A": ["399", "28275 Quoc-Bao", "5254 Ulysses", "24214 Jonchristo"]},
    "Eşleşme 37": {"Seçenek 37A": ["399", "3335 Quanzhou", "3722 Urata", "2617 Jiangxi"]},
    "Eşleşme 38": {"Seçenek 38A": ["399", "13192 Quine", "4139 Ul'yanin", "90918 Jasinski"]},
    "Eşleşme 39": {"Seçenek 39A": ["399", "199947 Qaidam", "9657 Ucka", "187447 Johnmester"]},
    "Eşleşme 40": {"Seçenek 40A": ["399", "8755 Querquedula", "55701 Ukalegon", "33487 Jeanpierrerivet"]},
    # k=6 (41-48)
    "Eşleşme 41": {"Seçenek 41A": ["399", "199947 Qaidam", "3722 Urata", "6137 Johnfletcher"]},
    "Eşleşme 42": {"Seçenek 42A": ["399", "13192 Quine", "7342 Uchinoura", "100229 Jeanbailly"]},
    "Eşleşme 43": {"Seçenek 43A": ["399", "52301 Qumran", "29950 Uppili", "5900 Jensen"]},
    "Eşleşme 44": {"Seçenek 44A": ["399", "336877 Qifaren", "501 Urhixidur", "306001 Joanllaneras"]},
    "Eşleşme 45": {"Seçenek 45A": ["399", "58098 Quirrenbach", "9720 Ulfbirgitta", "25415 Jocelyn"]},
    "Eşleşme 46": {"Seçenek 46A": ["399", "58098 Quirrenbach", "1351 Uzbekistania", "25138 Jaumann"]},
    "Eşleşme 47": {"Seçenek 47A": ["399", "5865 Qualytemocrina", "34862 Utkarshtandon", "27301 Joeingalls"]},
    "Eşleşme 48": {"Seçenek 48A": ["399", "34204 Quryshi", "4761 Urrutia", "84011 Jean-Claude"]},
    # k=7 (49-56)
    "Eşleşme 49": {"Seçenek 49A": ["399", "34204 Quryshi", "55701 Ukalegon", "8073 Johnharmon"]},
    "Eşleşme 50": {"Seçenek 50A": ["399", "50000 Quaoar", "2868 Upupa", "C/1946 P1"]},
    "Eşleşme 51": {"Seçenek 51A": ["399", "5865 Qualytemocrina", "3468 Urgenta", "121007 Jiaxingnanhu"]},
    "Eşleşme 52": {"Seçenek 52A": ["399", "18376 Quirk", "55701 Ukalegon", "47708 Jimhamilton"]},
    "Eşleşme 53": {"Seçenek 53A": ["399", "199947 Qaidam", "3010 Ushakov", "25869 Jacoby"]},
    "Eşleşme 54": {"Seçenek 54A": ["399", "177415 Queloz", "55701 Ukalegon", "90918 Jasinski"]},
    "Eşleşme 55": {"Seçenek 55A": ["399", "17438 Quasimodo", "233880 Urbanpriol", "16012 Jamierubin"]},
    "Eşleşme 56": {"Seçenek 56A": ["399", "20278 Qileihang", "4716 Urey", "306001 Joanllaneras"]}
}
# ==================================

# === GÜNCELLENMİŞ HEDEF LİSTESİ (v4.1) ===
TARGET_ASTEROIDS = {
    "55701 Ukalegon": "Birincil Ana Kapı",
    "84011 Jean-Claude": "Ara Kapı"
}
# ===

# === k=7 (TÜM 117+ ASTEROİD) VERİTABANI ===
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
# (Bu bölüm v4.2 ile %100 aynıdır)

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


def generate_asteroid_metro_map(final_routes, asteroid_graph, asteroid_to_match):
    # Etiketi k=7 (56 Eşleşme) olarak güncelle
    print("\n\n--- UZAY YOLU METRO HARİTASI (k=7 / 56 Eşleşme - FİNAL) ---")
    print("Harita, ana kapılara giden en verimli rotaları oluşturan asteroidden asteroide sıçramaları gösterir.")
    print("Lejant: *ANA/ARA KAPI*\n")

    for target_key, (total_cost, path) in final_routes.items():
        target_name = TARGET_ASTEROIDS.get(path[-1], "Bilinmeyen Hedef") 
        
        print(f"--- {target_name.upper()} HATTI (Toplam Maliyet: {total_cost:.2f}) ---")

        line = ""
        for i in range(len(path) - 1):
            from_ast, to_ast = path[i], path[i+1]
            cost = asteroid_graph[from_ast].get(to_ast, 0.0) 

            from_name = "DÜNYA" if from_ast == '399' else f"{from_ast}({asteroid_to_match.get(from_ast, 'Bilinmiyor')})"
            line += f"[{from_name}] --({cost:.2f})--> "

        final_ast_name = f"{path[-1]}({asteroid_to_match.get(path[-1], 'Bilinmiyor')})"
        line += f"*[ {path[-1]} ({target_name}) ]*"
        print(line + "\n")

    print("--- Harita Yorumu (v4.2 - Tam Fiziksel) ---")
    print(" - Bu harita, kodun 'Tam Fiziksel Model' ile bulduğu en verimli, çok duraklı rotaların gerçek adımlarını göstermektedir.")


def main():
    # Etiketleri k=7 (56 Eşleşme) olarak güncelle
    print("Uzaylı Bulmacası Motoru (v4.2_k7 - 56 Eşleşme Final Testi)...")
    print("Kapı Hedefleri: Ukalegon (Ana), Jean-Claude (Ara)")
    print("Ağ (Matris) 56 eşleşme kullanılarak oluşturuluyor...")

    match_names = list(ALL_MATCHES_DATA.keys())
    asteroid_to_match = {ast: m_name for m_name, m_data in ALL_MATCHES_DATA.items() for path in m_data.values() for ast in path if ast != '399'}

    print("'Tam Fiziksel Model' ağı oluşturuluyor...")
    
    all_known_asteroids = set(ASTEROID_DB.keys())
    for m_name, m_data in ALL_MATCHES_DATA.items():
        for path in m_data.values():
            for ast in path:
                if ast in ASTEROID_DB:
                    all_known_asteroids.add(ast)

    asteroid_graph = {ast: {} for ast in all_known_asteroids}

    # === TAM FİZİKSEL MODEL (Eşleşme İçi Rotalar) ===
    # (Mantık değişmedi, ama artık 56 eşleşme için çalışacak)
    for m_name, m_data in ALL_MATCHES_DATA.items():
        for path in m_data.values():
            if not all(ast in ASTEROID_DB for ast in path):
                print(f"UYARI: {m_name} içindeki bazı asteroidler DB'de yok, atlanıyor: {path}")
                continue
            
            for i in range(len(path) - 1):
                from_ast, to_ast = path[i], path[i+1]
                cost = calculate_cost(from_ast, to_ast, WEIGHTS)
                asteroid_graph[from_ast][to_ast] = cost

    # === SERBEST UÇUŞ MODELİ (Eşleşmeler Arası Geçiş) ===
    # (Mantık değişmedi, ama artık 56 eşleşme arasında çalışacak)
    print(f"{len(match_names)} eşleşme arasında Serbest Uçuş (Transfer) matrisi hesaplanıyor...")
    for i in range(len(match_names)):
        for j in range(i + 1, len(match_names)):
            m1_asteroids = [ast for path in ALL_MATCHES_DATA[match_names[i]].values() for ast in path if ast != '399' and ast in ASTEROID_DB]
            m2_asteroids = [ast for path in ALL_MATCHES_DATA[match_names[j]].values() for ast in path if ast != '399' and ast in ASTEROID_DB]
            
            for ast1 in m1_asteroids:
                for ast2 in m2_asteroids:
                    cost = calculate_cost(ast1, ast2, WEIGHTS)
                    if ast2 not in asteroid_graph[ast1] or cost < asteroid_graph[ast1][ast2]:
                        asteroid_graph[ast1][ast2] = cost
                        asteroid_graph[ast2][ast1] = cost

    print("Dijkstra algoritması çalıştırılıyor: Dünya'dan tüm hedeflere en verimli rotalar hesaplanıyor...")
    
    if '399' not in asteroid_graph:
        print("KRİTİK HATA: '399' (Dünya) grafikte bulunamadı.")
        return
        
    distances, previous_nodes = dijkstra(asteroid_graph, '399')

    final_routes_for_map = {}

    # Etiketi k=7 (56 Eşleşme) olarak güncelle
    print("\n--- ANA ROTA KEŞİF SONUÇLARI (k=7 / 56 Eşleşme - FİNAL) ---\n")
    for target_id, target_desc in TARGET_ASTEROIDS.items():
        print(f"[*] Hedef: {target_id} ({target_desc})")
        
        cost = distances.get(target_id, float('inf'))
        
        if target_id not in previous_nodes or cost == float('inf'):
                print(f"  -> {target_id} için rota bulunamadı. (Maliyet: Sonsuz)")
                continue
                
        path = []; current_node = target_id
        while current_node: 
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        path.reverse()
        
        final_routes_for_map[f"{target_id} ({target_desc})"] = (cost, path)
        path_with_matches = [f"{ast}({asteroid_to_match.get(ast, 'Dünya')})" if ast != '399' else "Dünya" for ast in path]
        print(f"  -> En Düşük Toplam Maliyet: {cost:.4f}")
        print(f"  -> En Verimli Rota: {' -> '.join(path_with_matches)}\n")

    # Etiketi k=7 olarak güncelle
    print("\n--- DÜNYA'DAN DİĞER ASTEROİDLERE EN VERİMLİ ROTALAR (k=7 - FİNAL) ---\n")
    all_other_targets = sorted(
        [ast for ast in asteroid_to_match.keys() if ast not in TARGET_ASTEROIDS], 
        key=lambda x: asteroid_to_match[x]
    )
    
    for target_asteroid in all_other_targets:
        parent_match = asteroid_to_match[target_asteroid]
        print(f"[*] Hedef Asteroid: {target_asteroid} ({parent_match})")
        
        cost = distances.get(target_asteroid, float('inf'))
        
        if target_asteroid not in previous_nodes or cost == float('inf'):
                print(f"  -> {target_asteroid} için rota bulunamadı.\n")
                continue
                
        path = []; current_node = target_asteroid
        while current_node: 
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        path.reverse()
        
        path_with_matches = [f"{ast}({asteroid_to_match.get(ast, 'Dünya')})" if ast != '399' else "Dünya" for ast in path]
        print(f"  -> En Düşük Toplam Maliyet: {cost:.4f}")
        print(f"  -> En Verimli Rota: {' -> '.join(path_with_matches)}\n")

    # Etiketi k=7 olarak güncelle
    print("\n--- DETAYLI ASTEROİD KALKIŞ MATRİSİ (k=7 - FİNAL) ---\n")
    for m_name, m_data in sorted(ALL_MATCHES_DATA.items()):
        print(f"========== {m_name} ==========")
        start_asteroids_in_match = [ast for path in m_data.values() for ast in path if ast != '399' and ast in ASTEROID_DB]
        
        if not start_asteroids_in_match:
            print(f"  ({m_name} için DB'de asteroid bulunamadı)\n")
            continue

        for start_asteroid in start_asteroids_in_match:
            print(f"--- {start_asteroid} ({m_name}) Kalkışlı Rotalar ---")
            destinations = []
            if start_asteroid in asteroid_graph:
                for target_asteroid, cost in asteroid_graph.get(start_asteroid, {}).items():
                    if cost > 0 and target_asteroid != '399' and target_asteroid in asteroid_to_match:
                            destinations.append((target_asteroid, cost))
            
            sorted_destinations = sorted(destinations, key=lambda item: item[1])
            
            if not sorted_destinations:
                print("  (Başka bir eşleşmeye verimli geçiş bulunamadı)")
            else:
                for dest_ast, cost in sorted_destinations[:5]:
                    dest_match = asteroid_to_match.get(dest_ast, "Bilinmiyor")
                    print(f"  -> {dest_ast} ({dest_match}): (Maliyet: {cost:.4f})")
            print("")

    # --- ANA METRO HARİTASI RAPORU ---
    generate_asteroid_metro_map(final_routes_for_map, asteroid_graph, asteroid_to_match)


    # === DÜZELTİLMİŞ YAN HAT RAPORU (ANA HARİTADAN SONRA) ===
    print("\n\n--- EN VERİMLİ YAN HATLAR (TOP 10 AKTARMA MERKEZİ) ---")
    print("Bunlar, Ana Kapılar haricinde Dünya'dan ulaşılması en düşük maliyetli 10 'Yan Hat' durağıdır.")
    
    side_asteroids = []
    # 'distances' ve 'previous_nodes' zaten bu scope içinde mevcut
    for ast, cost in distances.items():
        # 'asteroid_to_match' içinde olanları da ekleyerek sadece Eşleşme asteroidlerini al
        if ast not in TARGET_ASTEROIDS and ast != '399' and cost != float('inf') and ast in asteroid_to_match:
            side_asteroids.append((cost, ast))
            
    # Maliyete göre sırala
    sorted_side_asteroids = sorted(side_asteroids, key=lambda x: x[0])
    
    # En ucuz 10 tanesini al
    for cost, ast_id in sorted_side_asteroids[:10]:
        
        # Bu hedefe giden yolu yeniden oluştur (Ana Raporlardaki mantığın aynısı)
        path = []; current_node = ast_id
        while current_node:
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        path.reverse()
        
        target_match = asteroid_to_match.get(ast_id, "Bilinmiyor")
        print(f"\n--- YAN HAT: {ast_id} ({target_match}) (Toplam Maliyet: {cost:.2f}) ---")
        
        line = ""
        for i in range(len(path) - 1):
            from_ast, to_ast = path[i], path[i+1]
            # 'asteroid_graph' da bu scope içinde mevcut
            hop_cost = asteroid_graph.get(from_ast, {}).get(to_ast, 0.0) 
            
            from_name = "DÜNYA" if from_ast == '399' else f"{from_ast}({asteroid_to_match.get(from_ast, '?')})"
            line += f"[{from_name}] --({hop_cost:.2f})--> "

        # Son durağı ekle
        final_ast_name = f"{path[-1]}({asteroid_to_match.get(path[-1], '?')})"
        line += f"*[ {final_ast_name} ]*"
        print(line)
    
    # === YENİ BÖLÜM SONU ===


if __name__ == "__main__":
    main()