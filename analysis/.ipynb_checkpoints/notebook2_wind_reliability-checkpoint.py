# %% [markdown]
# # Notebook 2: Wind Reliability Analysis
# 
# **Goal**: Understand how reliably wind power can meet electricity demand in the UK.
# 
# Based on historical actual generation data for January 2024, we analyze wind power
# variability and recommend how many MW can be reliably expected.

# %% [markdown]
# ## 1. Data Loading

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.family'] = 'sans-serif'

print("Libraries loaded successfully.")

# %%
# Fetch actual wind generation data for January 2024
print("Fetching actual generation data...")
url = (
    "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream"
    "?publishDateTimeFrom=2024-01-01T00:00:00Z"
    "&publishDateTimeTo=2024-02-01T00:00:00Z"
    "&fuelType=WIND"
)
resp = requests.get(url)
raw = resp.json()

df = pd.DataFrame(raw)
df['startTime'] = pd.to_datetime(df['startTime'])
df = df[
    (df['startTime'] >= '2024-01-01') & 
    (df['startTime'] < '2024-02-01')
].sort_values('startTime').reset_index(drop=True)

print(f"Loaded {len(df)} records")
print(f"Date range: {df['startTime'].min()} to {df['startTime'].max()}")

# %% [markdown]
# ## 2. Time Series Overview

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df['startTime'], df['generation'], color='#4a9eff', linewidth=0.8, alpha=0.9)
ax.fill_between(df['startTime'], df['generation'], alpha=0.15, color='#4a9eff')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Wind Generation (MW)', fontsize=12)
ax.set_title('UK Wind Power Generation — January 2024', fontsize=14, fontweight='bold')
ax.axhline(y=df['generation'].mean(), color='#34d399', linestyle='--', linewidth=1.5,
           label=f'Mean: {df["generation"].mean():,.0f} MW')
