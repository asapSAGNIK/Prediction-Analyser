import { useState, useCallback } from 'react';
import { Controls } from './components/Controls';
import { ForecastChart } from './components/ForecastChart';
import { useForecastData } from './hooks/useForecastData';
import './index.css';

/**
 * Creates a local Date object that DISPLAYS as the given UTC values
 * in react-datepicker. We use this because react-datepicker shows
 * local time, but our data is UTC.
 */
function createLocalDateForUTC(year: number, month: number, day: number, hour = 0, min = 0): Date {
  return new Date(year, month - 1, day, hour, min);
}

/**
 * Converts a local Date (as displayed in the picker) to a UTC ISO string
 * for API calls. Treats the local date's face values as UTC.
 */
function toUTCISOString(localDate: Date): string {
  const y = localDate.getFullYear();
  const m = String(localDate.getMonth() + 1).padStart(2, '0');
  const d = String(localDate.getDate()).padStart(2, '0');
  const h = String(localDate.getHours()).padStart(2, '0');
  const min = String(localDate.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${d}T${h}:${min}:00Z`;
}

function App() {
  // Defaults: Jan 1 00:00 to Jan 2 00:00 (displayed as local, treated as UTC)
  const [startTime, setStartTime] = useState(() => createLocalDateForUTC(2024, 1, 1, 0, 0));
  const [endTime, setEndTime] = useState(() => createLocalDateForUTC(2024, 1, 2, 0, 0));
  const [forecastHorizon, setForecastHorizon] = useState(4);

  // Convert displayed dates to UTC ISO strings for the API
  const apiStartTime = useCallback(() => toUTCISOString(startTime), [startTime]);
  const apiEndTime = useCallback(() => toUTCISOString(endTime), [endTime]);

  const { data, loading, error } = useForecastData(
    apiStartTime(),
    apiEndTime(),
    forecastHorizon
  );

  return (
    <div className="app">
      <header className="header">
        <h1 className="header__title">
          <span className="header__accent">REint</span> Wind Forecast Monitor
        </h1>
        <p className="header__subtitle">
          UK National Wind Power Generation — Actual vs Forecasted · January 2024
        </p>
      </header>

      <Controls
        startTime={startTime}
        endTime={endTime}
        forecastHorizon={forecastHorizon}
        onStartTimeChange={setStartTime}
        onEndTimeChange={setEndTime}
        onHorizonChange={setForecastHorizon}
      />

      <ForecastChart data={data} loading={loading} error={error} />

      <footer style={{
        textAlign: 'center',
        marginTop: '24px',
        fontSize: '0.75rem',
        color: 'var(--color-text-muted)',
      }}>
        Data sourced from{' '}
        <a
          href="https://bmrs.elexon.co.uk"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'var(--color-accent)', textDecoration: 'none' }}
        >
          Elexon BMRS
        </a>
        {' '}· Built for REint
      </footer>
    </div>
  );
}

export default App;
