# Statistical Arbitrage in Cryptocurrencies

**Live interactive showcase:** https://am610.github.io/crypto-statarb-showcase/
**Terrain v2 (zoomable map):** https://am610.github.io/crypto-statarb-showcase/terrain/

An end-to-end quantitative research project: building, testing, and honestly
evaluating a statistical arbitrage system across liquid cryptocurrencies
(2022–2024). From raw 4-hour bar data to a dollar-neutral, multi-alpha
strategy that survives transaction costs.

## Key results

- **Net Sharpe 1.02** after realistic transaction costs (7 bps limit orders)
- **Beta 0.00 to Bitcoin** — returns are pure idiosyncratic alpha, not a
  BTC bull-run ride
- **Max drawdown −25.6%**, annualized net return 22.6%
- Universe: 10 liquid cryptos, 4-hour bars, 2022–2024 (6,569 observations)

## Research arc

1. **Empirical horizon scan** — mapped where short-term reversal (4–8h,
   Sharpe −3.58 as "momentum") hands over to medium-term momentum
   (21 days). Skipping one 4-hour bar removes microstructure bounce noise
   and unlocks a 12-hour momentum Sharpe of 1.79.
2. **Alpha 1: volume-conditioned mean reversion** — fading panic sell-offs
   on abnormal volume (forced liquidations). Gross Sharpe 3.58.
3. **Alpha 2: 21-day lagged cross-sectional momentum** — daily-rebalanced,
   gross Sharpe 1.36.
4. **Execution friction** — the honest chapter: Alpha 1's 476×/yr turnover
   turns Sharpe 3.58 into **−1.32 net**; Alpha 2 survives at **1.02 net**.
5. **Multi-alpha blending** — reversal/momentum correlation of −0.103
   gives a gross-optimal blend Sharpe of 3.85; the net-executable optimum
   is 100% momentum.
6. **Risk attribution** — drawdown profile, beta/alpha vs. Bitcoin,
   information ratio 1.01.

## Methodology

Dollar-neutral construction (demeaned cross-sectional ranks every bar),
gross leverage 1.0 (50% long / 50% short), no look-ahead bias (decisions at
bar *t* earn bar *t+1*), 7 bps / 20 bps cost models.

Built from the research notebook
`02_Crypto_StatArb_Research_Lab_Simplified.ipynb`.

*Educational research project. Historical backtest, 2022–2024. Not
investment advice. Past performance does not predict future results.*
