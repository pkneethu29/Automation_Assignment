# resources/keywords.py

import time
import logging
import yaml
import os
from requests import Session, RequestException
from faker import Faker
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)

# read yaml config if exists
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        CONFIG = yaml.safe_load(f)
else:
    CONFIG = {}

DEFAULT_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', CONFIG.get('retry', {}).get('attempts', 3)))
DEFAULT_BACKOFF = float(os.getenv('RETRY_BACKOFF', CONFIG.get('retry', {}).get('backoff_seconds', 1.0)))

fake = Faker()

def retry(attempts=DEFAULT_ATTEMPTS, backoff=DEFAULT_BACKOFF):
    """
    Decorator to retry functions with logging of each attempt.
    Usage: @retry(attempts=3, backoff=1.5)
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts+1):
                start = time.time()
                try:
                    logger.info(f"Attempt {attempt}/{attempts} calling {fn.__name__}")
                    result = fn(*args, **kwargs)
                    duration = time.time() - start
                    logger.info(f"Success on attempt {attempt}/{attempts} ({duration:.2f}s)")
                    return result
                except Exception as e:
                    duration = time.time() - start
                    logger.warning(f"Attempt {attempt}/{attempts} failed in {duration:.2f}s: {e}")
                    last_exc = e
                    if attempt < attempts:
                        sleep_time = backoff * attempt
                        logger.info(f"Sleeping {sleep_time}s before next attempt")
                        time.sleep(sleep_time)
            logger.error(f"All {attempts} attempts failed for {fn.__name__}")
            raise last_exc
        return wrapper
    return decorator

class HttpbinLibrary:
    """
    A Robot Framework library providing HTTP keywords, with retry and logging.
    """

    def __init__(self, base_url=None, timeout=None):
        self.base_url = base_url or os.getenv('HTTPBIN_BASE_URL') or CONFIG.get('httpbin', {}).get('base_url')
        self.timeout = timeout or CONFIG.get('httpbin', {}).get('timeout', 10)
        self.session = Session()

    @retry()
    def get(self, path="/get", params=None, headers=None):
        url = self.base_url.rstrip('/') + path
        logger.info(f"GET {url} params={params} headers={headers}")
        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    @retry()
    def post_json(self, path="/post", json_payload=None, headers=None):
        url = self.base_url.rstrip('/') + path
        logger.info(f"POST {url} json={json_payload} headers={headers}")
        resp = self.session.post(url, json=json_payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    # dynamic data generator
    def generate_user(self):
        return {
            "name": fake.name(),
            "email": fake.email(),
            "address": fake.address(),
            "bio": fake.sentence(nb_words=10)
        }