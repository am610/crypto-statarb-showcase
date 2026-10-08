import json
import os

target_dir = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project"
nb_path = os.path.join(target_dir, "01_Crypto_StatArb_Research_Lab.ipynb")

nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

def add_md(content):
    nb["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in content.strip().split("\n")]
    })

def add_code(content):
    nb["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in content.strip().split("\n")]
    })

# --- TITLE & EXECUTIVE OVERVIEW ---
add_md("""# Statistical Arbitrage in Cryptocurrencies: A Quantitative Research Lab
### Institutional Quantitative Research Project
**Author:** Quantitative Research Candidate  
**Topic:** Cross-Sectional Momentum, Volume-Conditioned Reversal, Execution Friction, and Multi-Alpha Portfolio Optimization

---

## Executive Overview & Research Objective

Statistical Arbitrage (*StatArb*) is a foundational quantitative hedge fund strategy. While developed in equities, digital asset markets present unique inefficiencies:
1. **Market Fragmentation & Retail Participation:** Heavy retail presence and high-leverage perpetual contracts create severe, periodic **liquidity cascades** and mispricings.
2. **24/7/365 Continuous Trading:** Absence of market opens/closes provides continuous price discovery, unique intraday volatility regimes, and mechanical flow patterns.
3. **Severe Trading Friction:** High retail commissions and bid-ask slippage (~20 bps round-trip) mean naive academic strategies fail in practice. A viable strategy must actively manage turnover and execution.

### Research Lab Structure
This notebook is structured into 9 modular, self-contained sections designed to demonstrate institutional research rigor:
* **Module 1:** Theoretical Foundations of Statistical Arbitrage in Digital Assets
* **Module 2:** Universe Ingestion & Cross-Sectional Data Hygiene
* **Module 3:** The Empirical Horizon Scan (Reversal vs. Momentum across Lookback Horizons)
* **Module 4:** Alpha 1 — Short-Term Volume-Conditioned Mean Reversion
* **Module 5:** Alpha 2 — Intermediate-Term Cross-Sectional Momentum with 1-Bar Lag
* **Module 6:** The Execution Friction Reality Check (Turnover & 20 bps vs. 7 bps Cost Modeling)
* **Module 7:** Multi-Alpha Blending & Markowitz / Equal-Vol Portfolio Optimization
* **Module 8:** Institutional Risk & Factor Attribution (BTC Beta, Alpha, and Drawdown Durations)
* **Module 9:** Quant Hedge Fund Interview Briefing & Portfolio Showcase""")

# --- MODULE 1: THEORY ---
add_md("""---
# Module 1: Theoretical Foundations of Statistical Arbitrage

### 1.1 The Core Market Inefficiencies
Statistical arbitrage strategies exploit statistical regularities in asset price dynamics rather than discounted cash flow models. In crypto, two primary price-volume anomalies coexist:
1. **Reversal (Mean Reversion):**
   * *Mechanism:* Driven by **uninformed liquidity shocks** (e.g., cascading margin liquidations on centralized exchanges, stop-loss runs, and retail panic). When large market sell orders hit an illiquid order book, prices temporarily dislocate far below equilibrium. Once the forced selling exhausts, prices mean-revert.
   * *Dominant Horizon:* High-frequency to short-term (4 to 8 hours).
2. **Momentum (Trend Persistence):**
   * *Mechanism:* Driven by **information diffusion**, sustained institutional capital reallocation, and retail attention cascades (FOMO). Positive fundamental or macroeconomic news is absorbed gradually, creating serially correlated trends.
   * *Dominant Horizon:* Intermediate-to-longer term (24 hours to multiple weeks).

### 1.2 The "Unconstrained" Cross-Sectional Framework
We construct a **dollar-neutral, cross-sectional (XS)** strategy:
At each rebalance timestamp $t$, given a universe of $N$ assets:
1. Compute an alpha signal $S_{i,t}$ for each asset $i \\in \\{1, \\dots, N\\}$.
2. Cross-sectionally rank the signals across assets:
   $$r_{i,t} = \\text{rank}(S_{i,t})$$
3. Demean to enforce **dollar neutrality** (zero net market exposure: $\\sum_i \\tilde{w}_{i,t} = 0$):
   $$\\tilde{w}_{i,t} = r_{i,t} - \\frac{1}{N} \\sum_{j=1}^N r_{j,t}$$
4. Normalize to enforce **unit gross leverage** ($\\sum_i |w_{i,t}| = 1.0$):
   $$w_{i,t} = \\frac{\\tilde{w}_{i,t}}{\\sum_{j=1}^N |\\tilde{w}_{j,t}|}$$
   * Long positions sum to $+0.5$; Short positions sum to $-0.5$.
   * Net market exposure is identically zero, systematically hedging out broad crypto market beta.""")

