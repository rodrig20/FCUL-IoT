from functools import wraps
import requests
import logging
import time


class Cache:
    def __init__(self, max_age_seconds: float) -> None:
        self.__max_age_seconds = max_age_seconds
        self.__cached_timestamp = float("-inf")
        self.__cached_value = None

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.__is_expired():
                self.__cached_value = func(*args, **kwargs)
                self.__cached_timestamp = time.time()
            return self.__cached_value

        return wrapper

    def __is_expired(self) -> bool:
        return time.time() - self.__cached_timestamp > self.__max_age_seconds


class ProcessorRequester:
    __base_url = "http://processor:5000"
    __logger = logging.getLogger("processor_requester")
    __logger.setLevel(logging.INFO)

    @classmethod
    @Cache(max_age_seconds=30 * 60)
    def get_headers(cls):
        try:
            response = requests.get(f"{cls.__base_url}/get_headers")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching headers: {e}")
            return None

    @classmethod
    @Cache(max_age_seconds=5)
    def get_all_info(cls):
        try:
            response = requests.get(f"{cls.__base_url}/get_all_info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching all info: {e}")
            return None
