from abc import ABC, abstractmethod
import httpx
import urllib.parse
from typing import Any


class Client(ABC):
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    async def fetch_tokens(self):
        pass

    @abstractmethod
    async def fetch_pools(self):
        pass

    async def get(self, path: str) -> Any:
        url = urllib.parse.urljoin(self.base_url(), path)
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