ax.axhline(y=df['generation'].min(), color='#f87171', linestyle=':', linewidth=1,
           label=f'Min: {df["generation"].min():,.0f} MW')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('wind_timeseries.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ### Observation
# 
# **[YOUR OBSERVATION HERE]**
# 
# _Example: "Wind generation in January 2024 is highly variable, 
# ranging from X MW to Y MW. There are clear periods of high and low wind."_

# %% [markdown]
# ## 3. Statistical Summary

# %%
gen = df['generation']
stats = {
    'Minimum': f"{gen.min():,.0f} MW",
    'Maximum': f"{gen.max():,.0f} MW",
    'Mean': f"{gen.mean():,.0f} MW",
    'Median': f"{gen.median():,.0f} MW",
    'Std Deviation': f"{gen.std():,.0f} MW",
    'Capacity Factor': f"{gen.mean() / gen.max():.1%}",
    '5th Percentile': f"{gen.quantile(0.05):,.0f} MW",
    '10th Percentile': f"{gen.quantile(0.10):,.0f} MW",
    '25th Percentile': f"{gen.quantile(0.25):,.0f} MW",
}

print(f"\n{'='*45}")
print(f"  Wind Generation Statistics — Jan 2024")
print(f"{'='*45}")
for key, val in stats.items():
    print(f"  {key:25s} {val}")
print(f"{'='*45}")

# %% [markdown]
# ## 4. Distribution of Generation Values

# %%
fig, ax = plt.subplots(figsize=(12, 5))
ax.hist(gen, bins=60, color='#4a9eff', alpha=0.8, edgecolor='white', linewidth=0.5)
ax.axvline(x=gen.mean(), color='#34d399', linestyle='--', linewidth=2,
           label=f'Mean: {gen.mean():,.0f} MW')
ax.axvline(x=gen.median(), color='#fbbf24', linestyle='--', linewidth=2,
           label=f'Median: {gen.median():,.0f} MW')
ax.axvline(x=gen.quantile(0.05), color='#f87171', linestyle='--', linewidth=2,
           label=f'5th percentile: {gen.quantile(0.05):,.0f} MW')
ax.set_xlabel('Wind Generation (MW)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Distribution of Wind Generation — January 2024', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('wind_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ## 5. Reliability Curve — The Key Analysis
# 
# For different MW thresholds, what percentage of time does wind generation
# exceed that level? This tells us how "reliable" a given MW amount is.

# %%
thresholds = np.arange(0, int(gen.max()) + 1000, 500)
reliability = [(gen >= t).mean() * 100 for t in thresholds]

df_reliability = pd.DataFrame({'threshold_mw': thresholds, 'pct_time_above': reliability})

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_reliability['threshold_mw'], df_reliability['pct_time_above'], 
        color='#4a9eff', linewidth=2.5)
ax.fill_between(df_reliability['threshold_mw'], df_reliability['pct_time_above'], 
                alpha=0.1, color='#4a9eff')

# Highlight key reliability levels
for pct, color, style in [(95, '#34d399', '-'), (90, '#fbbf24', '--'), (80, '#f87171', ':')]:
    mw_at_pct = gen.quantile(1 - pct/100)
    ax.axhline(y=pct, color=color, linestyle=style, alpha=0.7, linewidth=1)
    ax.axvline(x=mw_at_pct, color=color, linestyle=style, alpha=0.7, linewidth=1)
    ax.annotate(f'{pct}% → {mw_at_pct:,.0f} MW', 
                xy=(mw_at_pct, pct), fontsize=10, fontweight='bold',
                xytext=(mw_at_pct + 1500, pct + 2), color=color,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

ax.set_xlabel('Wind Generation Threshold (MW)', fontsize=12)
ax.set_ylabel('% of Time Generation Exceeds Threshold', fontsize=12)
ax.set_title('Wind Power Reliability Curve — January 2024', fontsize=14, fontweight='bold')
ax.set_ylim(0, 105)
plt.tight_layout()
plt.savefig('reliability_curve.png', dpi=150, bbox_inches='tight')
plt.show()

# Print key reliability values
print("\nReliability Table:")
print(f"{'Confidence Level':>20s}  {'MW Available':>15s}")
print(f"{'-'*20}  {'-'*15}")
for pct in [99, 95, 90, 85, 80, 75, 50]:
    mw = gen.quantile(1 - pct/100)
    print(f"{pct:>19}%  {mw:>12,.0f} MW")

# %% [markdown]
# ## 6. Low-Wind Period Analysis
# 
# How long do "low wind" periods last? This matters because electricity
# demand is continuous — a 30-minute dip is fine, but hours-long dips are a problem.

# %%
# Define "low wind" as below the 10th percentile
low_threshold = gen.quantile(0.10)
df['is_low'] = df['generation'] < low_threshold

# Find consecutive low-wind periods
df['low_group'] = (df['is_low'] != df['is_low'].shift()).cumsum()
low_periods = df[df['is_low']].groupby('low_group').agg(
    start=('startTime', 'first'),
    end=('startTime', 'last'),
    duration_hours=('startTime', lambda x: len(x) * 0.5),  # 30-min intervals
    min_generation=('generation', 'min'),
    mean_generation=('generation', 'mean'),
).reset_index(drop=True)

print(f"Low wind threshold (10th percentile): {low_threshold:,.0f} MW")
print(f"Number of low-wind periods: {len(low_periods)}")
print(f"Longest low-wind period: {low_periods['duration_hours'].max():.1f} hours")
print(f"Average low-wind duration: {low_periods['duration_hours'].mean():.1f} hours")
print(f"\nTop 5 longest low-wind periods:")
print(low_periods.nlargest(5, 'duration_hours')[['start', 'end', 'duration_hours', 'min_generation']].to_string(index=False))

# %% [markdown]
# ## 7. Generation by Hour of Day
# 
# Does wind power follow a daily pattern?

# %%
df['hour'] = df['startTime'].dt.hour
hourly_gen = df.groupby('hour')['generation'].agg(['mean', 'std', 'min', 'max'])

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(hourly_gen.index, hourly_gen['mean'], color='#4a9eff', alpha=0.8,
       edgecolor='#3a6de8', linewidth=0.5, label='Mean Generation')
ax.errorbar(hourly_gen.index, hourly_gen['mean'], yerr=hourly_gen['std'],
            fmt='none', color='#f87171', alpha=0.6, capsize=3, label='± Std Dev')
ax.set_xlabel('Hour of Day (UTC)', fontsize=12)
ax.set_ylabel('Generation (MW)', fontsize=12)
ax.set_title('Average Wind Generation by Hour — January 2024', fontsize=14, fontweight='bold')
ax.set_xticks(range(24))
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig('generation_by_hour.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ### Observation
# 
# **[YOUR OBSERVATION HERE]**
# 
# _Example: "Wind generation shows [little/some] daily pattern. 
# Average generation is [higher/lower] during [morning/evening] hours."_

# %% [markdown]
# ## 8. Recommendation
# 
# **[THIS IS THE MOST IMPORTANT PART — WRITE YOUR RECOMMENDATION HERE]**
# 
# Based on the reliability curve above, here's how to think about it:
# 
# - At **95% reliability**: wind provides at least X MW, 95% of the time
# - At **90% reliability**: wind provides at least X MW, 90% of the time  
# - At **80% reliability**: wind provides at least X MW, 80% of the time
# 
# **My recommendation:**
# 
# _"Based on the analysis of January 2024 UK wind generation data, I recommend 
# that approximately **X MW** of wind power can be reliably expected to meet 
# electricity demand._
# 
# _I chose a [90%/95%] confidence level because [your reasoning — e.g., 
# "critical infrastructure requires high reliability" or "remaining demand 
# can be covered by other sources like gas as backup"]._
# 
# _However, this recommendation comes with caveats:_
# - _January may not be representative of all months (wind patterns are seasonal)_
# - _Low-wind periods lasting up to X hours require backup capacity_
# - _[Any other observations from your analysis]"_
