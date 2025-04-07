import logging
import requests
import time
from registration import register_device
from collector_agent.config import BITCOIN_DEVICE_FRIENDLY_NAME, BITCOIN_DEVICE_ROLE, BITCOIN_GUID_FILE

def collect_bitcoin_metrics():
    """
    Collects Bitcoin metrics from CoinGecko API.
    Retrieves Bitcoin price, market cap, and 24h price change percentage.
    Aborts metric uploading if any of these values are None.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            bitcoin_data = data[0]
            price = bitcoin_data.get("current_price")
            market_cap = bitcoin_data.get("market_cap")
            price_change_24h = bitcoin_data.get("price_change_percentage_24h")
        else:
            raise Exception("Invalid data structure returned from CoinGecko")
        
        # Abort if any required metric value is None
        if price is None or market_cap is None or price_change_24h is None:
            raise Exception("One or more Bitcoin metrics are None")
    except Exception as e:
        logging.error("Error fetching Bitcoin metrics from CoinGecko: %s. Payload will not be uploaded.", e)
        return None

    # Register (or retrieve) the device GUID
    device_guid = register_device(BITCOIN_DEVICE_ROLE, BITCOIN_DEVICE_FRIENDLY_NAME, BITCOIN_GUID_FILE)
    if not device_guid:
        device_guid = "unregistered"

    payload = {
        "device_guid": device_guid,
        "metrics": [
            {"name": "Bitcoin Metrics", "fields": {
                "price": price,
                "market_cap": market_cap,
                "price_change_24h": price_change_24h
            }}
        ]
    }
    logging.info("Bitcoin collector payload: %s", payload)
    return payload

def run_bitcoin_collector(metrics_queue, interval=10):
    """
    Runs the Bitcoin collector agent which periodically fetches metrics
    from CoinGecko and puts them on the metrics_queue only if they are valid.
    """
    while True:
        payload = collect_bitcoin_metrics()
        if payload is not None:
            metrics_queue.put(payload)
        time.sleep(interval)
