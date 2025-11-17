#!/usr/bin/env python3
# update_prices_single_thread.py

import json
import requests
import time
from datetime import datetime, date

# Tus 147 consumibles
ITEM_IDS = [
    1703,2091,2456,2459,2633,3382,3386,3387,3388,3823,3824,3825,3826,3827,3829,3928,4390,4392,4623,
    5206,5631,5633,5634,5823,6048,6049,6050,6051,6052,6149,6373,6452,6453,6662,7078,7676,8150,8391,
    8392,8393,8394,8396,8831,8951,8956,9030,9036,9088,9144,9155,9172,9179,9187,9206,9224,9264,10305,
    10306,10307,10308,10309,10310,10507,10646,11184,11185,11186,11188,12190,12217,12404,12430,12431,
    12432,12433,12434,12435,12436,12643,12820,13442,13443,13444,13445,13446,13447,13452,13453,13454,
    13455,13456,13457,13458,13459,13460,13461,13462,13506,13510,13511,13512,13513,13928,13931,13935,
    14344,15993,16023,17708,18253,18262,18512,18641,19183,19440,19698,20002,20004,20007,20008,20520,
    20747,20748,20749,20750,21114,21151,21546,22682,23122,23123,47410,47412,47414,50237,51717,51718,
    51720,53015,54010,60976,60977,60978,61174,61175,61181,61198,61199,61224,61225,61423,83309,84040,84041
]

API_URL = "https://api.wowauctions.net/items/stats/30d/south-seas/mergedAh"

# Proxies frescos (actualizados 17/11/2025) + rotación simple
PROXIES = [
    "32.223.6.94:80", "50.122.86.118:80", "35.197.89.213:80", "192.73.244.36:80",
    "4.149.153.123:3128", "159.65.245.255:80", "138.68.60.8:80", "198.199.86.11:80",
    "188.40.57.101:80", "207.154.196.160:8080"
]

def get_price_with_retry(item_id: int, max_retries: int = 3) -> int:
    url = f"{API_URL}/{item_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for attempt in range(1, max_retries + 1):
        # Rotar proxy en cada intento
        proxy_str = PROXIES[(attempt - 1) % len(PROXIES)]
        proxy_dict = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
        
        try:
            r = requests.get(url, proxies=proxy_dict, headers=headers, timeout=20)
            if r.status_code != 200:
                raise Exception(f"Status {r.status_code}")
            
            data = r.json()
            today = date.today().isoformat()
            timestamps = sorted(data.keys(), reverse=True)
            
            # 1. Hoy
            for ts in timestamps:
                if ts.startswith(today) and data[ts].get("min_buy"):
                    price = int(data[ts]["min_buy"])
                    if price > 0:
                        return price
            
            # 2. Último disponible
            for ts in timestamps:
                if data[ts].get("min_buy"):
                    price = int(data[ts]["min_buy"])
                    if price > 0:
                        return price
                        
        except Exception as e:
            if attempt < max_retries:
                time.sleep(3)  # espera antes de reintentar
                continue
        
        # Último intento: sin proxy
        if attempt == max_retries:
            try:
                r = requests.get(url, headers=headers, timeout=20)
                if r.status_code == 200:
                    data = r.json()
                    for ts in sorted(data.keys(), reverse=True):
                        if data[ts].get("min_buy"):
                            price = int(data[ts]["min_buy"])
                            if price > 0:
                                return price
            except:
                pass
    
    return 0  # solo si falló todo

# ===================== MAIN =====================
print(f"Actualizando {len(ITEM_IDS)} consumibles - South Seas (1 hilo + reintentos)")
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Argentina\n")

prices = {}

for i, item_id in enumerate(ITEM_IDS, 1):
    print(f"{i:3}/{len(ITEM_IDS)} | {item_id}", end=" → ")
    price = get_price_with_retry(item_id)
    prices[str(item_id)] = price
    
    if price > 0:
        print(f"{price:,} cobre")
    else:
        print("SIN DATOS (3 intentos fallidos)")

# Guardar resultado
result = {
    "data": prices,
    "last_update": datetime.now().timestamp()
}

with open("southseasprices.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4)

print(f"\n¡TERMINADO! southseasprices.json actualizado.")
print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")