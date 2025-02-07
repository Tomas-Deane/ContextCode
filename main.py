"""
Main entry point for the application. A Flask web server that reads data from the
metrics datamodel and returns it as a JSON object while also timing the operation.
This brings together the BlockTimer class and metrics DataReader class from prior
examples (note, DataSnapshot is the new name for the datamodel object).

The metrics route has three different conversion methods to show how to convert the
data to JSON. JSON conversion needs a deep understanding of the data structure being
passed to any given parsing/generation method. The metrics route has a parameter to
demonstrate the three different methods, called conversion_method.

Browse to localhost:<port>/metrics?conversion_method=1 to see the raw JSON string.
Browse to localhost:<port>/metrics?conversion_method=2 to see the JSON string converted to a dict()
Browse to localhost:<port>/metrics?conversion_method=3 to see the object converted directly to a dict()

Note that method 3 is the one that provides the correct results and is also the most 
efficient as it avoids the overhead of converting to a JSON string and then back to a
JSON object.

To use this, run it and browse to the localhost:<port>/metrics route with a conversion method of your choice.
"""
import sys
import json
import logging
from lib_config.config import Config
from lib_utils.blocktimer import BlockTimer
from datetime import datetime, UTC
from lib_metrics_datamodel.metrics_datamodel import *
from flask import Flask, request


class Application:
    def __init__(self):
        """Initialize the application with required configuration and logging."""
        self.config = Config(__file__)
        self.logger = logging.getLogger(__name__)
        self.webserver = Flask(__name__)
        self.setup_routes()
        self.logger.debug("Application initialized")

    def setup_routes(self):
        """Setup the routes for the application."""
        self.webserver.route("/hello")(self.hello_world)
        self.webserver.route("/metrics")(self.metrics)

    def hello_world(self):
        """Hello world route."""
        self.logger.info("Hello world route called")
        return {'message': 'Hello, World from the Data Reading Web Server! Use /metrics to get data.'}

    def metrics(self):
        """Metrics route.
        Query Parameter:
            conversion_method (int, optional): The method of conversion to use. Defaults to 0, which is recommended.
            1: Response contains a RAW JSON string
            2: Object => JSON String => dict() for flask to convert back to JSON
            3: Object direct to dict() for flask to do the only JSON string conversion
        """
        conversion_method = request.args.get('conversion_method', default=0, type=int)
        
        self.logger.info("Metrics route called with conversion method %s", conversion_method)
        # Main application logic executed, with top-level error handling
        try:
            with BlockTimer("read_metrics", self.logger):
                data_snapshot = Device.read_PC_metrics()
                # Three different ways to convert to JSON for REST response
                if conversion_method == 1:
                    # RAW JSON string
                    rest_ready_json = data_snapshot.to_json()                
                elif conversion_method == 2:
                    # Object => JSON String => dict() for flask to convert back to JSON
                    json_string = data_snapshot.to_json()
                    rest_ready_json = json.loads(json_string)                
                else:
                    # Object direct to dict() for flask to do the only JSON string conversion
                    rest_ready_json = data_snapshot.to_dict()
                
                timestamp = datetime.now(UTC).isoformat()
            
            return {
                'status': 'success',
                'data': rest_ready_json,
                'timestamp': timestamp
            }, 200
            
        except Exception as e:
            self.logger.exception("Error in metrics route: %s", str(e))
            return {
                'status': 'error',
                'message': str(e)
            }, 500

    def run(self) -> int:
        """
        Main application logic.
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            self.logger.info("Starting Flask web server on port %s", self.config.web.port)
            self.webserver.run(debug=self.config.web.debug, port=self.config.web.port)
            self.logger.info("Application completed successfully")
            return 0
            
        except Exception as e:
            self.logger.exception("Application failed with error: %s", str(e))
            return 1
        

def main() -> int:
    """Entry point for the application."""
    app = Application()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())