import logging
import os
import psutil
import time
from registration import register_device
from aggregator_sdk.client import AggregatorAPI
from collector_agent.config import LOCAL_DEVICE_FRIENDLY_NAME, LOCAL_DEVICE_ROLE, LOCAL_GUID_FILE

def collect_local_metrics():
    # Register (or retrieve) the GUID from a local file using environment-based settings.
    device_guid = register_device(LOCAL_DEVICE_ROLE, LOCAL_DEVICE_FRIENDLY_NAME, LOCAL_GUID_FILE)
    if not device_guid:
        device_guid = "unregistered"
    mem_usage = psutil.virtual_memory().percent
    process_count = len(psutil.pids())
    
    # Build the payload with a 'fields' dictionary for each metric.
    metrics_payload = {
        "device_guid": device_guid,
        "metrics": [
            {"name": "Memory Usage", "fields": {"percentage": mem_usage}},
            {"name": "Process Count", "fields": {"count": process_count}}
        ]
    }
    return metrics_payload

def poll_commands():
    """
    Polls the aggregator for pending commands for this device using the SDK.
    """
    aggregator = AggregatorAPI()
    while True:
        try:
            # Get pending commands using the friendly name from config
            commands = aggregator.get_commands(LOCAL_DEVICE_FRIENDLY_NAME)
            for cmd in commands:
                # Check for the specific command text (case-insensitive)
                if cmd['command'].lower() == "open taskmanager":
                    logging.info("Executing Task Manager command")
                    # On Windows, this will open Task Manager.
                    os.system("start taskmgr")
        except Exception as e:
            logging.error("Error polling commands: %s", e)
        time.sleep(5)  # Poll every 5 seconds

def run_pc_collector(metrics_queue, interval=5):
    while True:
        payload = collect_local_metrics()
        metrics_queue.put(payload)
        time.sleep(interval)
