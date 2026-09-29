# The Quant & Trading Dictionary (Living Knowledge Base)
> A growing reference guide for quantitative finance, market microstructure, and algorithmic trading concepts. Designed for quick lookup, deep intuition, and interview preparation.

---

## Table of Contents
1. [Quantitative Hedge Fund](#1-quantitative-hedge-fund)
2. [Equities](#2-equities)
3. [High-Leverage Perpetual Contracts](#3-high-leverage-perpetual-contracts)
4. [Liquidity](#4-liquidity)
5. [Statistical Arbitrage (StatArb)](#5-statistical-arbitrage-statarb)
6. [Cascading Margin Liquidations (The "Fire Sale")](#6-cascading-margin-liquidations-the-fire-sale)
7. [Institutional Capital Reallocation](#7-institutional-capital-reallocation)
8. [Fundamentals](#8-fundamentals)
9. [Dollar-Neutral](#9-dollar-neutral)
10. [Cross-Sectional (XS)](#10-cross-sectional-xs)
11. [Rebalance](#11-rebalance)
12. [Asset](#12-asset)
13. [Gross Leverage](#13-gross-leverage)
14. [Market Exposure (Beta)](#14-market-exposure-beta)
15. [Order Flow Imbalance](#15-order-flow-imbalance)
16. [Market Maker Inventory Risk](#16-market-maker-inventory-risk)
17. [Forced Liquidations](#17-forced-liquidations)
18. [Fama-French / Carhart UMD (Up Minus Down)](#18-fama-french--carhart-umd-up-minus-down)

---

### 1. Quantitative Hedge Fund
* **Plain English:** An investment firm that manages money using mathematical models, statistical algorithms, and automated computer code rather than human emotion, intuition, or gut feelings.
* **How It Operates:**
  * **Discretionary Trader:** Reads news, speaks to company executives, looks at charts, and says: *"I think Bitcoin will go up because the Federal Reserve cut interest rates."*
  * **Quantitative Trader (Quant):** Analyzes historical price and volume data using Python, detects a statistically significant edge (e.g., *"When coin A drops 3 standard deviations on high volume, it mean-reverts 72% of the time over the next 4 hours"*), and builds algorithms to systematically trade that edge.
* **Famous Quant Funds:** Renaissance Technologies (Medallion Fund), Citadel, Two Sigma, Millennium, DE Shaw, Point72 (Cubist), WorldQuant.

---

### 2. Equities
* **Plain English:** Shares of ownership in a public corporation (commonly known as "stocks").
* **How It Works:** When you buy 1 share of Apple (`AAPL`) or Microsoft (`MSFT`), you legally own a fractional slice of that company's future earnings, cash flows, assets, and voting rights.
* **Contrast with Crypto:** Crypto tokens are **not** equity shares; they do not represent legal corporate ownership. They are decentralized network tokens, digital commodities, or governance rights. Furthermore, equities trade ~6.5 hours a day on weekdays with pre/post-market closes, whereas crypto trades **24/7/365 without pause**.

---

### 3. High-Leverage Perpetual Contracts ("Perps")
* **Plain English:** The dominant derivative contract in crypto. It allows traders to speculate on whether a crypto asset will go up or down using borrowed money—**without ever owning the underlying token** and **without an expiration date** (unlike traditional futures that expire monthly).
* **How Leverage Works:**
  * **1x (No Leverage):** You put down \$1,000 to buy \$1,000 of Bitcoin. If BTC drops 10%, your portfolio is worth \$900.
  * **20x Leverage:** You put down \$1,000 as collateral (margin) to control **\$20,000** of Bitcoin.
  * **The Fatal Trap:** If Bitcoin drops just **5%**, your \$20,000 position loses \$1,000. Your entire collateral is wiped out! The exchange immediately seizes your position and liquidates it.

---

### 4. Liquidity
* **Plain English:** How easily, quickly, and cheaply you can buy or sell an asset **without significantly changing its market price**.
* **Analogy:** Exchanging a \$100 bill for five \$20 bills is 100% liquid (instant, zero cost). Selling an antique painting or a house is highly *illiquid* (it takes months, negotiation, and high fees to find a buyer).
* **In Trading:**
  * **High Liquidity:** `BTCUSDT` has hundreds of millions of dollars in the order book. Buying \$100,000 of BTC moves the market by less than 0.01%.
  * **Low Liquidity (Illiquid):** A tiny altcoin with only \$10,000 in the order book. Trying to buy \$10,000 will blast the market price up 25% against yourself (**slippage**).
* **In Our Project:** We deliberately selected the **top 10 liquid coins** (`BTC`, `ETH`, `SOL`, etc.) to ensure our simulated trades could realistically execute without catastrophic slippage.

---

### 5. Statistical Arbitrage (StatArb)
* **Plain English:** A quantitative trading strategy that identifies temporary relative price mispricings between correlated assets and bets on their statistical tendency to return to equilibrium.
* **Pure Arbitrage vs. Statistical Arbitrage:**
  * **Pure Arbitrage (Risk-Free):** Buying Bitcoin on Coinbase for \$60,000 and selling it on Binance for \$60,050 at the exact same second. Guaranteed \$50 profit with zero market risk.
  * **Statistical Arbitrage (Probabilistic):** You buy an asset that has temporarily crashed too far and short an asset that has surged too high. You are not guaranteed to win every single trade, but across hundreds of trades, the law of large numbers provides a reliable mathematical edge.

---

### 6. Cascading Margin Liquidations (The "Fire Sale")
* **Plain English:** A violent domino effect where leveraged traders getting liquidated trigger further price drops, which in turn liquidates even more traders.
* **How the Waterfall Happens:**
  1. Bitcoin drops 3% unexpectedly.
  2. Highly leveraged traders (e.g., 50x and 20x) breach their margin limits.
  3. The exchange's automated risk engine seizes their accounts and sends **aggressive market sell orders** into the order book to close the positions.
  4. These massive sell orders exhaust available buy orders, pushing the price down another 4%.
  5. This second crash now liquidates the 10x traders, triggering another wave of emergency selling.
* **Why This Creates Alpha:** These liquidation sell orders are **uninformed**—the exchange is not selling because it thinks Bitcoin is bad; it is forced by code to sell at any price! Once the liquidation waterfall finishes, the artificial selling pressure abruptly stops, and the price **mean-reverts violently back up**.
* **In Our Project:** This is the exact economic foundation of **Alpha 1 (Volume-Conditioned Reversal)**!

---

### 7. Institutional Capital Reallocation
* **Plain English:** Large institutional market participants (hedge funds, ETF issuers, venture capital treasuries, family offices) moving millions or billions of dollars from one asset into another.
* **How It Causes Momentum:** Unlike a retail trader who buys \$500 in one click, an institution allocating \$300,000,000 into Solana cannot buy it all at once without causing massive slippage. They use execution algorithms (like TWAP/VWAP) to buy small clips every hour for several days or weeks.
* **The Result:** This steady, persistent buying pressure produces **positive autocorrelation (trend / momentum)** over 1-day to 3-week horizons.
* **In Our Project:** This is the economic foundation of **Alpha 2 (Cross-Sectional Momentum)**!

---

### 8. Fundamentals
* **Plain English:** The real-world operational, economic, and financial drivers of an asset's intrinsic value.
* **In Equities:** Corporate quarterly earnings, revenue growth, profit margins, balance sheet debt, cash flows, and P/E ratio.
* **In Crypto:** Active on-chain addresses, Total Value Locked (TVL), protocol revenue from transaction fees, staking yield, developer commits, and active users.
* **Quant vs. Fundamental:** Fundamental investors ask: *"Is Solana undervalued relative to its fee revenue?"* Quants ask: *"What are the statistical probability distributions of Solana's 21-day cross-sectional returns relative to other coins?"*

---

### 9. Dollar-Neutral
* **Plain English:** A portfolio designed so that the total dollar value of your **Long** positions (bets on prices going up) exactly equals the total dollar value of your **Short** positions (bets on prices going down).
* **The Formula:**
  $$\text{Net Exposure} = \sum_{i=1}^N w_i = \text{Long Weights} - \text{Short Weights} = 0.0$$
* **Why Hedge Funds Love It:** If the entire crypto market crashes 30% overnight:
  * Your Longs lose 30%.
  * Your Shorts gain 30%.
  * **Net market P&L = 0%!** You are immune to broad market crashes. You only make money on the *relative spread* (whether your Longs outperform your Shorts).
* **In Our Code:** We "demean" cross-sectional ranks to force the weights to sum to zero:
  ```python
  demeaned = ranked.subtract(ranked.mean(axis=1), axis=0)
  ```

---

### 10. Cross-Sectional (XS)
* **Plain English:** Comparing a group of assets **against each other at the exact same snapshot in time**, rather than tracking a single asset over historical time.
* **Time-Series vs. Cross-Sectional:**
  * **Time-Series (TS):** Looking at *Bitcoin alone* over the last 30 days. Is Bitcoin above its 30-day moving average?
  * **Cross-Sectional (XS):** Looking at *all 10 coins at 4:00 PM today*. Which coin performed the best? Which coin performed the worst?
* **In Our Code:**
  ```python
  # Ranking across all coins at timestamp t (axis=1)
  ranked = signal.rank(axis=1)
  ```
  We buy the top-ranked coins (relative winners) and short the bottom-ranked coins (relative losers).

---

### 11. Rebalance
* **Plain English:** Periodically adjusting your portfolio's actual positions back to your mathematical model's target weights.
* **Why We Do It:** As prices fluctuate, winning positions grow too large and losing positions shrink. Rebalancing sells portions of winners and buys more of targets to maintain your exact risk limits and dollar neutrality.
* **The Cost-Turnover Dilemma:** Rebalancing requires executing trades. Every trade incurs transaction costs (commissions + slippage).
  * Rebalancing every 4 hours generates excessive turnover ($> 1,500\times$/year), which destroys profits.
  * Rebalancing **daily (every 24 hours)** cuts turnover by over 85%, allowing momentum to remain profitable net of fees!

---

### 12. Asset
* **Plain English:** Any resource of economic value that can be purchased, held, and sold for cash.
* **Examples:** A stock (`AAPL`), a fiat currency (`USD`), a commodity (Gold), or a cryptocurrency (`BTC`).
* **In Our Code:** Each column in our price DataFrame (`df_px`) is an individual asset.

---

### 13. Gross Leverage
* **Plain English:** The total size of all active positions in your portfolio (both longs and shorts added together as positive numbers), expressed as a multiple of your account equity.
* **The Formula:**
  $$\text{Gross Leverage} = \sum_{i=1}^N |w_i|$$
* **Example:**
  * You have \$1,000,000 in trading capital.
  * You buy \$500,000 worth of `ETH` (Long, $+0.5$).
  * You short \$500,000 worth of `SOL` (Short, $-0.5$).
  * **Net Exposure:** $+0.5 + (-0.5) = 0.0$ (Dollar-Neutral).
  * **Gross Leverage:** $|+0.5| + |-0.5| = 1.0$ (1x Leverage: \$1,000,000 total invested capital).
* **In Our Code:** We normalize demeaned ranks by dividing by the sum of absolute values:
  ```python
  weights = demeaned.divide(demeaned.abs().sum(axis=1), axis=0)
  ```

---

### 14. Market Exposure (Beta)
* **Plain English:** The degree to which your portfolio's returns depend on the overall direction of the general market benchmark.
* **Analogy:** "A rising tide lifts all boats, and an outgoing tide strands them." If you simply buy and hold Bitcoin, you have **100% market exposure** ($\beta = 1.0$)—if crypto crashes 60%, you crash 60%.
* **Beta ($\beta$):** A regression coefficient measuring sensitivity to the benchmark:
  * $\beta = 1.0$: You move in lockstep with the crypto market.
  * $\beta = 0.0$: You have **zero market exposure**. Whether Bitcoin goes to \$1,000,000 or drops to zero, your portfolio is mathematically insulated.
* **In Our Project:** Single-index factor regression confirms our strategy has a **Beta of 0.00 to Bitcoin**, proving our returns are pure **Alpha** (manager skill / market-neutral edge).

---

---

### 15. Order Flow Imbalance (OFI)
* **Plain English:** A situation where the volume of aggressive market BUY orders significantly exceeds aggressive market SELL orders (or vice versa) within a specific time window.
* **How It Works in the Order Book:**
  * Passive traders place **Limit Orders** (bids to buy, asks to sell) waiting in the order book.
  * Aggressive traders execute **Market Orders** (taking liquidity immediately).
  * When a sudden wave of aggressive market sell orders floods the market, they rapidly consume all available bids at the top of the book. 
  * If there are not enough buyers waiting, the price must plunge lower to find the next willing buyer.
* **Why It Matters for StatArb (Mean Reversion):** Order flow imbalance often reflects temporary, non-fundamental liquidity demand (e.g., a large fund liquidating quickly or a cluster of retail stop-losses). Once this one-sided wave of orders stops, the imbalance vanishes, and price naturally rebounds toward fair value.

---

### 16. Market Maker Inventory Risk
* **Plain English:** The financial danger that professional liquidity providers (market makers) face when they accumulate a large, unwanted stockpile of an asset whose price is actively falling (or rising).
* **The Market Maker's Job:** Market makers continuously quote both a **Bid** (to buy) and an **Ask** (to sell), aiming to profit from the spread without taking a directional bet.
* **The Problem (Adverse Selection):**
  * During a market sell-off, aggressive sellers hit the market maker's bids over and over.
  * The market maker is forced to absorb these sells, accumulating a massive **"Long Inventory"** in a crashing asset.
  * If the price continues dropping, the market maker suffers heavy mark-to-market losses on this inventory.
* **The Defense Mechanism (Why This Drives Reversal):**
  1. To protect themselves, market makers immediately **lower their bids** and **widen their spreads** (stepping away from the market), causing the price to temporarily crash further.
  2. Once the panic subsides, market makers find themselves holding too much inventory. To rebalance their books, they mark up prices to offload their holdings at a profit.
  3. This inventory management dynamic is a primary structural driver of **short-term price reversal** (1h to 8h).

---

### 17. Forced Liquidations
* **Plain English:** Automated, non-negotiable emergency sell (or buy) orders executed by an exchange's risk management software when a leveraged trader runs out of collateral.
* **Step-by-Step Breakdown:**
  1. **Entering the Trade:** A trader puts up \$1,000 as collateral and opens a \$10,000 position on 10x leverage in Bitcoin perpetual futures.
  2. **The Price Moves Against Them:** Bitcoin drops by 9%. The position loses \$900.
  3. **The Margin Call / Liquidation Threshold:** The trader's remaining equity drops below the exchange's "maintenance margin" requirement.
  4. **The Execution:** The exchange does not ask permission or wait for the trader to deposit more cash. Its automated risk engine instantly seizes the account and executes an **aggressive market sell order** for the entire \$10,000 position into the order book.
* **Why Quants Consider This "Uninformed" Flow:** The liquidation engine does not care about Bitcoin's valuation, news, or technology. It sells mechanically and ruthlessly at any available price purely because of code rules.
* **In Our Project:** This is the bedrock of **Alpha 1 (Volume-Conditioned Reversal)**. When an asset experiences a steep price decline accompanied by a large volume spike, it signals that forced liquidations have exhausted themselves—creating an exceptional mean-reversion buying opportunity.

---

---

### 18. Fama-French / Carhart UMD (Up Minus Down)
* **Plain English:** The premier academic and hedge fund factor representing **Cross-Sectional Momentum**. It measures the return of buying the historical relative winners ("Up") and shorting the historical relative losers ("Down").
* **Origins in Academic Finance:**
  * **Fama & French (1993)** revolutionized asset pricing with their 3-Factor Model: Market Beta, Size ($SMB$ - Small Minus Big), and Value ($HML$ - High Minus Low).
  * **Mark Carhart (1997)** discovered that mutual fund returns could not be explained by those 3 factors alone. He added a **4th factor: Momentum ($UMD$)**, proving that assets with strong past performance continue outperforming in the intermediate term.
* **The Famous "1-Month Skip" (The Microstructure Secret):**
  * In equities, Carhart defined $UMD$ using returns from month $t-12$ to month $t-2$.
  * **Notice what is missing:** Month $t-1$ (the most recent month) is intentionally **SKIPPED**!
  * **Why Skip the Most Recent Bar?** Because the most recent period is heavily contaminated by **short-term mean reversion** (bid-ask bounce, market maker inventory rebalancing, and liquidity overshooting). If you include the immediate past bar, that short-term reversal drags down your momentum signal.
* **How It Directly Drives Our Crypto Project:**
  * This is the exact mathematical trick we applied in **Module 3 & Module 5**!
  * When we tested raw unlagged momentum on crypto bars, the Sharpe was weak or negative because the immediate 4-hour bar wanted to reverse.
  * Just like Carhart skipped month $t-1$, we **skipped the immediate 4-hour bar (`shift(2)`)**. The moment we skipped that bar, our momentum Sharpe ratio skyrocketed from 0 to **1.80**!

---

## Visual Summary: How These Concepts Connect in Our Project

```
Universe of Liquid ASSETS (BTC, ETH, SOL...)
       │
       ▼
Compute Statistical Signals:
  • SHORT-TERM REVERSAL ──► Exploits CASCADING MARGIN LIQUIDATIONS
  • INTERMEDIATE MOMENTUM ─► Exploits INSTITUTIONAL CAPITAL REALLOCATION
       │
       ▼
CROSS-SECTIONAL Rank across assets at timestamp t
       │
       ▼
DEMEAN Ranks ───────────► Enforces DOLLAR-NEUTRAL (Zero MARKET EXPOSURE / Beta = 0.0)
       │
       ▼
NORMALIZE by Sum(Abs) ──► Sets GROSS LEVERAGE = 1.0 (50% Long, 50% Short)
       │
       ▼
REBALANCE Daily ────────► Slashes Turnover and Execution Friction!
```
