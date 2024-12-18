## Introduction
Service that exposes a GraphQL API where you can query information about top 20 pools available in ETH chain and find the optimal path to trade 2 assets. All the data is stored on Redis, the app fetches all the data on start and refreshes the data every minute. The service is fully async.

My mindset for this exercise has been simplicy over complexity, hopefully the code is easy to follow and to understand and extending the code will be quiet easy.

## How to Setup
Using docker and compose you can simply start the containers by using the following command:

`docker compose up -d`

## How to query the service
Open in a browser the following url:

`http://localhost:8000/graphql`

It opens an interactive GraphQL console.

Examples on how to query the service:

#### Get pool by pair name (name field only)
```
{
  getPool(poolName:"OOGE/WETH") {
    name
  }
}
```

#### Get all pools (name field only)
```
{
  getPools {
    name
  }
}
```

#### Get available trading pairs
```
{
  getPairs
}
```

#### Get supported tokens
```
{
  supportedTokens
}
```

#### Find best path between 2 assets
```
{
  findBestPath(a:"Dogecasts", b:"USDT")
}
```

## Details
I documented in the code already my thougths, things that can be improved, where we could have possible bottlenecks etc.

## Testing / Linting
- Added a basic test covering the basic feature of the service, finding the optimal path between 2 assets.
- Mypy is used for type linting and Ruff for general code linting

## Notes
For the sake of this exercise, I haven't maintained a decent git history