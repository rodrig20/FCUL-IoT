from functools import wraps
import requests
import logging
import time


class Cache:
    def __init__(self, max_age_seconds: float) -> None:
        self.__max_age_seconds = max_age_seconds

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(func, "__cache_value") or self.__is_expired(func):
                func.__cache_value = func(*args, **kwargs)
                func.__cache_timestamp = time.time()
            return func.__cache_value

        return wrapper

    def __is_expired(self, func) -> bool:
        return time.time() - func.__cache_timestamp > self.__max_age_seconds


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
    def get_user_info(cls, user_id: str):
        """Get all information for a specific user from the Processor service with caching (5 sec)

        Args:
            user_id (str): The ID of the user to get information for.

        Returns:
            list[list]: All info from processor if successful, empty list if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_user_info/{user_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching all info: {e}")
            return None

    @classmethod
    @Cache(max_age_seconds=5)
    def get_stations(cls):
        """Get all charging stations from the Processor service

        Returns:
            list[dict]: List of stations with their ID, latitude and longitude if successful, None if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_stations")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching stations: {e}")
            return None

    @classmethod
    @Cache(max_age_seconds=5)
    def get_stations_for_user(cls, user_id: str):
        """Get all charging stations with visit status from the Processor service with caching (30 min)

        Args:
            user_id (str): The ID of the user to get stations for.

        Returns:
            list[dict]: List of stations with their ID, latitude, longitude and visit status if successful, None if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_stations_for_user/{user_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching stations for user: {e}")
            return None

    @classmethod
    @Cache(max_age_seconds=30 * 60)
    def get_all_users(cls):
        """Get list of all users from the Processor service with caching (30 min)

        Returns:
            list[str]: List of all user IDs if successful, empty list if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_users")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching users: {e}")
            return []

    @classmethod
    @Cache(max_age_seconds=5)
    def get_all_users_info(cls):
        """Get all information for all users from the Processor service with caching (5 sec)

        Returns:
            dict: All info from processor for all users if successful, empty dict if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_all_users_info")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching all users info: {e}")
            return {}

    @classmethod
    def classify(cls, feat1, feat2):
        """
        Requests clustering from the processor service.
        """
        try:
            response = requests.post(f"{cls.__base_url}/classify", json={"feat1": feat1, "feat2": feat2})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error making classify request: {e}")
            return None

