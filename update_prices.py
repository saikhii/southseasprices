#!/usr/bin/env python3
# southseas_codespaces_fixed.py - Versión anti-bloqueo para Codespaces (17/11/2025)
# Ejecutar: python southseas_codespaces_fixed.py

import json
import requests
import random
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed

# Tus 147 consumibles (hardcodeados)
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

# Lista fresca de proxies HTTP (elite/anónimos, validados 17/11/2025)
PROXIES = [
    "32.223.6.94:80", "50.122.86.118:80", "35.197.89.213:80", "192.73.244.36:80", "4.149.153.123:3128",
    "47.252.29.28:11222", "159.65.245.255:80", "209.97.150.167:8080", "138.68.60.8:80", "198.199.86.11:80",
    "188.40.57.101:80", "81.169.213.169:8888", "207.154.196.160:8080", "35.181.173.74:9443", "77.105.137.42:8080"
]

def get_proxy_dict(proxy_str):
    """Convierte 'IP:PORT' a dict para requests."""
    if not proxy_str:
        return None
    ip, port = proxy_str.split(':')
    return {"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"}

def validate_proxy_for_api(proxy_str):
    """Valida si el proxy responde a la API de wowauctions (prueba rápida con un ítem)."""
    proxy_dict = get_proxy_dict(proxy_str)
    try:
        test_url = f"{API_URL}/13510"  # Flask of the Titans como test
        r = requests.get(test_url, proxies=proxy_dict, timeout=8)
        return r.status_code == 200
    except:
        return False

def fetch_price(item_id: int) -> tuple[int, int]:
    """Intenta fetch con proxies rotativos + fallback sin proxy."""
    url = f"{API_URL}/{item_id}"
    # Lista de proxies para este ítem (random + shuffle para rotación)
    available_proxies = [p for p in PROXIES if validate_proxy_for_api(p)]
    random.shuffle(available_proxies)
    
    # Prueba hasta 5 proxies
    for i, proxy in enumerate(available_proxies[:5]):
        proxy_dict = get_proxy_dict(proxy)
        try:
            r = requests.get(url, proxies=proxy_dict, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                today = date.today().isoformat()
                timestamps = sorted(data.keys(), reverse=True)
                
                # Hoy primero
                for ts in timestamps:
                    if ts.startswith(today) and data[ts].get("min_buy"):
                        return item_id, int(data[ts]["min_buy"])
                # Último disponible
                for ts in timestamps:
                    if data[ts].get("min_buy"):
                        return item_id, int(data[ts]["min_buy"])
                break  # Si llegó hasta acá, proxy OK pero no hay min_buy
        except:
            continue
    
    # Fallback: sin proxy (a veces pasa en Codespaces)
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            data = r.json()
            today = date.today().isoformat()
            timestamps = sorted(data.keys(), reverse=True)
            for ts in timestamps:
                if ts.startswith(today) and data[ts].get("min_buy"):
                    return item_id, int(data[ts]["min_buy"])
            for ts in timestamps:
                if data[ts].get("min_buy"):
                    return item_id, int(data[ts]["min_buy"])
    except:
        pass
    
    return item_id, 0

def main():
    print(f"🚀 Actualizando {len(ITEM_IDS)} consumibles en Codespaces - South Seas (anti-bloqueo ON)")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Proxies disponibles: {len(PROXIES)}\n")
    
    prices = {}
    with ThreadPoolExecutor(max_workers=15) as executor:  # Menos hilos para estabilidad
        future_to_id = {executor.submit(fetch_price, iid): iid for iid in ITEM_IDS}
        
        for future in as_completed(future_to_id):
            item_id, price = future.result()
            prices[str(item_id)] = price
            status = f"{price:,} cobre" if price > 0 else "SIN DATOS"
            print(f"{item_id:6} → {status}")

    result = {
        "data": prices,
        "last_update": datetime.now().timestamp()
    }

    with open("southseasprices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print(f"\n✅ ¡LISTO! southseasprices.json generado. Chequeá errores arriba si hay 'SIN DATOS'.")
    print("Si sigue fallando >50%, probá ejecutar en tu máquina local sin Codespaces.")

if __name__ == "__main__":
    main()