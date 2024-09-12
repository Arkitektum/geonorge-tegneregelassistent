from .config_loader import ConfigLoader
from json import loads
from .logging_setup import logger as log
from .api_call_manager import ApiCallManager as acm


class GeonorgeAPI:

    def __init__(self):
        config_loader = ConfigLoader()
        self.config = config_loader.load_qgis_config()
        print(f"Geonorge API initialized with config: {self.config}")

    def get_styles_for_theme(self, tema):
        # Load the configuration

        # Define the endpoint URL and request parameters
        endpoint_url = self.config['endpoint_url']['cartography']
        request_params = {
            "text": str(tema),
            "limitofficial": True
        }

        # Make the API call
        api_call_new = acm()
        api_call_new.get(endpoint_url, request_params)
        response_data = api_call_new.get_response_data()
        if response_data:
            json_data = loads(str(response_data, 'utf-8'))
            log.info(
                "OK Fetching styles for theme '{}' from Geonorge".format(tema))
            return json_data

        return None

    def get_schemas(self):
        """
        Fetches schema data from the Geonorge API.
        :return: DataFrame containing schema data.
        :rtype: pd.DataFrame
        """
        # Get the endpoint URL from the config
        schema_url = self.config['endpoint_url']['schema']

        # Make the API call
        api_call_new = acm()
        api_call_new.get(schema_url)
        response_data = api_call_new.get_response_data()

        if response_data:
            log.info("OK Fetching schemas from Geonorge")
            json_data = loads(str(response_data, 'utf-8'))
            return json_data

        log.debug("Cannot fetch schemas from Geonorge")
        return None
