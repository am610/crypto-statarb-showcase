import matplotlib.pyplot as plt
import matplotlib.patches as patches

# High-Resolution ML Paper Architecture Canvas (16:9 widescreen, 300 DPI)
fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
ax.set_facecolor('#0d1117')  # Dark mode GitHub / academic paper dark aesthetic
fig.patch.set_facecolor('#0d1117')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Title & Metadata
ax.text(0.5, 0.965, "END-TO-END MACHINE LEARNING SYSTEM ARCHITECTURE", 
        fontsize=18, fontweight='bold', color='#f0f6fc', ha='center', va='center')
ax.text(0.5, 0.935, "Cross-Sectional Factor Synthesis, Unsupervised Regime Detection (GMM) & Dollar-Neutral Execution", 
        fontsize=11.5, color='#8b949e', ha='center', va='center')

def draw_card(ax, x, y, w, h, title, subtitle, bullets, badge_text, color, bg_color='#161b22'):
    # Soft glowing outline
    glow = patches.FancyBboxPatch(
        (x - 0.004, y - 0.004), w + 0.008, h + 0.008,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor=color, alpha=0.15, edgecolor="none", zorder=1
    )
    ax.add_patch(glow)

    # Main Card
    card = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.006,rounding_size=0.012",
        facecolor=bg_color, edgecolor=color, linewidth=1.8, zorder=2
    )
    ax.add_patch(card)

    # Top Badge
    badge = patches.FancyBboxPatch(
        (x + 0.015, y + h - 0.026), 0.09, 0.020,
        boxstyle="round,pad=0.003,rounding_size=0.006",
        facecolor=color, edgecolor="none", zorder=3
    )
    ax.add_patch(badge)
    ax.text(x + 0.060, y + h - 0.016, badge_text, color='#0d1117', fontsize=8.5, fontweight='bold', ha='center', va='center', zorder=4)

    # Card Title
    ax.text(x + 0.115, y + h - 0.016, title, color='#f0f6fc', fontsize=11, fontweight='bold', va='center', zorder=4)

    # Subtitle
    if subtitle:
        ax.text(x + 0.018, y + h - 0.040, subtitle, color='#58a6ff', fontsize=9, fontweight='semibold', zorder=4)

    # Bullet points
    y_offset = y + h - 0.062
    for b in bullets:
        ax.text(x + 0.018, y_offset, b, color='#c9d1d9', fontsize=8.8, zorder=4)
        y_offset -= 0.021

# Connectors with arrows
def draw_arrow(ax, start, end, color='#58a6ff', rad=0.0, lw=1.6):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(
            arrowstyle="->,head_length=0.45,head_width=0.3",
            color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}"
        ),
        zorder=5
    )

# -------------------------------------------------------------
# COLUMN 1: RAW INGESTION & FEATURE ENGINEERING
# -------------------------------------------------------------
draw_card(
    ax, x=0.03, y=0.62, w=0.28, h=0.28,
    title="Raw Data Ingestion Layer",
    subtitle="Binance 4h Liquid OHLCV Panel",
    bullets=[
        "• N = 10 Liquid USDT Pairs (2022–2024)",
        "• 6,569 4h bars (24/7/365 continuous)",
        "• Close prices, Base Volume, Quote Volume",
        "• Benchmark: BTCUSDT reference factor"
    ],
    badge_text="INPUT LAYER", color="#38bdf8"
)

draw_card(
    ax, x=0.03, y=0.26, w=0.28, h=0.32,
    title="Cross-Sectional Feature Engine",
    subtitle="11 Alpha & Microstructure Predictors",
    bullets=[
        "• Lagged Momentum: 12h, 24h, 3d, 7d, 14d, 21d",
        "• 1-Bar Lag: Shift(1) eliminates bid-ask bounce",
        "• Liquidation Metric: 6-day Volume Z-Score",
        "• Volatility: 24h & 7d Realized Standard Dev",
        "• Interaction: Reversal x (1 + Vol Z-Score)"
    ],
    badge_text="FEATURES", color="#818cf8"
)

draw_arrow(ax, (0.17, 0.62), (0.17, 0.58), color="#38bdf8")

