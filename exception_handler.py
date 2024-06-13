import time
from functools import wraps
from selenium.common.exceptions import StaleElementReferenceException


def handle_stale_exception(retries=3, delay=0.4):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException:
                    print(f'StaleElementReferenceException <<=>> Retrying {attempt + 1} times')
                    time.sleep(delay)
                print(f"Retried {retries} times, Skipping to the next element")
            return None

        return wrapper

    return decorator