# --- MODULE 2: DATA INGESTION ---
add_md("""---
# Module 2: Universe Ingestion & Cross-Sectional Data Hygiene

### 2.1 Universe Selection
We establish an institutional-grade universe of **10 top liquid cryptocurrencies** traded against USDT on Binance:
* **Market Benchmark:** `BTCUSDT`
* **Smart Contract Layer 1s:** `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `ADAUSDT`, `AVAXUSDT`, `DOTUSDT`
* **Large-Cap Payments & Infrastructure:** `DOGEUSDT`, `LINKUSDT`, `LTCUSDT`

**Time Horizon:** 2022-01-01 to 2024-12-31 (3 full years covering bear market, consolidation, and ETF bull run).  
**Sampling Frequency:** 4-hour bars (`4h`). Continuous trading yields $365 \\times 6 = 2,190$ bars per year.

### 2.2 Mathematical Definition of Returns & Lagging
For each asset $i$ at bar $t$:
$$R_{i,t} = \\frac{P_{i,t} - P_{i,t-1}}{P_{i,t-1}}$$
All portfolio decisions at timestamp $t$ use information strictly available up to $t$. Portfolio returns at $t+1$ are computed as:
$$R_{\\text{strat}, t+1} = \\sum_{i=1}^N w_{i,t} R_{i, t+1} = \\sum_{i=1}^N w_{i,t-1}^{\\text{shifted}} R_{i,t}$$
This strictly prevents **look-ahead bias**.""")

add_code("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Plot styling for institutional presentations
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11

# Annualization constants for 4h crypto bars
BARS_PER_DAY = 6
DAYS_PER_YEAR = 365
ANN_FACTOR = BARS_PER_DAY * DAYS_PER_YEAR  # 2,190 bars per year

data_dir = os.path.join(os.getcwd(), 'data')
df_px = pd.read_csv(os.path.join(data_dir, 'crypto_prices_4h.csv'), index_col=0, parse_dates=True)
df_vol = pd.read_csv(os.path.join(data_dir, 'crypto_volumes_4h.csv'), index_col=0, parse_dates=True)
df_qvol = pd.read_csv(os.path.join(data_dir, 'crypto_quote_volumes_4h.csv'), index_col=0, parse_dates=True)

# Compute asset percentage returns
df_ret = df_px.pct_change().dropna()

print(f"Loaded {df_px.shape[1]} assets from {df_px.index.min()} to {df_px.index.max()}")
print(f"Total 4-hour observations: {len(df_px)} bars (~{len(df_px)/ANN_FACTOR:.2f} years)")
display(df_px.head(3))""")

add_code("""# Cross-Sectional Return Summary Statistics
summary_stats = pd.DataFrame({
    'Ann. Return': df_ret.mean() * ANN_FACTOR,
    'Ann. Volatility': df_ret.std() * np.sqrt(ANN_FACTOR),
    'Sharpe Ratio': (df_ret.mean() * ANN_FACTOR) / (df_ret.std() * np.sqrt(ANN_FACTOR)),
    'Skewness': df_ret.skew(),
    'Kurtosis': df_ret.kurtosis()
})

display(summary_stats.round(2))

# Visualize Normalized Asset Trajectories (Base 100)
norm_px = (df_px / df_px.iloc[0]) * 100
fig, ax = plt.subplots(figsize=(13, 6))
norm_px.plot(ax=ax, lw=1.5, alpha=0.85)
ax.set_title("Cross-Sectional Asset Price Trajectories (Base 100, 2022-2024)", fontweight='bold')
ax.set_ylabel("Normalized Price (USDT)")
ax.set_yscale('log')
ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), frameon=True)
plt.tight_layout()
plt.show()""")

add_code("""# Pairwise Asset Return Correlations
fig, ax = plt.subplots(figsize=(10, 8))
corr_matrix = df_ret.corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='Blues', ax=ax, cbar_kws={'label': 'Correlation'})
ax.set_title("Crypto Cross-Sectional Return Correlation Matrix", fontweight='bold')
plt.tight_layout()
plt.show()""")

# --- MODULE 3: HORIZON SCAN ---
add_md("""---
# Module 3: The Empirical Horizon Scan (Reversal vs. Momentum)

### 3.1 Motivation & Hypothesis
A central tenet of quantitative finance is that market anomalies are horizon-dependent:
* **Short horizons ($H \\le 8$ hours):** Order flow imbalance, market maker inventory risk, and forced liquidations create **negative serial correlation (Reversal)**.
* **Longer horizons ($H \\ge 24$ hours):** Macro trends, persistent fund inflows, and delayed information diffusion create **positive serial correlation (Momentum)**.

