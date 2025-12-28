import requests
import json
import os
from src.utils.logger import get_logger
from src.config.config_reader import ConfigReader
_api_utils_logger = get_logger(__name__)  # Obtener instancia del logger para este módulo


class ApiUtils:

    def __init__(self, env='qa'):  # Default environment for API calls

        self.config_reader = ConfigReader()

        self.base_url = self.config_reader.get_api_base_url(env)

        self.timeout = self.config_reader.get_api_timeout()

        self.logger = _api_utils_logger.get_logger()

        _api_utils_logger.info(f"ApiUtils inicializado para el entorno: {env} con URL base: {self.base_url}")

        self.logger = _api_utils_logger


def _send_request(self, method, endpoint, headers=None, data=None, json_data=None, params=None):
    url = f"{self.base_url}{endpoint}"

    self.logger.info(f"Sending {method} request to: {url}")

    self.logger.debug(f"Headers: {headers}")

    self.logger.debug(f"Data: {data}")

    self.logger.debug(f"JSON Data: {json_data}")

    self.logger.debug(f"Params: {params}")

    try:

        response = requests.request(

            method,

            url,

            headers=headers,

            data=data,

            json=json_data,

            params=params,

            timeout=self.timeout

        )

        self.logger.info(f"Received response from {url} with status code: {response.status_code}")

        self.logger.debug(f"Response body: {response.text}")

        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        return response

    except requests.exceptions.HTTPError as e:

        self.logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")

        raise

    except requests.exceptions.ConnectionError as e:

        self.logger.error(f"Connection Error: {e}")

        raise

    except requests.exceptions.Timeout as e:

        self.logger.error(f"Timeout Error: {e}")

        raise

    except requests.exceptions.RequestException as e:

        self.logger.error(f"Request Exception: {e}")

        raise


def get(self, endpoint, headers=None, params=None):
    return self._send_request("GET", endpoint, headers=headers, params=params)


def post(self, endpoint, headers=None, data=None, json_data=None):
    return self._send_request("POST", endpoint, headers=headers, data=data, json_data=json_data)


def put(self, endpoint, headers=None, data=None, json_data=None):
    return self._send_request("PUT", endpoint, headers=headers, data=data, json_data=json_data)


def delete(self, endpoint, headers=None, params=None):
    return self._send_request("DELETE", endpoint, headers=headers, params=params)
