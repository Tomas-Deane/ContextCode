import logging
import requests
import math
import time
from registration import register_device
from collector_agent.config import OPENSKY_DEVICE_FRIENDLY_NAME, OPENSKY_DEVICE_ROLE, OPENSKY_GUID_FILE

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def collect_opensky_metrics():
    # Define a bounding box for Ireland.
    lamin = 51.4
    lamax = 55.5
    lomin = -10.5
    lomax = -5.3
    opensky_url = (
        f"https://opensky-network.org/api/states/all"
        f"?lamin={lamin}&lamax={lamax}&lomin={lomin}&lomax={lomax}"
    )
    plane_count = 0
    closest_distance = None
    closest_callsign = None
    
    # Limerick City coordinates.
    LIMERICK_LAT = 52.668
    LIMERICK_LON = -8.6305

    try:
        response = requests.get(opensky_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        states = data.get('states', [])
        plane_count = len(states)
        for state in states:
            # OpenSky API returns a list where:
            # state[1] is the callsign,
            # state[5] is longitude, and state[6] is latitude.
            plane_lon = state[5]
            plane_lat = state[6]
            if plane_lon is None or plane_lat is None:
                continue
            dist = haversine_distance(LIMERICK_LAT, LIMERICK_LON, plane_lat, plane_lon)
            if closest_distance is None or dist < closest_distance:
                closest_distance = dist
                closest_callsign = state[1].strip() if state[1] else "Unknown"
    except Exception as e:
        logging.error("Error fetching from OpenSky:", e)
        plane_count = 0
        closest_distance = 0
        closest_callsign = "None"

    if closest_distance is None:
        closest_distance = 0

    device_guid = register_device(OPENSKY_DEVICE_ROLE, OPENSKY_DEVICE_FRIENDLY_NAME, OPENSKY_GUID_FILE)
    if not device_guid:
        device_guid = "unregistered"

    # Build the payload using fields for each metric.
    payload = {
        "device_guid": device_guid,
        "metrics": [
            {"name": "Plane Count Ireland", "fields": {"plane_count": plane_count}},
            {"name": "Closest Plane Limerick", "fields": {"closest_distance": closest_distance, "callsign": closest_callsign}}
        ]
    }
    return payload

def run_third_party_collector(metrics_queue, interval=10):
    while True:
        payload = collect_opensky_metrics()
        metrics_queue.put(payload)
        time.sleep(interval)