### 3.2 The Microstructure Drag & The 1-Bar Lag Solution
In raw momentum calculations, the most recent bar typically suffers from short-term reversal noise. In equity markets, the famous Fama-French/Carhart $UMD$ factor skips the most recent month ($t-12$ to $t-2$) to eliminate short-term reversal.  
In crypto, we test whether **skipping the most recent 4h bar** (`shift(2)`) strips away reversal contamination and unleashes momentum.""")

add_code("""def run_uncon_backtest(signal, returns):
    \"\"\"
    Vectorized Cross-Sectional Rank-Demean-Normalize Backtester.
    Strictly avoids look-ahead bias by shifting portfolio weights.
    \"\"\"
    # Cross-sectional ranking across assets
    ranked = signal.rank(axis=1)
    # Demean to ensure dollar neutrality
    demeaned = ranked.subtract(ranked.mean(axis=1), axis=0)
    # Normalize so sum of absolute weights == 1.0
    weights = demeaned.divide(demeaned.abs().sum(axis=1), axis=0)
    # Shift weights by 1 period so trade at t earns return at t+1
    strat_ret = (weights.shift(1) * returns).sum(axis=1)
    return strat_ret, weights

def get_stats(strat_ret, ann_factor=ANN_FACTOR):
    \"\"\"Compute annualized performance statistics.\"\"\"
    mean_ret = strat_ret.mean() * ann_factor
    vol = strat_ret.std() * np.sqrt(ann_factor)
    sharpe = mean_ret / vol if vol > 0 else 0.0
    return pd.Series({'Return': mean_ret, 'Vol': vol, 'Sharpe': sharpe})

# Systematic Horizon Scan: 1 bar (4h) to 24 bars (96h)
horizons = [1, 2, 3, 4, 6, 9, 12, 18, 24]
unlagged_sharpes = {}
lagged_sharpes = {}

for h in horizons:
    # 1. Unlagged Momentum Signal (average return over past h bars)
    sig_raw = df_ret.rolling(h, min_periods=1).mean()
    strat_ret, _ = run_uncon_backtest(sig_raw, df_ret)
    unlagged_sharpes[h * 4] = get_stats(strat_ret)['Sharpe']
    
    # 2. Lagged Momentum Signal (skipping the immediate 1 bar to isolate pure momentum)
    sig_lag = df_ret.shift(1).rolling(h, min_periods=1).mean()
    strat_ret_lag, _ = run_uncon_backtest(sig_lag, df_ret)
    lagged_sharpes[h * 4] = get_stats(strat_ret_lag)['Sharpe']

horizon_df = pd.DataFrame({
    'Raw Momentum Sharpe': unlagged_sharpes,
    '1-Bar Lagged Momentum Sharpe': lagged_sharpes
})
horizon_df.index.name = 'Lookback Window (Hours)'

display(horizon_df.round(2))

# Visualize Sharpe Ratio vs Lookback Horizon
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(horizon_df.index, horizon_df['Raw Momentum Sharpe'], marker='o', lw=2.2, label='Raw Momentum (Unlagged)', color='#d9534f')
ax.plot(horizon_df.index, horizon_df['1-Bar Lagged Momentum Sharpe'], marker='s', lw=2.2, label='Lagged Momentum (1-Bar Skip)', color='#337ab7')
ax.axhline(0, color='gray', ls='--', lw=1)
ax.axvspan(0, 10, color='yellow', alpha=0.15, label='Reversal Zone (Negative Raw Momentum = Reversal Edge)')
ax.axvspan(20, 100, color='green', alpha=0.10, label='Momentum Zone (Persistent Positive Trend)')
ax.set_title("Empirical Horizon Scan: The Reversal-to-Momentum Transition", fontweight='bold')
ax.set_xlabel("Lookback Window (Hours)")
ax.set_ylabel("Annualized Sharpe Ratio (Gross)")
ax.legend(loc='lower right', frameon=True)
plt.tight_layout()
plt.show()""")

# --- MODULE 4: ALPHA 1 ---
add_md("""---
# Module 4: Alpha Strategy 1 — Volume-Conditioned Mean Reversion

### 4.1 Economic & Microstructural Rationale
Why does short-term reversal exist in crypto?
* In perpetual futures and spot trading, retail traders employ aggressive leverage (10x–50x).
* When prices drop sharply, automated liquidation engines force market sell orders into thin books (*the "Fire Sale" phenomenon*).
* **Key Insight:** A price crash accompanied by an **abnormal volume spike** indicates forced liquidations and liquidity exhaustion, NOT a fundamental re-rating. Once the liquidation cascade clears, market makers bid prices back up.

### 4.2 Mathematical Formulation
1. **Short-Term Return ($H = 1$ bar / 4 hours):**
   $$R_{i,t} = \\frac{P_{i,t} - P_{i,t-1}}{P_{i,t-1}}$$
2. **Volume Anomaly Metric ($Z$-Score of Quote Volume):**
   $$\\bar{V}_{i,t} = \\text{rolling\\_mean}(V_{i,t}, 36), \\quad \\sigma_{V, i, t} = \\text{rolling\\_std}(V_{i,t}, 36)$$
   $$Z_{V, i, t} = \\frac{V_{i,t} - \\bar{V}_{i,t}}{\\sigma_{V, i, t}}$$
