# %% [markdown]
# # Notebook 1: Forecast Error Analysis
# 
# **Goal**: Understand the error characteristics of the UK wind power forecast model.
# 
# We analyze forecasts for January 2024 from the Elexon BMRS API, comparing
# predicted vs actual wind generation to understand:
# - Overall forecast accuracy (mean, median, p99 errors)
# - How accuracy changes with forecast horizon
# - Whether accuracy varies by time of day

# %% [markdown]
# ## 1. Data Loading
# Fetch actual wind generation (FUELHH) and forecast data (WINDFOR) from the Elexon API.

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

# Set up matplotlib style for clean charts
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.family'] = 'sans-serif'

print("Libraries loaded successfully.")

# %%
# Fetch ACTUAL wind generation data for January 2024
print("Fetching actual generation data...")
actuals_url = (
    "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream"
    "?publishDateTimeFrom=2024-01-01T00:00:00Z"
    "&publishDateTimeTo=2024-02-01T00:00:00Z"
    "&fuelType=WIND"
)
actuals_resp = requests.get(actuals_url)
actuals_raw = actuals_resp.json()
print(f"Fetched {len(actuals_raw)} actual records")

# Fetch FORECAST wind generation data
print("Fetching forecast data...")
forecasts_url = (
    "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"
    "?publishDateTimeFrom=2023-12-30T00:00:00Z"
    "&publishDateTimeTo=2024-02-01T00:00:00Z"
)
forecasts_resp = requests.get(forecasts_url)
forecasts_raw = forecasts_resp.json()
print(f"Fetched {len(forecasts_raw)} forecast records")

# %%
# Convert to DataFrames
df_actuals = pd.DataFrame(actuals_raw)
df_actuals['startTime'] = pd.to_datetime(df_actuals['startTime'])
df_actuals = df_actuals[
    (df_actuals['startTime'] >= '2024-01-01') & 
    (df_actuals['startTime'] < '2024-02-01')
].sort_values('startTime').reset_index(drop=True)

df_forecasts = pd.DataFrame(forecasts_raw)
df_forecasts['startTime'] = pd.to_datetime(df_forecasts['startTime'])
df_forecasts['publishTime'] = pd.to_datetime(df_forecasts['publishTime'])

# Calculate forecast horizon in hours
df_forecasts['horizon_hours'] = (
    df_forecasts['startTime'] - df_forecasts['publishTime']
).dt.total_seconds() / 3600

# Keep only valid forecasts: horizon 0-48h, targeting January 2024
df_forecasts = df_forecasts[
    (df_forecasts['startTime'] >= '2024-01-01') &
    (df_forecasts['startTime'] < '2024-02-01') &
    (df_forecasts['horizon_hours'] >= 0) &
    (df_forecasts['horizon_hours'] <= 48)
].sort_values('startTime').reset_index(drop=True)

print(f"Actuals: {len(df_actuals)} records")
print(f"Forecasts: {len(df_forecasts)} records")
print(f"Actual date range: {df_actuals['startTime'].min()} to {df_actuals['startTime'].max()}")

# %% [markdown]
# ## 2. Matching Forecasts to Actuals
# 
# For each horizon value, we find the latest forecast published before the deadline
# and compare it to the actual generation.

# %%
def get_errors_for_horizon(df_actuals, df_forecasts, horizon_hours):
    """
    For each actual measurement, find the best matching forecast
    at the given horizon and compute the error.
    """
    results = []
    
    for _, actual_row in df_actuals.iterrows():
        target_time = actual_row['startTime']
        deadline = target_time - pd.Timedelta(hours=horizon_hours)
        
        # Find forecasts for this target time, published before the deadline
        candidates = df_forecasts[
            (df_forecasts['startTime'] == target_time) &
            (df_forecasts['publishTime'] <= deadline)
        ]
        
        if len(candidates) == 0:
            continue
        
        # Pick the latest (most recent) forecast
        best = candidates.loc[candidates['publishTime'].idxmax()]
        
        error = best['generation'] - actual_row['generation']
        results.append({
            'startTime': target_time,
            'actual': actual_row['generation'],
            'forecast': best['generation'],
            'error': error,
            'abs_error': abs(error),
            'horizon': horizon_hours,
            'hour_of_day': target_time.hour,
        })
    
    return pd.DataFrame(results)

