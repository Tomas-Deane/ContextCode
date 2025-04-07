import requests
from .config import DEFAULT_BASE_URL, DEFAULT_API_KEY
from .exceptions import AggregatorAPIError

class AggregatorAPI:
    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=DEFAULT_API_KEY, timeout=10):
        """
        Initialize the Aggregator API client.

        Args:
            base_url (str): Base URL of the aggregator server.
            api_key (str): API key used for authorized endpoints.
            timeout (int): Timeout in seconds for HTTP requests.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        # Headers for endpoints that require authentication (e.g. posting metrics)
        self.auth_headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def _handle_response(self, response):
        """
        Process the HTTP response.
        
        Raises:
            AggregatorAPIError: If the response has a non-OK status or fails JSON parsing.
        """
        if not response.ok:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text
            raise AggregatorAPIError(f"Error {response.status_code}: {error_data}")
        try:
            return response.json()
        except Exception as e:
            raise AggregatorAPIError(f"Failed to parse JSON: {e}")

    def get_metrics(self):
        """Retrieve the latest metrics snapshot."""
        url = f"{self.base_url}/api/metrics"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)

    def get_history(self, metric_id, page=1, page_size=20):
        """
        Retrieve historical readings for a given metric.
        
        Args:
            metric_id (int): The ID of the metric.
            page (int): Page number for pagination.
            page_size (int): Number of items per page.
        """
        url = f"{self.base_url}/api/history/{metric_id}"
        params = {"page": page, "page_size": page_size}
        response = requests.get(url, params=params, timeout=self.timeout)
        return self._handle_response(response)

    def send_command(self, device, command):
        """
        Send a command to a device.

        Args:
            device (str): Friendly name of the device.
            command (str): Command to be executed.
        """
        url = f"{self.base_url}/api/command"
        payload = {"device": device, "command": command}
        response = requests.post(url, json=payload, 
                                 headers={"Content-Type": "application/json"}, 
                                 timeout=self.timeout)
        return self._handle_response(response)

    def get_commands(self, friendly_name):
        """
        Retrieve pending commands for a given device.

        Args:
            friendly_name (str): Friendly name of the device.
        """
        url = f"{self.base_url}/api/command/{friendly_name}"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)

    def register_device(self, role, friendly_name):
        """
        Register a new device with the aggregator.

        Args:
            role (str): Role of the device (e.g. "PC-Metrics", "OpenSky-Collector").
            friendly_name (str): A human-friendly device name.
        """
        url = f"{self.base_url}/api/register"
        payload = {"role": role, "friendly_name": friendly_name}
        response = requests.post(url, json=payload, 
                                 headers={"Content-Type": "application/json"}, 
                                 timeout=self.timeout)
        return self._handle_response(response)

    def post_metrics(self, device_guid, metrics):
        """
        Post metrics for a device.

        Args:
            device_guid (str): The GUID of the registered device.
            metrics (list): A list of metrics dictionaries. Each metric should include a "name"
                            and a "fields" dictionary.
        """
        url = f"{self.base_url}/api/metrics"
        payload = {"device_guid": device_guid, "metrics": metrics}
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.timeout)
        return self._handle_response(response)

    def get_schema(self):
        """Retrieve the current schema of devices and metrics."""
        url = f"{self.base_url}/api/schema"
        response = requests.get(url, timeout=self.timeout)
        return self._handle_response(response)