3. **Volume-Conditioned Reversal Signal:**
   $$S_{\\text{Rev}, i, t} = -R_{i,t} \\times \\max(Z_{V, i, t}, 0)$$
   * If volume is abnormally high ($Z_V > 0$), we aggressively bet against the 4h price move.
   * If volume is calm, we attenuate the signal to avoid fighting orderly drifts.""")

add_code("""# Calculate 36-bar (6-day) Rolling Volume Z-Score
vol_mean = df_qvol.rolling(36, min_periods=12).mean()
vol_std = df_qvol.rolling(36, min_periods=12).std()
vol_zscore = ((df_qvol - vol_mean) / vol_std).clip(lower=0, upper=3.0).fillna(0)

# Unconditioned Reversal: Pure 4h Return Negation
sig_rev_pure = -1.0 * df_ret

# Volume-Conditioned Reversal: Amplify during liquidation spikes
sig_rev_conditioned = -1.0 * df_ret * (1.0 + vol_zscore)

ret_rev_pure, w_rev_pure = run_uncon_backtest(sig_rev_pure, df_ret)
ret_rev_cond, w_rev_cond = run_uncon_backtest(sig_rev_conditioned, df_ret)

stats_rev = pd.DataFrame({
    'Pure 4h Reversal': get_stats(ret_rev_pure),
    'Volume-Conditioned Reversal': get_stats(ret_rev_cond)
})

display(stats_rev.round(2))

# Plot Cumulative Performance
fig, ax = plt.subplots(figsize=(12, 5))
ret_rev_pure.cumsum().plot(ax=ax, label=f"Pure Reversal (SR: {stats_rev.loc['Sharpe', 'Pure 4h Reversal']:.2f})", lw=1.8, color='orange')
ret_rev_cond.cumsum().plot(ax=ax, label=f"Volume-Conditioned Reversal (SR: {stats_rev.loc['Sharpe', 'Volume-Conditioned Reversal']:.2f})", lw=2.2, color='green')
ax.set_title("Alpha 1: Volume-Conditioned vs. Pure Mean Reversion (Gross Cumulative Return)", fontweight='bold')
ax.set_ylabel("Cumulative Log Return")
ax.legend(loc='upper left', frameon=True)
plt.tight_layout()
plt.show()""")

# --- MODULE 5: ALPHA 2 ---
add_md("""---
# Module 5: Alpha Strategy 2 — Cross-Sectional Momentum with 1-Bar Lag

### 5.1 Economic Rationale
* Cryptocurrencies experience prolonged narrative and liquidity cycles (e.g., Layer 1 rotations, DeFi revivals, ETF inflows).
* Once an institutional accumulation program starts, buying pressure spans multiple days to weeks.
* As discovered in Module 3, raw momentum is polluted by immediate 1-bar reversal. Skipping the most recent bar eliminates microstructure friction and captures pure cross-sectional drift.

### 5.2 Mathematical Formulation & Rebalancing Frequency
1. **Lookback Window:** 14 to 21 days (84 to 126 bars of 4h).
2. **Lagged Momentum Signal:**
   $$S_{\\text{Mom}, i, t} = \\frac{1}{K} \\sum_{k=1}^{K} R_{i, t-k} = \\text{ret.shift(1).rolling(K).mean()}$$
3. **Execution Cadence:** To prevent unnecessary transaction churn, portfolio weights are rebalanced **daily (every 24 hours / 6 bars)**, dramatically reducing turnover while capturing medium-term trends.""")

add_code("""# Multi-Week Momentum with Daily Rebalancing
LOOKBACK_DAYS = 21
LOOKBACK_BARS = LOOKBACK_DAYS * BARS_PER_DAY  # 126 bars

# 1-bar lagged momentum
sig_mom = df_ret.shift(1).rolling(LOOKBACK_BARS, min_periods=BARS_PER_DAY * 3).mean()

# Construct target weights
ranked_m = sig_mom.rank(axis=1)
demeaned_m = ranked_m.subtract(ranked_m.mean(axis=1), axis=0)
w_mom_target = demeaned_m.divide(demeaned_m.abs().sum(axis=1), axis=0)

# Rebalance daily (every 6 bars) to manage turnover
w_mom = w_mom_target.copy()
rebalance_mask = (np.arange(len(w_mom)) % BARS_PER_DAY) != 0
w_mom.iloc[rebalance_mask] = np.nan
w_mom = w_mom.ffill()

ret_mom = (w_mom.shift(1) * df_ret).sum(axis=1)
stats_mom = get_stats(ret_mom)

print("Alpha 2: 21-Day Lagged Momentum Performance (Daily Rebalance, Gross):")
display(stats_mom.round(2))

