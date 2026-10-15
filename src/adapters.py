from abc import ABC, abstractmethod
from src.http_client import HTTPClient, HTTPConfig

class IntegrationAdapter(ABC):
    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def receive(self):
        pass

class RESTAdapter(IntegrationAdapter):
    def __init__(self, base_url, headers=None):
        self.client = HTTPClient(HTTPConfig(base_url, headers=headers or {}))

    def send(self, data, path="/api/data"):
        return self.client.post(path, json=data).json()

    def receive(self, path="/api/data"):
        return self.client.get(path).json()

class CRMAdapter(RESTAdapter):
    def __init__(self, base_url, token):
        super().__init__(base_url, headers={"Authorization": f"Bearer {token}"})

    def create_lead(self, lead):
        return self.send(lead, "/leads")

    def get_contacts(self):
        return self.receive("/contacts")

class WMSAdapter(RESTAdapter):
    def __init__(self, base_url, api_key):
        super().__init__(base_url, headers={"X-API-Key": api_key})

    def push_order(self, order):
        return self.send(order, "/orders")

    def get_stock(self):
        return self.receive("/stock")