# -------------------------------------------------------------
# COLUMN 2: CROSS-SECTIONAL NORMALIZATION & TARGET
# -------------------------------------------------------------
draw_card(
    ax, x=0.35, y=0.58, w=0.29, h=0.32,
    title="Cross-Sectional Standardization",
    subtitle="Eliminating Beta & Market Swings",
    bullets=[
        "• Per-timestamp Z-scoring across assets:",
        "    Z_{k, i, t} = (X_{k, i, t} - μ_t) / σ_t",
        "• Strips systemic macro crypto drift",
        "• Target: Forward 24h return rank",
        "    Y_{i, t} = Rank(R_{i, t+1 -> t+6}) - mean",
        "• Strict Chronological Split: 2022-23 vs 2024"
    ],
    badge_text="PIPELINE", color="#a78bfa"
)

draw_arrow(ax, (0.31, 0.42), (0.35, 0.70), color="#818cf8", rad=0.1)

# -------------------------------------------------------------
# COLUMN 3: MACHINE LEARNING MODELING DUAL-BRANCH
# -------------------------------------------------------------
# Branch A: Supervised Factor Synthesis
draw_card(
    ax, x=0.68, y=0.68, w=0.29, h=0.22,
    title="Supervised Factor Synthesis",
    subtitle="Linear Shrinkage vs. Decision Trees",
    bullets=[
        "• Ridge Regression: L2 penalty on collinearity",
        "• XGBoost: Non-linear feature trees",
        "• Reality: Unconstrained trees overfit bear noise",
        "    In-Sample SR: 1.66 -> Out-of-Sample: -0.50"
    ],
    badge_text="BRANCH A", color="#f43f5e"
)

# Branch B: Unsupervised Regime Detection
draw_card(
    ax, x=0.68, y=0.42, w=0.29, h=0.22,
    title="Unsupervised Regime Detection",
    subtitle="2-State Gaussian Mixture Model (GMM)",
    bullets=[
        "• Fits GMM on 24h cross-sectional volatility",
        "• State 0 (86.3%): Quiet / Trending Regime",
        "• State 1 (13.7%): Panic Liquidation Cascade",
        "• Solves the Reversal Fee Trap dynamically"
    ],
    badge_text="BRANCH B", color="#10b981"
)

draw_arrow(ax, (0.64, 0.76), (0.68, 0.76), color="#f43f5e")
draw_arrow(ax, (0.64, 0.65), (0.68, 0.54), color="#10b981", rad=-0.05)

# -------------------------------------------------------------
# BOTTOM LAYER: ADAPTIVE REGIME SWITCHING & PORTFOLIO ENGINE
# -------------------------------------------------------------
draw_card(
    ax, x=0.35, y=0.06, w=0.29, h=0.32,
    title="Adaptive Regime Routing Engine",
    subtitle="Dynamic Capital Reallocation",
    bullets=[
        "• If Regime = Normal (Quiet):",
        "    Deploy 21-Day Lagged Momentum",
        "• If Regime = Panic (Volatility Shock):",
        "    Deploy Volume-Conditioned Reversal",
        "• Rebalance Daily (24h) to slash turnover",
        "• Full Sample Net Sharpe increases to 0.90"
    ],
    badge_text="ROUTING", color="#fbbf24"
)

draw_arrow(ax, (0.825, 0.42), (0.64, 0.22), color="#10b981", rad=0.15)

draw_card(
    ax, x=0.68, y=0.06, w=0.29, h=0.32,
    title="Portfolio Construction & Factor Attribution",
    subtitle="Dollar-Neutral Unit Leverage & Factor Alpha",
    bullets=[
        "• Dollar-Neutral: Long +50%, Short -50%",
        "• Maker Execution: Net of 7 bps trading fees",
        "• OLS Factor Regression against BTCUSDT:",
        "    Beta = -0.0037 (Zero Market Exposure)",
        "    Correlation = -0.009 | R² = 0.01%",
        "    Annualized Alpha = +16.54%"
    ],
    badge_text="EXECUTION", color="#06b6d4"
)

draw_arrow(ax, (0.64, 0.22), (0.68, 0.22), color="#fbbf24")

plt.tight_layout()
output_path = "ml_system_architecture.png"
plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"Architecture flowchart successfully saved to: {output_path}")