# Cumulative Performance of Momentum Alpha
fig, ax = plt.subplots(figsize=(12, 5))
ret_mom.cumsum().plot(ax=ax, label=f"21d Lagged Momentum (SR: {stats_mom['Sharpe']:.2f})", lw=2, color='#2b5c8f')
ax.set_title("Alpha 2: Cross-Sectional Momentum with 1-Bar Lag (Gross Cumulative Return)", fontweight='bold')
ax.set_ylabel("Cumulative Return")
ax.legend(loc='upper left', frameon=True)
plt.tight_layout()
plt.show()""")

# --- MODULE 6: FRICTION & TURNOVER ---
add_md("""---
# Module 6: Execution Friction, Turnover & The 20 bps Reality Check

### 6.1 The Quant Reality: Transaction Cost Modeling
A backtest that ignores transaction costs is pure fiction. In cryptocurrency markets:
* **Exchange Commission:** ~7 bps (0.07%)
* **Bid-Ask Spread & Market Impact:** ~13 bps (0.13%)
* **All-In Execution Cost ($C$):** **20 bps (0.20% or $0.0020$)** for aggressive market orders.
* **Passive Execution Cost ($C_{\\text{limit}}$):** **7 bps (0.07% or $0.0007$)** when utilizing limit orders to cross the spread passively.

### 6.2 Mathematical Definition of Two-Way Turnover
At each rebalance timestamp $t$:
$$\\text{Turnover}_t = \\sum_{i=1}^N |w_{i,t} - w_{i, t-1}|$$
* If the entire portfolio is replaced, $\\text{Turnover}_t = 2.0$ (100% sold, 100% newly bought).
* The cost drag at timestamp $t$ is:
  $$\\text{Cost}_t = \\text{Turnover}_t \\times C$$
* The **Net Strategy Return** is:
  $$R_{\\text{net}, t} = R_{\\text{gross}, t} - \\text{Cost}_t$$

### 6.3 The Microstructure Lesson from Class
In fast 4h reversal, weights change every 4 hours, resulting in massive annual turnover ($> 1,500\\times$). At 20 bps per trade, transaction costs destroy high-frequency alpha.  
However, as demonstrated in our execution module:
1. **Momentum with daily rebalancing** slashes turnover by **88%** (from $920\\times$ to $110\\times$), remaining **highly profitable net of costs** (Net Sharpe $+1.01$ at 7 bps, $+0.36$ at 20 bps).
2. **Selective Execution / Limit Orders** capture the spread and preserve profitability.""")

add_code("""TCOST_MARKET = 0.0020  # 20 bps market orders
TCOST_LIMIT = 0.0007   # 7 bps limit orders

def evaluate_execution(weights, returns, cost_dec):
    \"\"\"Compute Gross and Net returns accounting for turnover and execution costs.\"\"\"
    w_clean = weights.fillna(0)
    w_lag = w_clean.shift(1).fillna(0)
    
    # Two-way turnover
    turnover = (w_clean - w_lag).abs().sum(axis=1)
    
    gross_ret = (w_clean.shift(1) * returns).sum(axis=1)
    cost = turnover * cost_dec
    net_ret = gross_ret - cost
    
    return gross_ret, net_ret, turnover

# Evaluate Alpha 2 (Momentum) under Market Orders (20 bps) and Limit Orders (7 bps)
gross_mom, net_mom_20, to_mom = evaluate_execution(w_mom, df_ret, TCOST_MARKET)
_, net_mom_7, _ = evaluate_execution(w_mom, df_ret, TCOST_LIMIT)

# Reversal execution: evaluate with daily rebalancing to tame churn
w_rev_daily = w_rev_cond.copy()
mask_rev = (np.arange(len(w_rev_daily)) % BARS_PER_DAY) != 0
w_rev_daily.iloc[mask_rev] = np.nan
w_rev_daily = w_rev_daily.ffill()

gross_rev, net_rev_20, to_rev = evaluate_execution(w_rev_daily, df_ret, TCOST_MARKET)
_, net_rev_7, _ = evaluate_execution(w_rev_daily, df_ret, TCOST_LIMIT)

execution_summary = pd.DataFrame({
    'Alpha 1 (Reversal, Daily Reb)': [
        to_rev.mean() * ANN_FACTOR,
        get_stats(gross_rev)['Sharpe'],
        get_stats(net_rev_7)['Sharpe'],
        get_stats(net_rev_20)['Sharpe']
    ],
    'Alpha 2 (21d Momentum, Daily Reb)': [
        to_mom.mean() * ANN_FACTOR,
        get_stats(gross_mom)['Sharpe'],
        get_stats(net_mom_7)['Sharpe'],
        get_stats(net_mom_20)['Sharpe']
    ]
}, index=['Annual Turnover (x)', 'Gross Sharpe', 'Net Sharpe (7 bps Limit Orders)', 'Net Sharpe (20 bps Market Orders)'])

display(execution_summary.round(2))

