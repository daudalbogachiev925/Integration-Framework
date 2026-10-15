import requests
from dataclasses import dataclass, field
from src.retry import retry
from src.circuit_breaker import CircuitBreaker

@dataclass
class HTTPConfig:
    base_url: str
    timeout: int = 30
    headers: dict = field(default_factory=dict)
    max_retries: int = 3

class HTTPClient:
    def __init__(self, config: HTTPConfig):
        self.config = config
        self.breaker = CircuitBreaker(name=config.base_url)
        self.session = requests.Session()
        self.session.headers.update(config.headers)

    def _do(self, method, path, **kwargs):
        url = f"{self.config.base_url}{path}"
        r = self.session.request(method, url,
                                 timeout=self.config.timeout, **kwargs)
        r.raise_for_status()
        return r

    def get(self, path, params=None):
        return self._call("GET", path, params=params)

    def post(self, path, json=None):
        return self._call("POST", path, json=json)

    def put(self, path, json=None):
        return self._call("PUT", path, json=json)

    def delete(self, path):
        return self._call("DELETE", path)

    def _call(self, method, path, **kwargs):
        @retry(max_attempts=self.config.max_retries)
        def execute():
            return self._do(method, path, **kwargs)
        return self.breaker.call(execute)
