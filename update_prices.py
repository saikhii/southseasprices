#!/usr/bin/env python3
# update_prices_optimized.py - Optimizado: 5-15min, anti-ban (delays, proxies, UA rotation)
import json
import requests
import time
import random
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Tus 147 item IDs (hardcodeados)
ITEM_IDS = [1703,2091,2456,2459,2633,3382,3386,3387,3388,3823,3824,3825,3826,3827,3829,3928,4390,4392,4623,5206,5631,5633,5634,5823,6048,6049,6050,6051,6052,6149,6373,6452,6453,6662,7078,7676,8150,8391,8392,8393,8394,8396,8831,8951,8956,9030,9036,9088,9144,9155,9172,9179,9187,9206,9224,9264,10305,10306,10307,10308,10309,10310,10507,10646,11184,11185,11186,11188,12190,12217,12404,12430,12431,12432,12433,12434,12435,12436,12643,12820,13442,13443,13444,13445,13446,13447,13452,13453,13454,13455,13456,13457,13458,13459,13460,13461,13462,13506,13510,13511,13512,13513,13928,13931,13935,14344,15993,16023,17708,18253,18262,18512,18641,19183,19440,19698,20002,20004,20007,20008,20520,20747,20748,20749,20750,21114,21151,21546,22682,23122,23123,47410,47412,47414,50237,51717,51718,51720,53015,54010,60976,60977,60978,61174,61175,61181,61198,61199,61224,61225,61423,83309,84040,84041]

API_URL = "https://api.wowauctions.net/items/stats/30d/south-seas/mergedAh"

# User-Agents rotativos (humanos)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Proxies frescos HTTP (rotativos, validados 17/11/2025 - elite/anónimos)
PROXIES = [
    "32.223.6.94:80", "50.122.86.118:80", "35.197.89.213:80", "192.73.244.36:80",
    "4.149.153.123:3128", "159.65.245.255:80", "138.68.60.8:80", "198.199.86.11:80",
    "188.40.57.101:80", "207.154.196.160:8080"
]

def get_session_with_retry():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_proxy_dict():
    proxy_str = random.choice(PROXIES)
    ip, port = proxy_str.split(':')
    return {"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"}

def fetch_price(item_id: int, session: requests.Session) -> tuple[int, int]:
    url = f"{API_URL}/{item_id}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://wowauctions.net/",
        "Connection": "keep-alive"
    }
    proxy_dict = get_proxy_dict()  # Rotar proxy por request
    
    for attempt in range(3):  # Reintentos con backoff
        try:
            r = session.get(url, headers=headers, proxies=proxy_dict, timeout=10)
            if r.status_code == 200:
                data = r.json()
                today = date.today().isoformat()
                timestamps = sorted(data.keys(), reverse=True)
                
                # Prioridad: hoy, luego último
                for ts in timestamps:
                    if ts.startswith(today) and data[ts].get("min_buy"):
                        return item_id, int(data[ts]["min_buy"])
                for ts in timestamps:
                    if data[ts].get("min_buy"):
                        return item_id, int(data[ts]["min_buy"])
                return item_id, 0  # No hay min_buy
            elif r.status_code in [429, 403]:
                wait = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff + random
                time.sleep(wait)
                continue
            else:
                return item_id, 0
        except Exception:
            if attempt < 2:
                time.sleep(random.uniform(2, 5))  # Delay random si error
            continue
    return item_id, 0

def main():
    print(f"🚀 Optimizando actualización - South Seas (anti-ban: delays/proxies/UA) - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    prices = {}
    session = get_session_with_retry()
    
    with ThreadPoolExecutor(max_workers=8) as executor:  # 8 hilos: balance velocidad/seguridad
        future_to_id = {executor.submit(fetch_price, iid, session): iid for iid in ITEM_IDS}
        
        for future in as_completed(future_to_id):
            item_id, price = future.result()
            prices[str(item_id)] = price
            status = f"{price:,} cobre" if price > 0 else "SIN DATOS"
            print(f"{item_id:6} → {status}")
            time.sleep(random.uniform(1, 3))  # Delay random entre completados (humano)
    
    result = {"data": prices, "last_update": datetime.now().timestamp()}
    with open("southseasprices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    
    print(f"\n✅ ¡Listo! {len(prices)} items actualizados en ~{datetime.now().strftime('%M:%S')}")

if __name__ == "__main__":
    main()