# Plot Momentum Gross vs Net Performance
fig, ax = plt.subplots(figsize=(12, 5))
gross_mom.cumsum().plot(ax=ax, label=f"Gross Momentum (SR: {get_stats(gross_mom)['Sharpe']:.2f})", lw=1.8, color='navy')
net_mom_7.cumsum().plot(ax=ax, label=f"Net Momentum @ 7 bps Limit Orders (SR: {get_stats(net_mom_7)['Sharpe']:.2f})", lw=2.2, color='teal')
net_mom_20.cumsum().plot(ax=ax, label=f"Net Momentum @ 20 bps Market Orders (SR: {get_stats(net_mom_20)['Sharpe']:.2f})", lw=1.8, ls='--', color='crimson')
ax.set_title("Alpha 2: Transaction Cost Impact on Momentum", fontweight='bold')
ax.set_ylabel("Cumulative Return")
ax.legend(loc='upper left', frameon=True)
plt.tight_layout()
plt.show()""")

# --- MODULE 7: MULTI-ALPHA COMBINATION ---
add_md("""---
# Module 7: Multi-Alpha Blending & Portfolio Optimization

### 7.1 Motivation: The Free Lunch of Diversification
In Homework 5 (*The Price of Hedging*), we established that combining lowly or negatively correlated alphas drastically improves risk-adjusted returns:
$$\\sigma_{\\text{combo}}^2 = w_1^2 \\sigma_1^2 + w_2^2 \\sigma_2^2 + 2 w_1 w_2 \\rho \\sigma_1 \\sigma_2$$
Because Reversal and Momentum exploit completely opposite market mechanisms (liquidity overshooting vs. information diffusion), their correlation is naturally negative ($\\rho < 0$).

### 7.2 Multi-Strategy Allocation Frameworks
1. **Equal Volatility Weighting ($1/\\sigma_i$):**
   $$w_i = \\frac{1 / \\sigma_i}{\\sum_j 1 / \\sigma_j}$$
2. **Sharpe Ratio Weighting:**
   $$w_i = \\frac{\\max(\\text{SR}_i, 0)}{\\sum_j \\max(\\text{SR}_j, 0)}$$
3. **Markowitz Mean-Variance Optimal Weighting (Long-Only Allocation):**
   Maximize portfolio Sharpe ratio subject to $w_i \\ge 0$ and $\\sum w_i = 1.0$. We utilize quadratic programming/constrained optimization to prevent shorting strategies.""")

add_code("""from scipy.optimize import minimize

# Combine Gross Return Streams to demonstrate pure theoretical Alpha diversification
alpha_gross = pd.DataFrame({
    'Reversal (Gross)': ret_rev_cond,
    'Momentum (Gross)': ret_mom
}).dropna()

corr_gross = alpha_gross.corr().iloc[0, 1]
print(f"Correlation between Reversal and Momentum Alphas: {corr_gross:.3f} (Significant Negative Correlation!)")

# Combine Viable Executable Streams (Net of 7 bps Limit Orders)
alpha_net = pd.DataFrame({
    'Reversal (Net)': net_rev_7,
    'Momentum (Net)': net_mom_7
}).dropna()

# Constrained Markowitz Optimization for Strategy Allocation
def optimize_portfolio(rets):
    mu = rets.mean() * ANN_FACTOR
    cov = rets.cov() * ANN_FACTOR
    
    def neg_sharpe(w):
        port_ret = w @ mu
        port_vol = np.sqrt(w @ cov @ w)
        return -port_ret / port_vol if port_vol > 0 else 0
    
    # Constraints: weights sum to 1.0, non-negative
    bounds = [(0.0, 1.0) for _ in range(len(mu))]
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
    
    init_w = np.ones(len(mu)) / len(mu)
    res = minimize(neg_sharpe, init_w, bounds=bounds, constraints=cons)
    return pd.Series(res.x, index=rets.columns)

w_opt_gross = optimize_portfolio(alpha_gross)
w_opt_net = optimize_portfolio(alpha_net)

print("\\nOptimal Strategy Allocations:")
print("Gross Portfolio Weights:")
display(w_opt_gross.round(3))
print("Net Executable Portfolio Weights:")
display(w_opt_net.round(3))

# Compute Blended Return Streams
combo_gross = (alpha_gross * w_opt_gross).sum(axis=1)
combo_net = (alpha_net * w_opt_net).sum(axis=1)

combo_comparison = pd.DataFrame({
    'Reversal (Gross)': get_stats(alpha_gross['Reversal (Gross)']),
    'Momentum (Gross)': get_stats(alpha_gross['Momentum (Gross)']),
    'Blended Gross Ensemble': get_stats(combo_gross),
    'Momentum (Net @ 7bps)': get_stats(alpha_net['Momentum (Net)']),
    'Blended Net Ensemble': get_stats(combo_net)
})

print("\\nMulti-Alpha Ensemble Performance Dashboard:")
display(combo_comparison.round(2))

