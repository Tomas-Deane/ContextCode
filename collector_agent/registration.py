import logging
import os
from aggregator_sdk.client import AggregatorAPI

def register_device(role, friendly_name, guid_file):
    """
    Registers the device with the aggregator using the SDK.
    If the guid_file exists, returns the stored GUID.
    Otherwise, sends a registration request and stores the returned GUID.
    """
    if os.path.exists(guid_file):
        with open(guid_file, 'r') as f:
            guid = f.read().strip()
            if guid:
                return guid

    aggregator = AggregatorAPI()
    data = aggregator.register_device(role, friendly_name)
    if "device_guid" in data:
        guid = data["device_guid"]
        with open(guid_file, 'w') as f:
            f.write(guid)
        return guid
    else:
        logging.error("Error registering device:", data)
        return None
