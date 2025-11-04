from abc import ABC, abstractmethod
from typing import Dict, Optional

import requests


class RemoteLoader(ABC):
    """Base class for loading quiz files from remote sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MCQPy-Web/1.0"})

    @abstractmethod
    def load_quiz(self, url: str) -> Optional[Dict]:
        """
        Load a complete quiz from a URL

        Args:
            url: URL to load quiz from

        Returns:
            Dictionary with config and questions, or None if failed
        """
        pass

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this loader can handle the given URL

        Args:
            url: URL to check

        Returns:
            True if this loader can handle the URL, False otherwise
        """
        pass
