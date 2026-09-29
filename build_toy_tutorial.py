import json
import os
import pandas as pd
import numpy as np

target_dir = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project"
data_dir = os.path.join(target_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# 1. Create a tiny, crystal-clear toy CSV with round numbers (3 coins, 5 timestamps)
toy_data = pd.DataFrame({
    'BTC': [100.0, 110.0, 104.5, 114.95, 103.45],
    'ETH': [50.0,  50.0,  52.5,  52.5,   55.125],
    'SOL': [10.0,  9.0,   9.9,   8.91,   9.801]
}, index=['T1', 'T2', 'T3', 'T4', 'T5'])

toy_csv_path = os.path.join(data_dir, "toy_crypto_prices.csv")
toy_data.to_csv(toy_csv_path)
print(f"Created toy dataset at: {toy_csv_path}")

# 2. Build the interactive workbook notebook
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

# --- TITLE ---
add_md("""# Hands-On Minimal Toy Tutorial: Build the Entire Pipeline from Scratch!
### Quantitative StatArb Practice Lab (Just 3 Coins & 5 Timestamps)

Welcome! This workbook is designed to give you complete, 100% crystal-clear transparency into the entire quantitative trading pipeline.

Instead of analyzing thousands of bars across 10 coins, we use a **tiny toy universe**:
* **3 Coins:** `BTC`, `ETH`, `SOL`
* **5 Timestamps:** `T1`, `T2`, `T3`, `T4`, `T5`

Every number here is so simple you could calculate it with a pen, paper, and a handheld calculator in 2 minutes!

---

## The 5-Step Pipeline You Will Build:
1. **Step 1:** Load the raw price table (`toy_crypto_prices.csv`).
2. **Step 2:** Calculate asset percentage returns.
3. **Step 3:** Generate the momentum signal and calculate **Dollar-Neutral Weights** (Rank $\\rightarrow$ Demean $\\rightarrow$ Normalize).
4. **Step 4:** Calculate **Strategy Returns** (using `weights.shift(1)` to prevent lookahead bias).
5. **Step 5:** Calculate the **Sharpe Ratio**!""")

# --- STEP 1 ---
add_md("""---
## Step 1: Load the Raw Price Table

Here are the starting prices:
* **T1:** `BTC = 100`, `ETH = 50`, `SOL = 10`
* **T2:** `BTC = 110` (+10%), `ETH = 50` (0%), `SOL = 9` (-10%)
* ...and so on.

Let's load this table into Pandas and inspect it.""")

add_code("""import os
import pandas as pd
import numpy as np

# Load the toy dataset
data_path = os.path.join(os.getcwd(), 'data', 'toy_crypto_prices.csv')
prices = pd.read_csv(data_path, index_col=0)

print("=== RAW PRICE TABLE ===")
display(prices)""")

# --- STEP 2 ---
add_md("""---
## Step 2: Calculate Asset Percentage Returns

### The Math:
$$\\text{Return}_t = \\frac{\\text{Price}_t - \\text{Price}_{t-1}}{\\text{Price}_{t-1}}$$

### Pen & Paper Check (from T1 to T2):
* **BTC:** $\\frac{110 - 100}{100} = +0.10$ (+10%)
* **ETH:** $\\frac{50 - 50}{50} = 0.00$ (0%)
* **SOL:** $\\frac{9 - 10}{10} = -0.10$ (-10%)

Let's compute this in Python!""")

add_code("""# Calculate returns using price difference divided by previous price
previous_prices = prices.shift(1)
price_changes = prices - previous_prices
returns = price_changes / previous_prices

# Notice T1 has no previous price, so we drop it
returns = returns.dropna()

print("=== ASSET RETURNS TABLE ===")
display(returns.round(3))""")

# --- STEP 3 ---
add_md("""---
## Step 3: Turn Signals into Dollar-Neutral Portfolio Weights

Now, we build a **1-period Momentum strategy**:
* If a coin was the top winner $\\rightarrow$ We want to **BUY** it (positive weight).
* If a coin was the bottom loser $\\rightarrow$ We want to **SHORT** it (negative weight).
* Total Longs must equal Total Shorts (Dollar-Neutral: sum = 0).
* Total absolute exposure must equal 1.0 (Unit Leverage: sum of abs = 1.0).

### Pen & Paper Check at T2:
At T2, the returns were: `SOL = -0.10`, `ETH = 0.00`, `BTC = +0.10`.
1. **Rank from lowest to highest:**
   * `SOL` is rank 1 (lowest)
   * `ETH` is rank 2 (middle)
   * `BTC` is rank 3 (highest)
2. **Calculate Average Rank:** $\\frac{1 + 2 + 3}{3} = 2.0$
3. **Demean (Subtract 2.0 to center around zero):**
   * `SOL`: $1 - 2 = \\mathbf{-1.0}$
   * `ETH`: $2 - 2 = \\mathbf{0.0}$
   * `BTC`: $3 - 2 = \\mathbf{+1.0}$
   * *Notice:* $-1.0 + 0.0 + 1.0 = \\mathbf{0.0}$ (Dollar-neutral!).
4. **Normalize (Divide by sum of absolute values):**
   * Sum of absolute values $= |-1| + |0| + |+1| = 2.0$.
   * `SOL` weight: $-1.0 / 2.0 = \\mathbf{-0.50}$ (Short \$0.50 of SOL)
   * `ETH` weight: $0.0 / 2.0 = \\mathbf{0.00}$
   * `BTC` weight: $+1.0 / 2.0 = \\mathbf{+0.50}$ (Long \$0.50 of BTC)
   * *Notice:* $|-0.5| + |0| + |+0.5| = \\mathbf{1.0}$ (Unit leverage!).

Let's compute this for all rows in Python:""")

add_code("""# Create an empty table for weights
weights = pd.DataFrame(np.nan, index=returns.index, columns=returns.columns)

for timestamp in returns.index:
    # 1. Get current returns at this timestamp (our signal)
    current_signal = returns.loc[timestamp]
    
    # 2. Rank coins from lowest (1) to highest (3)
    ranks = current_signal.rank()
    
    # 3. Demean (subtract average rank) -> forces sum to 0.0
    centered_ranks = ranks - ranks.mean()
    
    # 4. Normalize -> forces sum of absolute weights to 1.0
    total_abs = centered_ranks.abs().sum()
    if total_abs > 0:
        weights.loc[timestamp] = centered_ranks / total_abs

print("=== PORTFOLIO WEIGHTS TABLE ===")
display(weights.round(2))

# Verify rules:
print("\\nVerification Check:")
print("1. Do weights sum to 0.0 (Dollar-Neutral)?\\n", weights.sum(axis=1).round(6))
print("2. Do absolute weights sum to 1.0 (Unit Leverage)?\\n", weights.abs().sum(axis=1).round(6))""")

# --- STEP 4 ---
add_md("""---
## Step 4: Calculate Strategy Returns (P&L)

Now, how much money did our strategy make?

### The Rule: Prevent Lookahead Bias!
* At timestamp **T2**, we decided our weights: Long BTC (+0.50), Short SOL (-0.50).
* We hold these positions from T2 to T3.
* Therefore, the return we earn at **T3** is:
  $$\\text{Strategy Return at T3} = (\\text{Weight from T2}) \\times (\\text{Asset Return at T3})$$
* That is why we use `weights.shift(1)`!

### Pen & Paper Check at T3:
* **Position decided at T2:** `BTC = +0.50`, `ETH = 0.00`, `SOL = -0.50`.
* **Asset returns that happened between T2 and T3:**
  * `BTC`: went down $-5.0\\%$ ($-0.05$)
  * `ETH`: went up $+5.0\\%$ ($+0.05$)
  * `SOL`: went up $+10.0\\%$ ($+0.10$)
* **Our Portfolio Return at T3:**
  $$\\text{Return} = (+0.50 \\times -0.05) + (0.00 \\times 0.05) + (-0.50 \\times 0.10)$$
  $$\\text{Return} = -0.025 + 0.00 - 0.050 = \\mathbf{-0.075} \\text{ (or } -7.5\\%)$$
* *Notice:* Our momentum bet lost $-7.5\\%$ because BTC reversed down and SOL reversed up!

Let's compute this in Python across all timestamps:""")

add_code("""# Shift weights by 1 timestamp so yesterday's decision earns today's return
previous_weights = weights.shift(1)

# Multiply weights by asset returns
pnl_contributions = previous_weights * returns

# Sum across all coins to get the portfolio return at each timestamp
strategy_returns = pnl_contributions.sum(axis=1).dropna()

print("=== PnL CONTRIBUTIONS PER ASSET ===")
display(pnl_contributions.round(4))

print("=== TOTAL STRATEGY RETURN PER TIMESTAMP ===")
display(strategy_returns.round(4))""")

# --- STEP 5 ---
add_md("""---
## Step 5: Calculate the Sharpe Ratio

Now we calculate the final scorecard:
$$\\text{Sharpe Ratio} = \\frac{\\text{Average Return}}{\\text{Standard Deviation (Risk)}} \\times \\sqrt{\\text{Annualization Factor}}$$

Let's compute this for our strategy!""")

add_code("""# Annualization factor (for daily data, 365 days)
ANN_FACTOR = 365

mean_return = strategy_returns.mean()
annual_return = mean_return * ANN_FACTOR

volatility = strategy_returns.std()
annual_volatility = volatility * np.sqrt(ANN_FACTOR)

if annual_volatility > 0:
    sharpe = annual_return / annual_volatility
else:
    sharpe = 0.0

print("=== FINAL STRATEGY SCORECARD ===")
print(f"Average Return per Bar : {mean_return * 100:.2f}%")
print(f"Annualized Return      : {annual_return * 100:.2f}%")
print(f"Annualized Volatility  : {annual_volatility * 100:.2f}%")
print(f"Sharpe Ratio           : {sharpe:.2f}")""")

# --- EXERCISE SECTION ---
add_md("""---
## Practice Challenge For You! (Flip to Reversal)

Remember what we learned: **Reversal is simply $-1.0 \\times \\text{Momentum}$!**

In the cell below, try running the exact same pipeline, but multiply the signal by `-1.0`:
```python
current_signal = -1.0 * returns.loc[timestamp]
```
What happens to the strategy returns and the Sharpe ratio? Run the cell below to see!""")

add_code("""# YOUR TURN: Reversal Strategy (Flipping the sign by -1.0)
rev_weights = pd.DataFrame(np.nan, index=returns.index, columns=returns.columns)

for timestamp in returns.index:
    # FLIP THE SIGN FOR REVERSAL:
    reversal_signal = -1.0 * returns.loc[timestamp]
    
    ranks = reversal_signal.rank()
    centered = ranks - ranks.mean()
    tot_abs = centered.abs().sum()
    if tot_abs > 0:
        rev_weights.loc[timestamp] = centered / tot_abs

# Calculate Reversal Strategy Returns
rev_strategy_returns = (rev_weights.shift(1) * returns).sum(axis=1).dropna()

# Reversal Sharpe Ratio
rev_annual_return = rev_strategy_returns.mean() * ANN_FACTOR
rev_annual_vol = rev_strategy_returns.std() * np.sqrt(ANN_FACTOR)
rev_sharpe = rev_annual_return / rev_annual_vol

print("=== REVERSAL STRATEGY RESULTS ===")
print(f"Momentum Sharpe: {sharpe:.2f}")
print(f"Reversal Sharpe: {rev_sharpe:.2f}")
print("-> Notice the Sharpe ratio is the EXACT OPPOSITE! That's the power of flipping the sign!")""")

output_nb_path = os.path.join(target_dir, "03_Hands_On_Minimal_Toy_Tutorial.ipynb")
with open(output_nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print(f"Hands-on Toy Tutorial created at: {output_nb_path}")
