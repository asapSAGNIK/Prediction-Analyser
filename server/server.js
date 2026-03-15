import express from 'express';
import cors from 'cors';
import { fetchActuals, fetchForecasts, matchForecasts } from './utils.js';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

/**
 * GET /api/actuals
 * Query params: from (ISO), to (ISO)
 */
app.get('/api/actuals', async (req, res) => {
    try {
        const { from, to } = req.query;

        if (!from || !to) {
            return res.status(400).json({ error: 'Missing required query params: from, to' });
        }

        const fromDate = new Date(from);
        const toDate = new Date(to);

        const allActuals = await fetchActuals();
        const filtered = allActuals.filter((d) => {
            const st = new Date(d.startTime);
            return st >= fromDate && st <= toDate;
        });

        res.json(filtered);
    } catch (err) {
        console.error('[API] /api/actuals error:', err.message);
        res.status(500).json({ error: 'Failed to fetch actuals data' });
    }
});

/**
 * GET /api/forecasts
 * Query params: from (ISO), to (ISO), horizon (hours, default 4)
 */
app.get('/api/forecasts', async (req, res) => {
    try {
        const { from, to, horizon = '4' } = req.query;

        if (!from || !to) {
            return res.status(400).json({ error: 'Missing required query params: from, to' });
        }

        const horizonHours = parseFloat(horizon);
        if (isNaN(horizonHours) || horizonHours < 0 || horizonHours > 48) {
            return res.status(400).json({ error: 'Horizon must be between 0 and 48' });
        }

        const allForecasts = await fetchForecasts();
        const matched = matchForecasts(allForecasts, from, to, horizonHours);

        res.json(matched);
    } catch (err) {
        console.error('[API] /api/forecasts error:', err.message);
        res.status(500).json({ error: 'Failed to fetch forecast data' });
    }
});

app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`[Server] Running on http://localhost:${PORT}`);
});