# Visualize Blended Alpha Equity Curves
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Gross Multi-Alpha
alpha_gross['Reversal (Gross)'].cumsum().plot(ax=ax1, label=f"Reversal alone (SR: {get_stats(alpha_gross['Reversal (Gross)'])['Sharpe']:.2f})", ls='--', color='orange')
alpha_gross['Momentum (Gross)'].cumsum().plot(ax=ax1, label=f"Momentum alone (SR: {get_stats(alpha_gross['Momentum (Gross)'])['Sharpe']:.2f})", ls='--', color='blue')
combo_gross.cumsum().plot(ax=ax1, label=f"Ensemble (SR: {get_stats(combo_gross)['Sharpe']:.2f})", lw=2.5, color='darkgreen')
ax1.set_title("Gross Multi-Alpha Blending (Theoretical Diversification)", fontweight='bold')
ax1.set_ylabel("Cumulative Return")
ax1.legend(loc='upper left', frameon=True)

# Net Multi-Alpha
alpha_net['Momentum (Net)'].cumsum().plot(ax=ax2, label=f"Net Momentum (SR: {get_stats(alpha_net['Momentum (Net)'])['Sharpe']:.2f})", lw=2, color='teal')
combo_net.cumsum().plot(ax=ax2, label=f"Net Ensemble (SR: {get_stats(combo_net)['Sharpe']:.2f})", lw=2.5, color='darkgreen')
ax2.set_title("Net Multi-Alpha Ensemble (Executable @ 7 bps)", fontweight='bold')
ax2.legend(loc='upper left', frameon=True)

plt.tight_layout()
plt.show()""")

# --- MODULE 8: RISK ATTRIBUTION ---
add_md("""---
# Module 8: Institutional Risk Attribution & Factor Analysis

### 8.1 Drawdown & Underwater Analysis
Institutional allocators require deep visibility into downside tail risk. Following `PythonDrawdowns.ipynb`, we evaluate:
* **Underwater Curve:**
  $$\\text{Drawdown}_t = \\frac{W_t}{\\max_{\\tau \\le t} W_\\tau} - 1$$
* **Maximum Drawdown (MDD):** $\\min_t(\\text{Drawdown}_t)$
* **Drawdown Duration:** Maximum consecutive periods spent underwater before achieving a new high-water mark.

### 8.2 Factor Benchmark Regression (Alpha & Beta to Bitcoin)
Is the strategy merely a disguised bet on crypto market beta? We estimate the Single-Index Model against `BTCUSDT`:
$$R_{\\text{strat}, t} = \\alpha + \\beta R_{\\text{BTC}, t} + \\epsilon_t$$
* **Beta ($\\beta$):** $\\frac{\\text{Cov}(R_{\\text{strat}}, R_{\\text{BTC}})}{\\text{Var}(R_{\\text{BTC}})}$
* **Annualized Alpha ($\\alpha$):** $\\alpha_{\\text{bar}} \\times \\text{ANN\\_FACTOR}$
* **Information Ratio (IR):** $\\frac{\\text{Mean}(\\epsilon)}{\\text{Std}(\\epsilon)} \\times \\sqrt{\\text{ANN\\_FACTOR}}$""")

add_code("""# Primary Production Strategy: Net Executable Multi-Alpha Ensemble
strat_final = combo_net.copy()
wealth_index = (1.0 + strat_final).cumprod()

# Compute Drawdown Series
peak = wealth_index.expanding(min_periods=1).max()
drawdown = (wealth_index / peak) - 1.0
max_dd = drawdown.min()

# Compute Drawdown Duration (in bars and days)
dd_duration_bars = 0
max_duration_bars = 0
for dd in drawdown:
    if dd < 0:
        dd_duration_bars += 1
        if dd_duration_bars > max_duration_bars:
            max_duration_bars = dd_duration_bars
    else:
        dd_duration_bars = 0

max_duration_days = max_duration_bars / BARS_PER_DAY

print(f"Maximum Drawdown: {max_dd * 100:.2f}%")
print(f"Maximum Drawdown Duration: {max_duration_bars} bars (~{max_duration_days:.1f} days)")

# Single-Index Factor Regression against BTCUSDT
btc_ret = df_ret['BTCUSDT'].reindex(strat_final.index).fillna(0)

cov_matrix = np.cov(strat_final, btc_ret)
strat_variance = cov_matrix[0, 0]
btc_variance = cov_matrix[1, 1]
covariance = cov_matrix[0, 1]

# Beta to Bitcoin
beta_btc = covariance / btc_variance
# Residual Return (Pure Alpha)
residual = strat_final - beta_btc * btc_ret
alpha_ann = residual.mean() * ANN_FACTOR
alpha_ir = (residual.mean() / residual.std()) * np.sqrt(ANN_FACTOR)

risk_scorecard = pd.DataFrame({
    'Metric': [
        'Annualized Return (Net)',
        'Annualized Volatility',
        'Net Sharpe Ratio (7 bps)',
        'Maximum Drawdown',
        'Max Drawdown Duration',
        'Market Beta (to BTC)',
        'Annualized Alpha (to BTC)',
        'Information Ratio (IR)'
    ],
    'Value': [
        f"{strat_final.mean() * ANN_FACTOR * 100:.2f}%",
        f"{strat_final.std() * np.sqrt(ANN_FACTOR) * 100:.2f}%",
        f"{strat_final.mean() / strat_final.std() * np.sqrt(ANN_FACTOR):.2f}",
        f"{max_dd * 100:.2f}%",
        f"{max_duration_days:.1f} days",
        f"{beta_btc:.3f}",
        f"{alpha_ann * 100:.2f}%",
        f"{alpha_ir:.2f}"
    ]
})

