import pytest
from unittest.mock import patch
from graphql_definitions.queries import Query
import asyncio


@pytest.mark.asyncio
@patch('graphql_definitions.queries.RedisClient')
async def test_optimal_path(redis_client_patch):
    """
    """
    re = asyncio.Future()
    re.set_result(['key1', 'key2', 'key3'])
    redis_client_patch.get_keys.return_value = re

    def re(key):
        match key:
            case "key1":
                re = asyncio.Future()
                re.set_result({
                    'token1_symbol': 'a',
                    'token2_symbol': 'd',
                    'reserve_in_usd': 100
                })

                return re

            case "key2":
                re = asyncio.Future()
                re.set_result({
                    'token1_symbol': 'a',
                    'token2_symbol': 'c',
                    'reserve_in_usd': 1500
                },)

                return re

            case "key3":
                re = asyncio.Future()
                re.set_result({
                    'token1_symbol': 'c',
                    'token2_symbol': 'd',
                    'reserve_in_usd': 1000
                })

                return re

    redis_client_patch.get_json_value.side_effect = re
    path = await Query().find_best_path("a", "d")
    assert ["a", "c", "d"] == path