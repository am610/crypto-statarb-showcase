import re

md_path = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project/QUANT_DICTIONARY.md"

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# New entries to add to TOC
new_toc = """15. [Order Flow Imbalance](#15-order-flow-imbalance)
16. [Market Maker Inventory Risk](#16-market-maker-inventory-risk)
17. [Forced Liquidations](#17-forced-liquidations)
"""

# Replace TOC
if "14. [Market Exposure (Beta)](#14-market-exposure-beta)" in text:
    text = text.replace(
        "14. [Market Exposure (Beta)](#14-market-exposure-beta)",
        "14. [Market Exposure (Beta)](#14-market-exposure-beta)\n" + new_toc.strip()
    )

new_content = """---

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
"""

# Insert before Visual Summary
if "## Visual Summary: How These Concepts Connect in Our Project" in text:
    text = text.replace(
        "## Visual Summary: How These Concepts Connect in Our Project",
        new_content.strip() + "\n\n---\n\n## Visual Summary: How These Concepts Connect in Our Project"
    )
else:
    text += "\n\n" + new_content

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("QUANT_DICTIONARY.md updated successfully!")