# Compute errors for a standard 4-hour horizon
df_errors_4h = get_errors_for_horizon(df_actuals, df_forecasts, 4)
print(f"Matched {len(df_errors_4h)} actual-forecast pairs at 4h horizon")

# %% [markdown]
# ## 3. Basic Error Statistics (4-hour horizon)
# 
# These metrics tell us how accurate the forecasts are overall.

# %%
def print_error_stats(df, horizon_label):
    """Print a summary table of error statistics."""
    errors = df['error']
    abs_errors = df['abs_error']
    
    stats = {
        'Mean Error (Bias)': f"{errors.mean():.1f} MW",
        'Mean Absolute Error (MAE)': f"{abs_errors.mean():.1f} MW",
        'Median Absolute Error': f"{abs_errors.median():.1f} MW",
        'P99 Absolute Error': f"{abs_errors.quantile(0.99):.1f} MW",
        'RMSE': f"{np.sqrt((errors**2).mean()):.1f} MW",
        'Max Absolute Error': f"{abs_errors.max():.1f} MW",
    }
    
    print(f"\n{'='*50}")
    print(f"  Error Statistics — {horizon_label}")
    print(f"{'='*50}")
    for key, val in stats.items():
        print(f"  {key:30s} {val}")
    print(f"{'='*50}")

print_error_stats(df_errors_4h, "4-hour horizon")

# %% [markdown]
# ## 4. Error vs Forecast Horizon
# 
# **Key question**: Do forecasts get worse the further ahead they predict?

# %%
# Compute errors for multiple horizons
horizons = [1, 2, 4, 6, 8, 12, 16, 20, 24, 30, 36, 42, 48]
horizon_stats = []

for h in horizons:
    df_h = get_errors_for_horizon(df_actuals, df_forecasts, h)
    if len(df_h) == 0:
        continue
    horizon_stats.append({
        'horizon': h,
        'mae': df_h['abs_error'].mean(),
        'rmse': np.sqrt((df_h['error']**2).mean()),
        'median_ae': df_h['abs_error'].median(),
        'p99': df_h['abs_error'].quantile(0.99),
        'bias': df_h['error'].mean(),
        'count': len(df_h),
    })

df_horizon = pd.DataFrame(horizon_stats)

# Plot MAE and RMSE vs horizon
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_horizon['horizon'], df_horizon['mae'], 'o-', color='#4a9eff', 
        linewidth=2, markersize=6, label='MAE')
ax.plot(df_horizon['horizon'], df_horizon['rmse'], 's-', color='#f87171', 
        linewidth=2, markersize=6, label='RMSE')
