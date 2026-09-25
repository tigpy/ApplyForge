from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class JobConnector(ABC):
    name: str

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_job(self, external_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def normalize(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        pass

class ApplicationConnector(JobConnector):
    @abstractmethod
    def prepare_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def submit_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
