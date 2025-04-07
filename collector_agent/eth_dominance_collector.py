import logging
import requests
import time
from registration import register_device
from collector_agent.config import ETH_DOMINANCE_DEVICE_FRIENDLY_NAME, ETH_DOMINANCE_DEVICE_ROLE, ETH_DOMINANCE_GUID_FILE

def collect_eth_dominance():
    """
    Collects Ethereum dominance percentage from CoinGecko Global API.
    Retrieves the Ethereum market cap percentage and returns it as a 'percentage' field.
    Aborts if the value is None.
    """
    url = "https://api.coingecko.com/api/v3/global"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        eth_dominance = data.get("data", {}).get("market_cap_percentage", {}).get("eth", None)
        if eth_dominance is None:
            raise Exception("Ethereum dominance value is None")
    except Exception as e:
        logging.error("Error fetching Ethereum dominance from CoinGecko: %s. Payload will not be uploaded.", e)
        return None

    # Register (or retrieve) the device GUID for this collector.
    device_guid = register_device(ETH_DOMINANCE_DEVICE_ROLE, ETH_DOMINANCE_DEVICE_FRIENDLY_NAME, ETH_DOMINANCE_GUID_FILE)
    if not device_guid:
        device_guid = "unregistered"

    payload = {
        "device_guid": device_guid,
        "metrics": [
            {"name": "Ethereum Dominance", "fields": {"percentage": eth_dominance}}
        ]
    }
    logging.info("Ethereum Dominance collector payload: %s", payload)
    return payload

def run_eth_dominance_collector(metrics_queue, interval=10):
    """
    Runs the Ethereum Dominance collector agent which periodically fetches the metric
    and puts the payload on the metrics_queue only if valid.
    """
    while True:
        payload = collect_eth_dominance()
        if payload is not None:
            metrics_queue.put(payload)
        time.sleep(interval)
