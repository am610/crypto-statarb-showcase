# Statistical Arbitrage in Cryptocurrencies: A Quantitative Research Lab
### Institutional Research Project

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Strategy](https://img.shields.io/badge/Strategy-Statistical%20Arbitrage-brightgreen.svg)
![Asset%20Class](https://img.shields.io/badge/Asset%20Class-Crypto%20USDT%20Pairs-orange.svg)
![Market%20Neutral](https://img.shields.io/badge/Beta%20to%20BTC-0.00-purple.svg)

---

## Research Pipeline Architecture

<p align="center">
  <img src="project_flowchart.png" alt="Statistical Arbitrage Research Pipeline" width="100%" />
</p>

## Executive Summary

This project implements an institutional-grade **Statistical Arbitrage (StatArb)** research and backtesting framework across liquid cryptocurrency markets over the **2022–2024** period.

Rather than applying naive price indicators, this study decomposes digital asset price discovery into two distinct, economically grounded phenomena:
1. **Short-Term Volume-Conditioned Mean Reversion (Reversal):** Exploiting forced margin liquidations and retail order-flow shocks over 4-hour horizons.
2. **Intermediate-Term Cross-Sectional Momentum with 1-Bar Lag:** Exploiting persistent institutional flow and narrative drift over 21-day horizons, while skipping the immediate 4-hour bar to strip away microstructural bounce noise.

### Key Empirical Findings
* **The Horizon Scan Transition:** Reversal is strongly dominant at horizons $\le 8$ hours (Gross Sharpe $+3.58$). Beyond 12 hours, momentum emerges and peaks when the immediate 1-bar noise is skipped (Sharpe $+1.80$).
* **Friction Reality:** In high-frequency 4-hour reversal, annual turnover ($> 1,500\times$) destroys returns if executed with 20 bps market orders. In contrast, **21-day cross-sectional momentum rebalanced daily** slashes annual turnover to $110\times$, achieving a **Net Sharpe of 1.02** and **+22.58% net annual return** under realistic 7 bps limit-order execution.
* **The Free Lunch of Diversification:** Gross reversal and momentum alphas exhibit a **negative correlation ($\rho = -0.103$)**, allowing a Markowitz-optimal combination to expand the gross Sharpe ratio to **3.85** while suppressing volatility from 22% to 16%.
* **Zero Market Beta:** Factor regression against Bitcoin (`BTCUSDT`) confirms a **Beta of 0.00**, demonstrating that performance is 100% idiosyncratic cross-sectional selection alpha rather than disguised systemic market exposure.

---

## Project Structure

```
Crypto_StatArb_Project/
├── app.py                                    # Live Web Portfolio Scanner & Alpha Engine (Flask + Tailwind + Chart.js)
├── portfolio_scanner.py                      # Interactive CLI Portfolio Factor Diagnostic & Alpha Attributor
├── 01_Crypto_StatArb_Research_Lab.ipynb      # Primary institutional research lab with full backtests & outputs
├── 02_Crypto_StatArb_Research_Lab_Simplified.ipynb # Step-by-step educational research lab with explicit code
├── 03_Hands_On_Minimal_Toy_Tutorial.ipynb    # Minimal 5-step practice sandbox with round numbers
├── QUANT_PIPELINE_TUTORIAL.html              # Interactive visual guide to the 5-step quant trading pipeline
├── QUANT_DICTIONARY.html                     # Searchable quant finance dictionary with live search
├── project_flowchart.png                     # 300-DPI architecture flowchart
├── requirements.txt                          # Python dependencies for local use and cloud hosting
├── README.md                                 # Institutional executive summary & documentation
└── data/                                     # Historical 4-hour bar data from Binance (2022–2024)
    ├── crypto_prices_4h.csv
    ├── crypto_volumes_4h.csv
    └── crypto_quote_volumes_4h.csv
```

### Quickstart: Run the Live Web Scanner
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the interactive web dashboard
python3 app.py
# Open: http://localhost:5000

# 3. Or run the terminal CLI scanner on your holdings
python3 portfolio_scanner.py --holdings "BTC:10, ETH:5, SOL:25, SUI:20"
```

---

## Research Methodology & Mathematical Formulations

### 1. The Cross-Sectional (XS) Portfolio Engine
At each rebalance timestamp $t$ across $N=10$ liquid assets:
1. Compute alpha signal $S_{i,t}$.
2. Cross-sectionally rank: $r_{i,t} = \text{rank}(S_{i,t})$.
3. Demean to ensure dollar neutrality ($\sum_i \tilde{w}_{i,t} = 0$):
   $\tilde{w}_{i,t} = r_{i,t} - \frac{1}{N} \sum_{j=1}^N r_{j,t}$
4. Normalize to enforce unit gross leverage ($\sum_i |w_{i,t}| = 1.0$):
   $w_{i,t} = \frac{\tilde{w}_{i,t}}{\sum_{j=1}^N |\tilde{w}_{j,t}|}$
5. Portfolio returns at $t+1$ (strictly avoiding lookahead bias):
   $R_{\text{strat}, t+1} = \sum_{i=1}^N w_{i,t} R_{i, t+1} = \sum_{i=1}^N w_{i, t-1}^{\text{shifted}} R_{i, t}$

### 2. Alpha Signals
* **Volume-Conditioned Reversal (Alpha 1):**
  $S_{\text{Rev}, i, t} = -R_{i,t} \times (1.0 + \max(Z_{V, i, t}, 0))$
  where $Z_{V, i, t}$ is the 36-bar rolling $Z$-score of quote volume.
* **Lagged Momentum (Alpha 2):**
  $S_{\text{Mom}, i, t} = \frac{1}{K} \sum_{k=1}^K R_{i, t-k} = \text{ret.shift(1).rolling(K).mean()}$
  with $K = 126$ bars (21 days) and 24-hour rebalancing.

### 3. Execution & Transaction Cost Modeling
Two-way turnover at each bar:
$\text{Turnover}_t = \sum_{i=1}^N |w_{i,t} - w_{i, t-1}|$
Net return accounting for transaction cost $C$:
$R_{\text{net}, t} = R_{\text{gross}, t} - (\text{Turnover}_t \times C)$
* Aggressive Market Orders: $C = 20\text{ bps}$ ($0.0020$)
* Passive Limit Orders: $C = 7\text{ bps}$ ($0.0007$)

---

## Institutional Performance Scorecard

| Metric | Cross-Sectional Momentum (Net @ 7 bps) | Theoretical Multi-Alpha Ensemble (Gross) | Bitcoin Benchmark (Buy & Hold) |
| :--- | :---: | :---: | :---: |
| **Annualized Return** | **+22.58%** | **+61.42%** | +36.21% |
| **Annualized Volatility** | **22.22%** | **15.95%** | 52.14% |
| **Sharpe Ratio** | **1.02** | **3.85** | 0.70 |
| **Maximum Drawdown** | **-25.55%** | **-7.14%** | -76.84% |
| **Beta to Bitcoin** | **0.00** | **-0.01** | 1.00 |
| **Annualized Alpha** | **+22.58%** | **+61.50%** | 0.00% |
| **Information Ratio** | **1.02** | **3.86** | N/A |

---

## Quant Portfolio Manager (PM) Interview Playbook

When presenting this project in hedge fund interviews:
1. **The Edge:** In crypto, retail liquidations create high-frequency overshooting (reversal), while institutional accumulation creates medium-term trends (momentum).
2. **The Microstructure Innovation:** Raw momentum is corrupted by immediate reversal noise. Lagging momentum by 1 bar (`shift(2)`) eliminates this friction and dramatically improves signal quality.
3. **Execution Reality:** Unmanaged 4h reversal has turnover $> 1,500\times$, rendering market orders unprofitable. The solution is horizon extension (daily rebalancing), limit order execution (7 bps), and multi-alpha diversification.
4. **Pure Idiosyncratic Alpha:** With market beta verified at $0.00$, this strategy functions as a true market-neutral decorrelated return stream.
