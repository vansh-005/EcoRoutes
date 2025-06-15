require('dotenv').config();
const express = require('express');
const axios = require('axios');
const redis = require('redis');

const REDIS_URL = process.env.REDIS_URL || 'redis://redis:6379';
const OSRM_URL = process.env.OSRM_URL || 'http://osrm:5000';
const PORT = process.env.PORT || 3000;

const client = redis.createClient({ url: REDIS_URL });
client.connect().catch(err => console.error('Redis connection error:', err));

const app = express();

app.get('/aqi/:z/:x/:y.png', async (req, res) => {
  const { z, x, y } = req.params;
  try {
    const data = await client.getBuffer(`aqi:${z}:${x}:${y}`);
    if (!data) return res.status(404).send('Tile not cached');
    res.set('Content-Type', 'image/png');
    res.send(data);
  } catch (err) {
    console.error('Error fetching tile:', err.message);
    res.status(500).send('Server error');
  }
});

app.get('/route', async (req, res) => {
  const { start, end } = req.query;
  if (!start || !end) return res.status(400).send('start and end query params required');
  try {
    const url = `${OSRM_URL}/route/v1/driving/${start};${end}`;
    const response = await axios.get(url, { params: { overview: 'full', geometries: 'geojson' } });
    res.json(response.data);
  } catch (err) {
    console.error('Error fetching route:', err.message);
    res.status(500).send('Server error');
  }
});

app.listen(PORT, () => {
  console.log(`API server listening on port ${PORT}`);
});