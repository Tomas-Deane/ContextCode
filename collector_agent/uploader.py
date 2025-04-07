import logging
import time
from aggregator_sdk.client import AggregatorAPI

def upload_metrics(metrics_queue):
    """
    Continuously takes items from the metrics_queue and posts them to the aggregator using the SDK.
    Logs both the payload and the response (or error) so that the uploaded payload is visible.
    """
    aggregator = AggregatorAPI()
    while True:
        payload = metrics_queue.get()
        try:
            device_guid = payload.get("device_guid")
            metrics = payload.get("metrics")
            response = aggregator.post_metrics(device_guid, metrics)
            logging.info("Successfully uploaded metrics. Payload: %s, Response: %s", payload, response)
        except Exception as e:
            logging.error("Error uploading metrics. Payload: %s, Error: %s", payload, e)
        finally:
            metrics_queue.task_done()
        # Throttle the upload loop
        time.sleep(1)