ax.set_xlabel('Forecast Horizon (hours)', fontsize=12)
ax.set_ylabel('Error (MW)', fontsize=12)
ax.set_title('Forecast Error vs Horizon — January 2024', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.set_xticks(horizons)
plt.tight_layout()
plt.savefig('error_vs_horizon.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nHorizon Statistics Table:")
print(df_horizon[['horizon', 'mae', 'rmse', 'bias', 'count']].to_string(index=False))

# %% [markdown]
# ### Observation — Error vs Horizon
# 
# **[YOUR OBSERVATION HERE]**
# 
# _Look at the chart above and write 2-3 sentences. For example:_
# _"As the forecast horizon increases from 1h to 48h, the MAE increases from 
# approximately X MW to Y MW. This confirms that shorter-term forecasts are 
# significantly more accurate than longer-term ones. The steepest increase 
# in error occurs between X and Y hours."_

# %% [markdown]
# ## 5. Error by Time of Day
# 
# **Key question**: Are forecasts more accurate at certain hours?

# %%
# Use 4-hour horizon errors grouped by hour of day
hourly_errors = df_errors_4h.groupby('hour_of_day')['abs_error'].agg(['mean', 'median', 'std'])
hourly_errors.columns = ['MAE', 'Median AE', 'Std Dev']

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(hourly_errors.index, hourly_errors['MAE'], color='#4a9eff', alpha=0.8, 
              edgecolor='#3a6de8', linewidth=0.5)
ax.set_xlabel('Hour of Day (UTC)', fontsize=12)
ax.set_ylabel('Mean Absolute Error (MW)', fontsize=12)
ax.set_title('Forecast Error by Hour of Day — 4h Horizon', fontsize=14, fontweight='bold')
ax.set_xticks(range(24))
plt.tight_layout()
plt.savefig('error_by_hour.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nHourly Error Table (4h horizon):")
print(hourly_errors.to_string())

# %% [markdown]
# ### Observation — Time of Day
# 
# **[YOUR OBSERVATION HERE]**
# 
# _Look at the bar chart above. Are some hours worse than others? Example:_
# _"Forecast errors tend to be higher during [morning/evening/night] hours, 
# with peak MAE of X MW at hour Y. This could be because wind patterns 
# change more rapidly during [those periods]."_

# %% [markdown]
# ## 6. Error Distribution

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram of errors (with sign — shows bias)
axes[0].hist(df_errors_4h['error'], bins=50, color='#4a9eff', alpha=0.8, edgecolor='white')
axes[0].axvline(x=0, color='#f87171', linestyle='--', linewidth=1.5, label='Zero error')
axes[0].axvline(x=df_errors_4h['error'].mean(), color='#34d399', linestyle='--', 
                linewidth=1.5, label=f'Mean: {df_errors_4h["error"].mean():.0f} MW')
axes[0].set_xlabel('Error (MW)', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)
axes[0].set_title('Error Distribution (4h horizon)', fontsize=13, fontweight='bold')
axes[0].legend()

# Histogram of absolute errors
axes[1].hist(df_errors_4h['abs_error'], bins=50, color='#34d399', alpha=0.8, edgecolor='white')
axes[1].axvline(x=df_errors_4h['abs_error'].median(), color='#f87171', linestyle='--',
                linewidth=1.5, label=f'Median: {df_errors_4h["abs_error"].median():.0f} MW')
axes[1].set_xlabel('Absolute Error (MW)', fontsize=11)
axes[1].set_ylabel('Frequency', fontsize=11)
axes[1].set_title('Absolute Error Distribution (4h horizon)', fontsize=13, fontweight='bold')
axes[1].legend()

plt.tight_layout()
plt.savefig('error_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ### Observation — Error Distribution
# 
# **[YOUR OBSERVATION HERE]**
# 
# _Example: "The error distribution is approximately normal/skewed. 
# The mean bias of X MW suggests the model tends to over/under-predict 
# wind generation. Most errors fall within ±X MW."_

# %% [markdown]
# ## 7. Conclusions
# 
# **[WRITE YOUR CONCLUSIONS HERE — 4-5 sentences summarizing what you found]**
# 
# _Example structure:_
# 
# _1. Overall, the wind power forecasts for January 2024 have a MAE of approximately 
# X MW at a 4-hour horizon, representing about Y% of mean generation._
# 
# _2. Forecast accuracy degrades with longer horizons — MAE increases from X MW 
# at 1h to Y MW at 48h, confirming that shorter-range predictions are more reliable._
# 
# _3. Time-of-day analysis shows [pattern], suggesting [reason]._
# 
# _4. The error distribution shows [pattern], with a slight [positive/negative] bias 
# indicating the model tends to [over/under]-predict._
# 
# _5. To improve forecast reliability, focus on [shorter horizons / specific time periods / etc]._
