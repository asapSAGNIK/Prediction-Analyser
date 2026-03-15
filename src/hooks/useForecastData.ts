import { useState, useEffect, useCallback } from 'react';

export interface ActualDataPoint {
    startTime: string;
    generation: number;
}

export interface ForecastDataPoint {
    startTime: string;
    generation: number;
    publishTime: string;
}

export interface ChartDataPoint {
    time: string;
    timestamp: number;
    actual?: number;
    forecast?: number;
}

interface UseForecastDataReturn {
    data: ChartDataPoint[];
    loading: boolean;
    error: string | null;
}

/**
 * Custom hook to fetch actuals and forecast data from the API,
 * merges them into a single array suitable for Recharts.
 */
export function useForecastData(
    fromISO: string,
    toISO: string,
    forecastHorizon: number
): UseForecastDataReturn {
    const [data, setData] = useState<ChartDataPoint[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const [actualsRes, forecastsRes] = await Promise.all([
                fetch(`/api/actuals?from=${encodeURIComponent(fromISO)}&to=${encodeURIComponent(toISO)}`),
                fetch(`/api/forecasts?from=${encodeURIComponent(fromISO)}&to=${encodeURIComponent(toISO)}&horizon=${forecastHorizon}`),
            ]);

            if (!actualsRes.ok) throw new Error('Failed to fetch actuals');
            if (!forecastsRes.ok) throw new Error('Failed to fetch forecasts');

            const actuals: ActualDataPoint[] = await actualsRes.json();
            const forecasts: ForecastDataPoint[] = await forecastsRes.json();

            // Merge both datasets by startTime
            const timeMap = new Map<string, ChartDataPoint>();

            for (const a of actuals) {
                const key = a.startTime;
                if (!timeMap.has(key)) {
                    timeMap.set(key, {
                        time: key,
                        timestamp: new Date(key).getTime(),
                    });
                }
                timeMap.get(key)!.actual = a.generation;
            }

            for (const f of forecasts) {
                const key = f.startTime;
                if (!timeMap.has(key)) {
                    timeMap.set(key, {
                        time: key,
                        timestamp: new Date(key).getTime(),
                    });
                }
                timeMap.get(key)!.forecast = f.generation;
            }

            // Sort by time
            const merged = Array.from(timeMap.values()).sort(
                (a, b) => a.timestamp - b.timestamp
            );

            setData(merged);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setData([]);
        } finally {
            setLoading(false);
        }
    }, [fromISO, toISO, forecastHorizon]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, loading, error };
}
