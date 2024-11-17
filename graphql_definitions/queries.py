from typing import List

import strawberry
from cache.redis_client import RedisClient
from dijkstar import Graph, find_path  # type: ignore
import asyncio

@strawberry.type
class PoolType:
    address: str
    name: str
    token1_address: str
    token2_address: str
    token1_symbol: str
    token2_symbol: str
    reserve_in_usd: str

@strawberry.type
class Query:
    @strawberry.field
    async def get_pool(self, pool_name: str) -> PoolType:
        re = await RedisClient.get_json_value(f"pools:{pool_name}")
        return PoolType(**re)

    @strawberry.field
    async def get_pools(self) -> List[PoolType]:
        keys = await RedisClient.get_keys("pools:*")

        #TODO: Use redis MGET command to retrieve multiple keys in 1 go
        data = await asyncio.gather(*(RedisClient.get_json_value(key) for key in keys))

        return [
            PoolType(**d)
            for d in data
        ]

    @strawberry.field
    async def get_pairs(self) -> List[str]:
        keys = await RedisClient.get_keys("pools:*")

        #TODO: Use redis MGET command to retrieve multiple keys in 1 go
        data = await asyncio.gather(*(RedisClient.get_json_value(key) for key in keys))

        return [
            f"{d["token1_symbol"]}/{d["token2_symbol"]}"
            for d in data
        ]

    @strawberry.field
    async def supported_tokens(self) -> List[str]:
        keys = await RedisClient.get_keys("pools:*")

        #TODO: Use redis MGET command to retrieve multiple keys in 1 go
        data = await asyncio.gather(*(RedisClient.get_json_value(key) for key in keys))

        return list(set(
            symbol
            for d in data
            for symbol in [d["token1_symbol"], d["token2_symbol"]]
        ))

    @strawberry.field
    async def find_best_path(self, a: str, b: str) -> List[str]:
        #TODO: The graph finding logic could be split into another service
        keys = await RedisClient.get_keys("pools:*")
        graph = Graph()
        for key in keys:
            #TODO: Use redis MGET command to retrieve multiple keys in 1 go
            # useful if there are many keys to reduce network requests
            d = await RedisClient.get_json_value(key)
            #TODO: Add fee into cost
            graph.add_edge(d["token1_symbol"], d["token2_symbol"], 1/float(d["reserve_in_usd"]))

        #TODO: Build the graph once tokens are fetched instead of building it on every findBestPath request
        result = find_path(graph, a, b)
        #TODO: Cache paths for same requests e.g if A->B has been computed once, cache it for a small period or other
        # conditions like pool liquidity changes drastically
        # another way to optimize this is to calculate the path on another service built in rust,
        # or build a python module in C, that would only be beneficial if we have huge graph
        return result.nodes