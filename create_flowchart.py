import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Canvas setup with ample breathing room
fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
ax.set_facecolor('#0b1329') # Rich dark navy background
fig.patch.set_facecolor('#0b1329')

# Define coordinates for a balanced 2-column layout
# Col 1: x = 0.08, w = 0.39
# Col 2: x = 0.53, w = 0.39
# Center: x = 0.305, w = 0.39

steps = [
    {
        "num": "STEP 1",
        "title": "Universe Ingestion & Data Hygiene",
        "desc": "• 10 Liquid Binance USDT Pairs (2022–2024)\n• 6,570 4h bars (24/7/365 continuous crypto calendar)\n• Strictly lagged returns (Zero Lookahead Bias)",
        "color": "#38bdf8", # Sky Blue
        "box": (0.08, 0.74, 0.39, 0.13)
    },
    {
        "num": "STEP 2",
        "title": "Empirical Horizon Scan",
        "desc": "• Scan 4h to 96h rolling lookback windows\n• Proves Reversal dominates <= 8h (Sharpe +3.58)\n• Discovers 1-Bar Lag (shift(2)) eliminates bounce drag",
        "color": "#fbbf24", # Amber Gold
        "box": (0.53, 0.74, 0.39, 0.13)
    },
    {
        "num": "STEP 3",
        "title": "Alpha 1: Volume-Conditioned Reversal",
        "desc": "• Microstructure Driver: Cascading forced liquidations\n• Condition 4h price drop on 6-day Volume Z-score\n• Amplifies bets when uninformed liquidation exhausts",
        "color": "#f43f5e", # Rose / Coral
        "box": (0.08, 0.51, 0.39, 0.13)
    },
    {
        "num": "STEP 4",
        "title": "Alpha 2: 21-Day Lagged Momentum",
        "desc": "• Institutional Driver: Multi-week capital reallocation\n• 21-day trend signal with 1-bar Carhart skip\n• Daily rebalancing (every 24h) slashes portfolio churn",
        "color": "#a855f7", # Violet / Purple
        "box": (0.53, 0.51, 0.39, 0.13)
    },
    {
        "num": "STEP 5",
        "title": "Execution Friction & Turnover Modeling",
        "desc": "• Real-world fees: 20 bps market vs 7 bps limit orders\n• 4h rebalancing creates >1,500x turnover, killing alpha\n• Daily rebalancing cuts churn by 88%, saving net edge",
        "color": "#ef4444", # Red
        "box": (0.08, 0.28, 0.39, 0.13)
    },
    {
        "num": "STEP 6",
        "title": "Multi-Alpha Portfolio Optimization",
        "desc": "• Alphas exhibit negative correlation (rho = -0.103)\n• Markowitz Mean-Variance & Equal-Vol weighting\n• Sharpe expands to 3.85; Volatility drops to 15.9%",
        "color": "#10b981", # Emerald Green
        "box": (0.53, 0.28, 0.39, 0.13)
    },
    {
        "num": "STEP 7",
        "title": "Institutional Risk & Factor Attribution",
        "desc": "• Underwater drawdown profile (Max Drawdown: -25.5%)\n• Single-index factor regression vs. Bitcoin benchmark\n• Beta = 0.00 to BTC -> 100% Pure Market-Neutral Alpha",
        "color": "#06b6d4", # Cyan / Teal
        "box": (0.305, 0.05, 0.39, 0.13)
    }
]

# Draw Cards
for step in steps:
    x, y, w, h = step["box"]
    color = step["color"]
    
    # Outer Glow
    glow = patches.FancyBboxPatch(
        (x - 0.005, y - 0.005), w + 0.01, h + 0.01,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor=color, alpha=0.18, edgecolor="none", zorder=1
    )
    ax.add_patch(glow)
    
    # Main Box
    card = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.008,rounding_size=0.016",
        facecolor='#162038', edgecolor=color, linewidth=2.0, zorder=2
    )
    ax.add_patch(card)
    
    # Step Badge
    badge = patches.FancyBboxPatch(
        (x + 0.015, y + h - 0.030), 0.08, 0.022,
        boxstyle="round,pad=0.004,rounding_size=0.008",
        facecolor=color, edgecolor="none", zorder=3
    )
    ax.add_patch(badge)
    ax.text(
        x + 0.055, y + h - 0.019, step["num"],
        color='#0b1329', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=4
    )
    
    # Header Title
    ax.text(
        x + 0.108, y + h - 0.019, step["title"],
        color='#ffffff', fontsize=12, fontweight='bold', va='center', zorder=4
    )
    
    # Description
    ax.text(
        x + 0.018, y + h * 0.44, step["desc"],
        color='#cbd5e1', fontsize=9.8, va='center', linespacing=1.6, zorder=4
    )

# Clean Directional Arrows
def connect_nodes(start, end, rad=0.0):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(
            arrowstyle="-|>", color="#38bdf8", lw=2.4,
            mutation_scale=18, connectionstyle=f"arc3,rad={rad}"
        ),
        zorder=5
    )

# Step 1 -> Step 2 (Data to Horizon Scan)
connect_nodes((0.47, 0.805), (0.53, 0.805))

# Step 2 -> Step 3 (Horizon Scan reveals Reversal)
connect_nodes((0.53, 0.75), (0.35, 0.64), rad=0.15)

# Step 2 -> Step 4 (Horizon Scan reveals Momentum)
connect_nodes((0.725, 0.74), (0.725, 0.64))

# Step 3 -> Step 5 (Reversal needs Turnover/Execution modeling)
connect_nodes((0.275, 0.51), (0.275, 0.41))

# Step 4 -> Step 5 (Momentum daily rebalancing evaluated)
connect_nodes((0.53, 0.52), (0.38, 0.41), rad=0.12)

# Step 4 -> Step 6 (Momentum into Multi-Alpha blend)
connect_nodes((0.725, 0.51), (0.725, 0.41))

# Step 3 -> Step 6 (Reversal into Multi-Alpha blend)
connect_nodes((0.47, 0.53), (0.58, 0.41), rad=-0.12)

# Step 5 -> Step 7 (Execution reality into Final Scorecard)
connect_nodes((0.275, 0.28), (0.42, 0.18), rad=-0.12)

# Step 6 -> Step 7 (Optimal blend into Final Scorecard)
connect_nodes((0.725, 0.28), (0.58, 0.18), rad=0.12)

# Global Flowchart Title
ax.text(
    0.5, 0.965, "Statistical Arbitrage in Cryptocurrencies: Research Pipeline",
    color='#ffffff', fontsize=19, fontweight='bold', ha='center', va='top'
)
ax.text(
    0.5, 0.932, "From Raw Bar Data to Market-Neutral Multi-Alpha Systematic Execution",
    color='#94a3b8', fontsize=12, ha='center', va='top'
)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

out_path = "/Users/ayan/Programs/Quant/WSQ/To_Do/Crypto_StatArb_Project/project_flowchart.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()

print("Clean flowchart regenerated at:", out_path)
