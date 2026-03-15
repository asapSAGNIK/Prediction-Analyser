const ELEXON_BASE = 'https://data.elexon.co.uk/bmrs/api/v1/datasets';

// In-memory cache — Jan 2024 data is historical, fetch once
let actualsCache = null;
let forecastsCache = null;

/**
 * Fetches all FUELHH (actual wind generation) data for January 2024.
 * Caches in memory after first fetch.
 */
export async function fetchActuals() {
    if (actualsCache) return actualsCache;

    console.log('[Cache] Fetching actuals from Elexon API...');
    const url = `${ELEXON_BASE}/FUELHH/stream?publishDateTimeFrom=2024-01-01T00:00:00Z&publishDateTimeTo=2024-02-01T00:00:00Z&fuelType=WIND`;

    const res = await fetch(url);
    if (!res.ok) throw new Error(`Elexon FUELHH API error: ${res.status}`);

    const data = await res.json();

    actualsCache = data
        .filter((d) => {
            const st = new Date(d.startTime);
            return st >= new Date('2024-01-01T00:00:00Z') && st < new Date('2024-02-01T00:00:00Z');
        })
        .map((d) => ({
            startTime: d.startTime,
            generation: d.generation,
        }))
        .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

    console.log(`[Cache] Actuals cached: ${actualsCache.length} records`);
    return actualsCache;
}

/**
 * Fetches all WINDFOR (forecast wind generation) data for January 2024.
 * Includes forecasts published before Jan to cover early targets.
 * Caches in memory after first fetch.
 */
export async function fetchForecasts() {
    if (forecastsCache) return forecastsCache;

    console.log('[Cache] Fetching forecasts from Elexon API...');
    const url = `${ELEXON_BASE}/WINDFOR/stream?publishDateTimeFrom=2023-12-30T00:00:00Z&publishDateTimeTo=2024-02-01T00:00:00Z`;

    const res = await fetch(url);
    if (!res.ok) throw new Error(`Elexon WINDFOR API error: ${res.status}`);

    const data = await res.json();

    forecastsCache = data
        .filter((d) => {
            const startTime = new Date(d.startTime);
            const publishTime = new Date(d.publishTime);
            const horizonMs = startTime - publishTime;
            const horizonHours = horizonMs / (1000 * 60 * 60);

            return (
                startTime >= new Date('2024-01-01T00:00:00Z') &&
                startTime < new Date('2024-02-01T00:00:00Z') &&
                horizonHours >= 0 &&
                horizonHours <= 48
            );
        })
        .map((d) => ({
            startTime: d.startTime,
            publishTime: d.publishTime,
            generation: d.generation,
        }))
        .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));

    console.log(`[Cache] Forecasts cached: ${forecastsCache.length} records`);
    return forecastsCache;
}

/**
 * For each target time in the requested range, finds the latest forecast
 * published at least `horizonHours` before the target time.
 */
export function matchForecasts(forecasts, from, to, horizonHours) {
    const fromDate = new Date(from);
    const toDate = new Date(to);

    // Group forecasts by startTime
    const byStartTime = new Map();
    for (const f of forecasts) {
        const key = f.startTime;
        if (!byStartTime.has(key)) byStartTime.set(key, []);
        byStartTime.get(key).push(f);
    }

    const results = [];

    for (const [startTimeStr, entries] of byStartTime) {
        const startTime = new Date(startTimeStr);
        if (startTime < fromDate || startTime > toDate) continue;

        const deadline = new Date(startTime.getTime() - horizonHours * 60 * 60 * 1000);

        let best = null;
        for (const entry of entries) {
            const pubTime = new Date(entry.publishTime);
            if (pubTime <= deadline) {
                if (!best || pubTime > new Date(best.publishTime)) {
                    best = entry;
                }
            }
        }

        if (best) {
            results.push(best);
        }
    }

    return results.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
}