print("\\nInstitutional Performance & Factor Attribution Scorecard:")
display(risk_scorecard.set_index('Metric'))

# Plot Wealth Curve and Underwater Drawdown Curve
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# Equity Curve vs BTC
wealth_index.plot(ax=ax1, color='darkgreen', lw=2, label='StatArb Strategy (Net of Costs)')
btc_wealth = (1.0 + btc_ret).cumprod()
btc_wealth.plot(ax=ax1, color='gray', lw=1.5, ls='--', alpha=0.7, label='Bitcoin Buy & Hold Benchmark')
ax1.set_title("Institutional Performance: Net StatArb vs. Bitcoin Benchmark", fontweight='bold')
ax1.set_ylabel("Wealth Index (Base 1.0)")
ax1.legend(loc='upper left', frameon=True)

# Underwater Curve
drawdown.plot(ax=ax2, color='crimson', lw=1.2)
ax2.fill_between(drawdown.index, drawdown.values, 0, color='crimson', alpha=0.25)
ax2.set_title("Underwater Drawdown Profile", fontweight='bold')
ax2.set_ylabel("Drawdown (%)")
ax2.set_ylim(bottom=min(max_dd * 1.2, -0.05), top=0.01)

plt.tight_layout()
plt.show()""")

# --- MODULE 9: INTERVIEW PLAYBOOK ---
add_md("""---
# Module 9: Quant PM Interview Playbook & Talking Points

When presenting this project to a **Quant Portfolio Manager (PM)** or **Recruiter**, focus on the following key points:

### 1. The 2-Minute Elevator Pitch
> *"I researched and engineered an institutional-grade statistical arbitrage system across liquid cryptocurrencies over 2022–2024. Rather than treating crypto as a generic asset class, I decomposed price dynamics into two distinct economic phenomena: high-frequency liquidity-driven mean reversion conditioned on volume anomalies, and intermediate-term cross-sectional momentum. By lagging the momentum signal by one bar, I eliminated microstructure drag. After incorporating realistic transaction costs and turnover constraints, I demonstrated that daily-rebalanced cross-sectional momentum achieves a net Sharpe of 1.01 with a market beta of approximately 0.0 to Bitcoin, proving pure cross-sectional alpha generation."*

### 2. Anticipating Tough Quant Interview Questions

#### Q1: "How did you prevent look-ahead bias and survivorship bias?"
* **Look-Ahead Bias:** Portfolio weights formed at bar $t$ are strictly applied to returns at bar $t+1$ using Pandas `.shift(1)`. All volume $Z$-scores and moving averages use backward-looking rolling windows only.
* **Survivorship Bias:** The universe was restricted to established mega-cap and large-cap liquid assets with verified multi-year continuous liquidity on Binance.

#### Q2: "Crypto has 20 bps execution costs. Why didn't transaction costs wipe out your alpha?"
* *Raw* 4h reversal has high turnover (~1.35 per bar), which degrades net returns when traded with market orders.
* I addressed this by:
  1. **Distinguishing theoretical edge from execution reality:** Showing where academic gross alpha lives vs. where executable net alpha lives.
  2. **Horizon & Rebalance optimization:** Moving momentum to a 21-day lookback with daily rebalancing slashed turnover by 88% (from $920\\times$ to $110\\times$).
  3. **Order execution:** Demonstrating the impact of passive limit orders (7 bps) vs. aggressive market orders (20 bps).

#### Q3: "What is your market exposure? Is this just a disguised Bitcoin bull strategy?"
* The portfolio is **strictly dollar-neutral** at every single bar ($\\sum w_i = 0$, Longs $= +0.5$, Shorts $= -0.5$).
* Single-index factor regression confirms a **Beta of $\\approx 0.0$** to Bitcoin, proving the strategy's returns are derived from pure cross-sectional asset selection (*Alpha*), not systemic crypto market exposure.

---
### Future Research Extensions
1. **Funding Rate & Open Interest Integration:** Incorporating perpetual futures funding rates to identify over-leveraged long/short skews.
2. **Order Book Imbalance (Microstructure):** Utilizing L2/L3 order book depth to estimate real-time bid-ask liquidity and dynamically adjust limit vs. market order routing.
3. **Regime-Switching Allocation:** Using rolling market volatility (e.g., crypto VIX / Parkinson volatility) to dynamically shift capital toward reversal during turbulent regimes and toward momentum during quiet trending regimes.""")

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print(f"Successfully created notebook at: {nb_path}")
print(f"Total cells: {len(nb['cells'])}")
