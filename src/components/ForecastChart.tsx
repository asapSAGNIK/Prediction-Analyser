import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';
import type { ChartDataPoint } from '../hooks/useForecastData';

interface ForecastChartProps {
    data: ChartDataPoint[];
    loading: boolean;
    error: string | null;
}

const CHART_MARGIN = { top: 8, right: 16, left: 8, bottom: 8 };

/** Format timestamp for X-axis labels */
function formatXAxis(timestamp: number): string {
    const d = new Date(timestamp);
    const day = String(d.getUTCDate()).padStart(2, '0');
    const month = String(d.getUTCMonth() + 1).padStart(2, '0');
    const hours = String(d.getUTCHours()).padStart(2, '0');
    const mins = String(d.getUTCMinutes()).padStart(2, '0');
    return `${hours}:${mins}\n${day}/${month}`;
}

/** Format MW values for Y-axis */
function formatYAxis(value: number): string {
    if (value >= 1000) {
        return `${Math.round(value / 1000)}k`;
    }
    return String(value);
}

/** Custom tooltip component */
function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ dataKey: string; value: number; color: string }> }) {
    if (!active || !payload || payload.length === 0) return null;

    // Get the time from the first payload item
    const firstItem = payload[0];
    const chartPoint = firstItem as unknown as { payload: ChartDataPoint };
    const time = chartPoint.payload?.time;

    let timeLabel = '';
    if (time) {
        const d = new Date(time);
        const day = String(d.getUTCDate()).padStart(2, '0');
        const month = String(d.getUTCMonth() + 1).padStart(2, '0');
        const year = d.getUTCFullYear();
        const hours = String(d.getUTCHours()).padStart(2, '0');
        const mins = String(d.getUTCMinutes()).padStart(2, '0');
        timeLabel = `${day}/${month}/${year} ${hours}:${mins} UTC`;
    }

    return (
        <div className="custom-tooltip">
            <div className="custom-tooltip__time">{timeLabel}</div>
            {payload.map((entry, i) => (
                <div key={i} className="custom-tooltip__row">
                    <span
                        className="custom-tooltip__dot"
                        style={{ background: entry.color }}
                    />
                    <span className="custom-tooltip__label">
                        {entry.dataKey === 'actual' ? 'Actual' : 'Forecast'}
                    </span>
                    <span className="custom-tooltip__value">
                        {entry.value != null
                            ? `${entry.value.toLocaleString()} MW`
                            : '—'}
                    </span>
                </div>
            ))}
        </div>
    );
}

export function ForecastChart({ data, loading, error }: ForecastChartProps) {
    if (loading) {
        return (
            <div className="chart-card" id="chart-panel">
                <div className="chart-card__header">
                    <h2 className="chart-card__title">Wind Power Generation</h2>
                </div>
                <div className="status-container">
                    <div className="spinner" />
                    <span className="status-text">Loading data from Elexon API...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chart-card" id="chart-panel">
                <div className="chart-card__header">
                    <h2 className="chart-card__title">Wind Power Generation</h2>
                </div>
                <div className="status-container">
                    <p className="error-text">⚠ {error}</p>
                    <p className="status-text">Please check your connection and try again.</p>
                </div>
            </div>
        );
    }

    if (data.length === 0) {
        return (
            <div className="chart-card" id="chart-panel">
                <div className="chart-card__header">
                    <h2 className="chart-card__title">Wind Power Generation</h2>
                </div>
                <div className="status-container">
                    <p className="status-text">No data available for the selected time range.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="chart-card" id="chart-panel">
            <div className="chart-card__header">
                <h2 className="chart-card__title">Wind Power Generation</h2>
                <div className="chart-card__legend">
                    <div className="legend-item">
                        <span className="legend-dot legend-dot--actual" />
                        <span>Actual</span>
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot legend-dot--forecast" />
                        <span>Forecast</span>
                    </div>
                </div>
            </div>
            <div className="chart-container">
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart
                        data={data}
                        margin={CHART_MARGIN}
                    >
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="var(--color-grid)"
                            vertical={false}
                        />
                        <XAxis
                            dataKey="timestamp"
                            type="number"
                            domain={['dataMin', 'dataMax']}
                            tickFormatter={formatXAxis}
                            stroke="var(--color-text-muted)"
                            tick={{ fontSize: 11 }}
                            tickLine={false}
                            axisLine={{ stroke: 'var(--color-border)' }}
                            dy={4}
                        />
                        <YAxis
                            tickFormatter={formatYAxis}
                            stroke="var(--color-text-muted)"
                            tick={{ fontSize: 11 }}
                            tickLine={false}
                            axisLine={false}
                            width={50}
                            label={{
                                value: 'Power (MW)',
                                angle: -90,
                                position: 'insideLeft',
                                style: {
                                    fill: 'var(--color-text-muted)',
                                    fontSize: 11,
                                    fontWeight: 500,
                                },
                                offset: -2,
                            }}
                        />
                        <Tooltip
                            content={<CustomTooltip />}
                            cursor={{ stroke: 'var(--color-border)', strokeDasharray: '4 4' }}
                        />
                        <Line
                            type="monotone"
                            dataKey="actual"
                            stroke="var(--color-actual)"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4, strokeWidth: 0 }}
                            connectNulls={false}
                            name="Actual Generation"
                        />
                        <Line
                            type="monotone"
                            dataKey="forecast"
                            stroke="var(--color-forecast)"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4, strokeWidth: 0 }}
                            connectNulls={true}
                            name="Forecasted Generation"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
