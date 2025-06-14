require('dotenv').config();
const axios = require('axios');
const redis = require('redis');

const AQI_TOKEN = process.env.AQI_TOKEN;
const REDIS_URL = process.env.REDIS_URL || 'redis://redis:6379';

const ZOOM = 11;
const tiles = [];
for (let x = 1686; x <= 1690; x++) {
  for (let y = 780; y <= 784; y++) {
    tiles.push({ z: ZOOM, x, y });
  }
}

async function cacheAqiTiles(client) {
  for (const { z, x, y } of tiles) {
    const url = `https://tiles.waqi.info/tiles/usepa-aqi/${z}/${x}/${y}.png?token=${AQI_TOKEN}`;
    try {
      const { data } = await axios.get(url, { responseType: 'arraybuffer' });
      await client.set(`aqi:${z}:${x}:${y}`, Buffer.from(data), { EX: 60 * 20 });
      console.log(`[${new Date().toLocaleTimeString()}] Cached AQI tile z${z} x${x} y${y}`);
    } catch (e) {
      console.error(`[${new Date().toLocaleTimeString()}] Failed to fetch tile z${z} x${x} y${y}:`, e.message);
    }
  }
}

async function main() {
  const client = redis.createClient({ url: REDIS_URL });
  await client.connect();

  while (true) {
    await cacheAqiTiles(client);
    console.log(`[${new Date().toLocaleTimeString()}] Waiting 15 minutes for next update...`);
    await new Promise(res => setTimeout(res,15* 60 * 1000));
  }
}

main();
