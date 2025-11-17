#!/usr/bin/env python3
# update_southseas_prices.py
# Ejecutar con: python update_southseas_prices.py

import json
import requests
from datetime import datetime, date

# === LISTA COMPLETA DE TUS CONSUMIBLES (hardcodeada, sin depender de archivos externos) ===
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

# === CONFIGURACIÓN API ===
API_URL = "https://api.wowauctions.net/items/stats/30d/south-seas/mergedAh"

def get_latest_min_buy(item_id: int) -> int | None:
    url = f"{API_URL}/{item_id}"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            return None
        data = r.json()

        today = date.today().isoformat()
        # Ordenar timestamps de más reciente a más antiguo
        timestamps = sorted(data.keys(), reverse=True)

        # 1º prioridad: min_buy de hoy
        for ts in timestamps:
            if ts.startswith(today) and data[ts].get("min_buy"):
                return int(data[ts]["min_buy"])

        # 2º prioridad: último min_buy disponible
        for ts in timestamps:
            if data[ts].get("min_buy"):
                return int(data[ts]["min_buy"])

    except Exception as e:
        print(f"    Error con {item_id}: {e}")
    return None

def main():
    prices = {}
    print("Actualizando precios South Seas - merged AH...\n")
    
    for item_id in sorted(ITEM_IDS):
        print(f"{item_id}", end=" → ")
        price = get_latest_min_buy(item_id)
        if price is not None:
            prices[str(item_id)] = price
            print(f"{price:,} cobre")
        else:
            prices[str(item_id)] = 0  # o puedes poner None si prefieres
            print("SIN DATOS")

    result = {
        "data": prices,
        "last_update": datetime.now().timestamp()
    }

    with open("southseasprices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print("\n¡Listo! southseasprices.json creado y actualizado.")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')} (Argentina)")

if __name__ == "__main__":
    main()