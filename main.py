from contextlib import asynccontextmanager
from fastapi import FastAPI
from cache.redis_client import RedisClient
from dotenv import load_dotenv
import os
from strawberry.fastapi import GraphQLRouter
import strawberry
from graphql_definitions.queries import Query
from dex_clients.gecko_terminal import GeckoTerminal
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore

load_dotenv()

#TODO: This could be in another file
async def fetch_pools():
    pools = await GeckoTerminal().fetch_pools()
    for pool in pools:
        await RedisClient.set_json_value(
            f"pools:{pool["token1_symbol"]}/{pool["token2_symbol"]}",
            "$",
            pool
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisClient.initialize(os.getenv("REDIS_URL"))
    await fetch_pools()

    #TODO: This cronjob could be moved to a separate container/pod so it doesn't consume resources for the API
    # slowing it down
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_pools, 'interval', minutes=1)
    scheduler.start()

    yield

    scheduler.shutdown()
    await RedisClient.close_connection()


schema = strawberry.Schema(query=Query)
graphql_app: GraphQLRouter = GraphQLRouter(schema)

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")