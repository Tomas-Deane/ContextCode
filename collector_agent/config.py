import os

# Local (PC) metrics device configuration
LOCAL_DEVICE_FRIENDLY_NAME = os.environ.get("COLLECTOR_FRIENDLY_NAME", "Tomas-Laptop")
LOCAL_DEVICE_ROLE = os.environ.get("COLLECTOR_ROLE", "Local-Metrics")
LOCAL_GUID_FILE = os.environ.get("LOCAL_GUID_FILE", "pc_guid.txt")

# OpenSky metrics device configuration
OPENSKY_DEVICE_FRIENDLY_NAME = os.environ.get("OPENSKY_FRIENDLY_NAME", "OpenSky-Data")
OPENSKY_DEVICE_ROLE = os.environ.get("OPENSKY_ROLE", "OpenSky-ThirdParty")
OPENSKY_GUID_FILE = os.environ.get("OPENSKY_GUID_FILE", "opensky_guid.txt")

# Bitcoin metrics device configuration
BITCOIN_DEVICE_FRIENDLY_NAME = os.environ.get("BITCOIN_FRIENDLY_NAME", "Bitcoin-Metrics")
BITCOIN_DEVICE_ROLE = os.environ.get("BITCOIN_ROLE", "Bitcoin-Collector")
BITCOIN_GUID_FILE = os.environ.get("BITCOIN_GUID_FILE", "bitcoin_guid.txt")

# Ethereum Dominance metrics device configuration
ETH_DOMINANCE_DEVICE_FRIENDLY_NAME = os.environ.get("ETH_DOMINANCE_FRIENDLY_NAME", "ETH-Dominance")
ETH_DOMINANCE_DEVICE_ROLE = os.environ.get("ETH_DOMINANCE_ROLE", "ETH-Dominance-Collector")
ETH_DOMINANCE_GUID_FILE = os.environ.get("ETH_DOMINANCE_GUID_FILE", "eth_dominance_guid.txt")