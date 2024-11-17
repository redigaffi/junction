from dex_clients.client import Client
from typing import TypedDict, List, Optional
import httpx
from itertools import batched
import asyncio

class PoolType(TypedDict):
    address: str
    name: str
    token1_address: str
    token2_address: str
    token1_symbol: Optional[str]
    token2_symbol: Optional[str]
    reserve_in_usd: str

class GeckoTerminal(Client):
    BASE_URL = "https://api.geckoterminal.com/api/v2/"

    def base_url(self) -> str:
        return self.BASE_URL

    async def fetch_tokens(self):
        return await super().fetch_tokens()

    async def fetch_pools(self) -> List[PoolType]:
        # TODO: HTTP Error checking, take into account rate-limiting, retrying, etc.
        pool_data = await self.get("networks/eth/pools")
        return_data: List[PoolType] = []
        token_addresses = set()
        for pool in pool_data["data"]:
            token1_address = pool["relationships"]["base_token"]["data"]["id"].replace("eth_", "")
            token2_address = pool["relationships"]["quote_token"]["data"]["id"].replace("eth_", "")
            token_addresses.update([token1_address, token2_address])

            return_data.append({
                "address": pool["attributes"]["address"],
                "name": pool["attributes"]["name"],
                "token1_address": token1_address,
                "token2_address": token2_address,
                "reserve_in_usd": pool["attributes"]["reserve_in_usd"],
                "token1_symbol": None,
                "token2_symbol": None,
            })

        token_info = {}
        async with httpx.AsyncClient():
            # TODO: HTTP Error checking, take into account rate-limiting, retrying, etc.
            tok_info_re = await asyncio.gather(
                *(self.get(f"networks/eth/tokens/multi/{",".join(list(addresses))}")
                  for addresses in batched(token_addresses, 30))
            )

            token_info = {
                tok_info["attributes"]["address"]: tok_info["attributes"]
                for tok_info_chunk in tok_info_re
                for tok_info in tok_info_chunk["data"]
                if tok_info["attributes"]["address"] not in token_info
            }

        for ret in return_data:
            ret["token1_symbol"] = token_info[ret["token1_address"]]["symbol"]
            ret["token2_symbol"] = token_info[ret["token2_address"]]["symbol"]

        return return_data

