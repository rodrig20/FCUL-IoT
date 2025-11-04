from functools import wraps
import requests
import logging
import time


class Cache:
    """A simple caching decorator that caches function results for a specified time"""

    def __init__(self, max_age_seconds: float) -> None:
        """Initialize the cache with a maximum age for cached values

        Args:
            max_age_seconds (float): Maximum age in seconds before cache expires
        """
        self.__max_age_seconds = max_age_seconds
        self.__cached_timestamp = float("-inf")
        self.__cached_value = None

    def __call__(self, func):
        """Make this class instance callable as a decorator

        Args:
            func: The function to decorate

        Returns:
            function: The wrapped function with caching capability
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function that implements the caching logic

            Args:
                *args: Variable length argument list
                **kwargs: Arbitrary keyword arguments

            Returns:
                The cached result if not expired, otherwise executes the function
            """
            if self.__is_expired():
                # Update cached value and timestamp
                self.__cached_value = func(*args, **kwargs)
                self.__cached_timestamp = time.time()
            return self.__cached_value

        return wrapper

    def __is_expired(self) -> bool:
        """Check if the cached value has expired

        Returns:
            bool: True if the cache has expired, False otherwise
        """
        return time.time() - self.__cached_timestamp > self.__max_age_seconds


class ProcessorRequester:
    """Class responsible for making requests to the Processor service"""

    __base_url = "http://processor:5000"
    __logger = logging.getLogger("processor_requester")
    __logger.setLevel(logging.INFO)

    @classmethod
    @Cache(max_age_seconds=30 * 60)
    def get_headers(cls) -> list:
        """Get headers from the Processor service with caching (30 min)

        Returns:
            list: List of headers
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_headers")
            response.raise_for_status()
            data = response.json()
            # Type cheking
            if isinstance(data, list):
                return data
            else:
                cls.__logger.error(
                    "Unexpected response format: expected list"
                )
                return []
        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching headers: {e}")
            return []

    @classmethod
    @Cache(max_age_seconds=5)
    def get_all_info(cls) -> list[tuple]:
        """Get all information from the Processor service with caching (5 sec)

        Returns:
            list[list]: All info from processor if successful, empty list if an error occurs
        """
        try:
            response = requests.get(f"{cls.__base_url}/get_all_info")
            response.raise_for_status()
            data = response.json()

            # Ensure response is a list
            if isinstance(data, list):
                return data
            else:
                cls.__logger.error(
                    "Unexpected response format: expected list"
                )
                return []

        except requests.exceptions.RequestException as e:
            cls.__logger.error(f"Error fetching all info: {e}")
            return []
