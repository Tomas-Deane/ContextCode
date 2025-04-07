import threading
import logging
import os
import json
from metrics_queue import create_metrics_queue
from pc_collector import run_pc_collector, poll_commands
from third_party_collector import run_third_party_collector
from bitcoin_collector import run_bitcoin_collector
from eth_dominance_collector import run_eth_dominance_collector
from uploader import upload_metrics

# Define a JSON formatter for machine-readable logging.
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

# Configure file handler.
log_file = os.path.join(os.path.dirname(__file__), "collector.log")
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(JsonFormatter())

# Configure stream handler (prints to stdout).
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(JsonFormatter())

# Configure logging with both handlers.
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)
logger.info("Logging is configured. Logs are written to both the terminal and %s", log_file)

def main():
    q = create_metrics_queue()

    # Start thread to poll commands for the local device.
    command_thread = threading.Thread(target=poll_commands, daemon=True)
    command_thread.start()

    # Start thread for local PC metrics.
    pc_thread = threading.Thread(target=run_pc_collector, args=(q, 5), daemon=True)
    pc_thread.start()

    # Start thread for Bitcoin metrics.
    bitcoin_thread = threading.Thread(target=run_bitcoin_collector, args=(q, 10), daemon=True)
    bitcoin_thread.start()
    
    # Start thread for Ethereum Dominance metrics.
    eth_dominance_thread = threading.Thread(target=run_eth_dominance_collector, args=(q, 10), daemon=True)
    eth_dominance_thread.start()

    #  OpenSky metrics (can get rate limited for day pretty quick).
    third_party_thread = threading.Thread(target=run_third_party_collector, args=(q, 10), daemon=True)
    third_party_thread.start()

    # Start the uploader in the main thread.
    upload_metrics(q)

if __name__ == "__main__":
    main()
