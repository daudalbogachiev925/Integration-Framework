import time
import random
from functools import wraps

class RetryError(Exception):
    pass

def retry(max_attempts=3, base_delay=1.0, backoff=2.0, jitter=0.1,
          exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exc = None
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    attempt += 1
                    if attempt >= max_attempts:
                        break
                    delay = base_delay * (backoff ** (attempt - 1))
                    delay += random.uniform(0, jitter * delay)
                    time.sleep(delay)
            raise RetryError(f"All {max_attempts} attempts failed: {last_exc}")
        return wrapper
    return decorator

def retry_call(func, *args, max_attempts=3, **kwargs):
    return retry(max_attempts=max_attempts)(func)(*args, **kwargs)
