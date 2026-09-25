from typing import Dict
from packages.connectors.base import JobConnector
from packages.connectors.manual import ManualImportConnector
from packages.connectors.mock import MockApplicationConnector
from packages.connectors.public_feed import PublicFeedConnector

class ConnectorRegistry:
    def __init__(self):
        self._connectors: Dict[str, JobConnector] = {}
        self.register(ManualImportConnector())
        self.register(MockApplicationConnector())
        self.register(PublicFeedConnector())

    def register(self, connector: JobConnector) -> None:
        self._connectors[connector.name] = connector

    def get(self, name: str) -> JobConnector:
        if name not in self._connectors:
            raise KeyError(f"Connector '{name}' is not registered. Available: {list(self._connectors.keys())}")
        return self._connectors[name]

    def list_connectors(self) -> Dict[str, bool]:
        return {name: conn.health_check() for name, conn in self._connectors.items()}

connector_registry = ConnectorRegistry()
