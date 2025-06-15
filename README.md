# EcoRoutes

This project uses Docker Compose to spin up a routing stack consisting of OSRM,
Redis, and a small Node backend. The backend periodically fetches AQI tiles and
exposes an API for retrieving cached tiles or routing information.

## Backend API

The backend image now starts `node index.js`, which runs an Express server.
Routes:

- `GET /aqi/:z/:x/:y.png` – returns a cached AQI tile from Redis.
- `GET /route?start=lon,lat&end=lon,lat` – proxies a route request to the OSRM service.

The separate `aqi-fetcher` service continues running `scripts/fetch-aqi.js` to
update the cache.
