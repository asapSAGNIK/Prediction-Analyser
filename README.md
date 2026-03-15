# REint Wind Forecast Monitor

A full-stack web application designed to visualize and analyze UK national wind power generation. This project compares **actual** wind generation against **forecasted** generation using real historical data (from January 2024) pulled directly from the Elexon BMRS API.

The core technical challenge addressed by this application is the implementation of a **forecast horizon matching algorithm**. The system efficiently sifts through thousands of overlapping, real-time predictions to isolate the single most relevant forecast for any given target time and lookahead horizon.

## Architecture & Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Recharts, `react-datepicker`.
- **Backend/API**: Node.js 20, Express (ESM).
- **Styling**: Custom CSS Design System (Dynamic dark mode, Inter font, purely vanilla CSS for maximum performance, no heavy UI libraries).
- **Data Source**: Elexon BMRS API (`FUELHH` for actuals, `WINDFOR` for forecasts).

## Key Features

1. **Horizon Matching Engine**: The backend implements an O(N) map-reducible grouping algorithm to instantly match actual readings with the exact forecast published `H` hours prior.
2. **In-Memory Caching Strategy**: To prevent rate-limiting and maximize UI responsiveness, the entire January 2024 dataset is cached into RAM on the first load, dropping subsequent query times to <10ms.
3. **Continuous Chart Rendering**: Recharts is optimized to bridge the gap between 30-minute actual data and hourly forecast data natively.
4. **Professional UI System**: Responsive, accessible, and curated dark aesthetic tailored for trading/monitoring environments.

## How to Run Locally

### Prerequisites
- Node.js (v18 or v20 recommended)
- `npm`

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Both Servers (Concurrently)
```bash
npm run dev
```
*Note: This command uses `concurrently` to spin up both the Vite frontend (`http://localhost:5173`) and the Express backend (`http://localhost:3001` with API proxying) simultaneously.*

### 3. Open in Browser
Visit `http://localhost:5173`

## Jupyter Analysis Notebooks

This repository also contains two Python/Jupyter data-science notebooks analyzing the forecast models.

- `analysis/notebook1_forecast_error.ipynb`: Analyzes the forecasting model's prediction decay over varying horizons (MAE/RMSE) and identifies diurnal bias patterns.
- `analysis/notebook2_wind_reliability.ipynb`: Constructs a reliability curve to determine the baseline gigawatt output the UK grid can depend upon at a 90% confidence level during winter months.

To run the analysis:
```bash
cd analysis
pip install -r requirements.txt
jupyter notebook
```

## Potential Next Steps / scale

- **Live Data Streams**: Hook the backend up to Elexon's live WebSockets instead of the historical REST APIs.
- **Database Layer**: Replace the Node.js memory cache with a timeseries database (e.g., TimescaleDB or InfluxDB) to support multi-year queries without OOM risks.
- **Caching Layer**: Implement Redis for distributed caching if deploying multiple Node.js workers.
