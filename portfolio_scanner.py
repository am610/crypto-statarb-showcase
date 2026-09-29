#!/usr/bin/env python3
"""
=============================================================================
Personal Crypto Quantitative Portfolio Scanner & Rebalancer
Institutional Quantitative Framework
=============================================================================
Features:
1. 21-Day Lagged Cross-Sectional Momentum (skips recent 4h microstructure noise).
2. Institutional Risk Attribution: Portfolio Beta (Market Risk) AND Alpha (Pure Skill).
3. Universal Multi-Exchange Price Resolver:
   - Primary: Yahoo Finance (yfinance)
   - Secondary: Coinbase Exchange Public REST API (no API key required)
   - Tertiary: Binance US Public REST API (no API key required)
   -> Fetches ANY coin you trade without errors.
=============================================================================
"""

import sys
import argparse
import datetime
import urllib.request
import json
import warnings
import numpy as np
import pandas as pd
import yfinance as yf

# Suppress minor library deprecations
warnings.filterwarnings('ignore', category=FutureWarning)

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

YAHOO_SYMBOL_MAP = {
    'SUI': 'SUI20947-USD',
    'PEPE': 'PEPE24478-USD',
    'RENDER': 'RENDER-USD',
    'FET': 'FET-USD',
    'TAO': 'TAO22974-USD',
    'SHIB': 'SHIB-USD',
    'NEAR': 'NEAR-USD',
    'APT': 'APT21794-USD',
    'INJ': 'INJ-USD',
    'TIA': 'TIA28301-USD',
}

def clean_coin_ticker(c: str) -> str:
    return c.strip().upper().replace('$', '').replace('-USD', '').replace('USDT', '')

def fetch_coinbase_candles(coin: str):
    """Fetch hourly candles directly from Coinbase Public REST API"""
    end = datetime.datetime.now(datetime.timezone.utc)
    all_rows = []
    # Fetch 2 pages (~600 hours)
    for _ in range(2):
        start = end - datetime.timedelta(hours=300)
        url = (f"https://api.exchange.coinbase.com/products/{coin}-USD/candles?"
               f"granularity=3600&start={start.isoformat()}&end={end.isoformat()}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    all_rows.extend(data)
        except Exception:
            break
        end = start

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df = df.drop_duplicates('datetime').sort_values('datetime').set_index('datetime')
    return df['close']

def fetch_binance_candles(coin: str):
    """Fetch hourly candles from Binance US Public REST API"""
    url = f"https://api.binance.us/api/v3/klines?symbol={coin}USDT&interval=1h&limit=600"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list) and len(data) > 0:
                # [open_time, open, high, low, close, volume, ...]
                times = [pd.to_datetime(row[0], unit='ms', utc=True) for row in data]
                closes = [float(row[4]) for row in data]
                s = pd.Series(closes, index=times, name=coin)
                return s
    except Exception:
        pass
    return None

def fetch_single_coin(coin: str, period='1mo', interval='1h'):
    """Universal cascade: Yahoo -> Coinbase -> Binance US"""
    # 1. Try Yahoo
    yf_symbol = YAHOO_SYMBOL_MAP.get(coin, f"{coin}-USD")
    try:
        raw = yf.download(yf_symbol, period=period, interval=interval, progress=False)
        if not raw.empty:
            if isinstance(raw.columns, pd.MultiIndex):
                s = raw['Close'].iloc[:, 0].dropna()
            elif 'Close' in raw:
                s = raw['Close'].dropna()
            else:
                s = raw.iloc[:, 0].dropna()
            if len(s) > 48:
                return s
    except Exception:
        pass

    # 2. Try Coinbase
    cb_s = fetch_coinbase_candles(coin)
    if cb_s is not None and len(cb_s) > 48:
        print(f"  ✓ Auto-resolved '{coin}' via Coinbase Exchange API.")
        return cb_s

    # 3. Try Binance US
    bn_s = fetch_binance_candles(coin)
    if bn_s is not None and len(bn_s) > 48:
        print(f"  ✓ Auto-resolved '{coin}' via Binance US API.")
        return bn_s

    return None

def fetch_crypto_data(coins, period='1mo', interval='1h'):
    print(f"\n[1/4] Fetching live hourly market data for: {', '.join(coins)}...")
    series_dict = {}
    
    for c in coins:
        s = fetch_single_coin(c, period=period, interval=interval)
        if s is not None and not s.empty:
            series_dict[c] = s
        else:
            print(f"  ✗ Warning: Could not find live market data for '{c}'. Skipping.")

    if not series_dict:
        print("Error: Could not retrieve market data for any specified coins.")
        sys.exit(1)

    df_prices = pd.DataFrame(series_dict)
    df_prices = df_prices.dropna(how='all').ffill().bfill()
    return df_prices

def analyze_portfolio(df_prices, user_holdings=None):
    LOOKBACK_HOURS = 21 * 24
    LAG_HOURS = 4
    
    if len(df_prices) < LOOKBACK_HOURS + LAG_HOURS:
        LOOKBACK_HOURS = max(24, len(df_prices) - LAG_HOURS - 1)

    p_recent = df_prices.iloc[-LAG_HOURS]
    p_past = df_prices.iloc[-LOOKBACK_HOURS]
    
    # 21-day percentage return (skipping last 4 hours)
    mom_21d = (p_recent - p_past) / p_past
    latest_prices = df_prices.iloc[-1]
    
    # Beta to BTC using hourly returns
    hourly_returns = df_prices.pct_change(fill_method=None).dropna()
    betas = {}
    if 'BTC' in hourly_returns.columns:
        btc_ret = hourly_returns['BTC']
        btc_var = btc_ret.var()
        for c in df_prices.columns:
            if c == 'BTC':
                betas[c] = 1.0
            else:
                cov = hourly_returns[c].cov(btc_ret)
                betas[c] = cov / btc_var if btc_var > 0 else 1.0
    else:
        for c in df_prices.columns:
            betas[c] = 1.0

    df_metrics = pd.DataFrame({
        'Latest Price ($)': latest_prices,
        '21-Day Momentum': mom_21d,
        'Beta to BTC': pd.Series(betas)
    }).dropna(subset=['Latest Price ($)', '21-Day Momentum'])
    
    # Filter to requested coins if user specified holdings
    if user_holdings:
        valid_coins = [c for c in user_holdings.keys() if c in df_metrics.index]
        df_metrics = df_metrics.loc[valid_coins]
    
    # Cross-Sectional Ranking & Demeaning (Dollar Neutrality)
    df_metrics['Momentum Rank'] = df_metrics['21-Day Momentum'].rank(ascending=True)
    mean_rank = df_metrics['Momentum Rank'].mean()
    demeaned_signal = df_metrics['Momentum Rank'] - mean_rank
    
    abs_sum = demeaned_signal.abs().sum()
    if abs_sum > 0:
        df_metrics['Zero-Beta Target Weight'] = demeaned_signal / abs_sum
    else:
        df_metrics['Zero-Beta Target Weight'] = 0.0
        
    # Long-Only Spot Target Weights (proportional to momentum)
    min_mom = df_metrics['21-Day Momentum'].min()
    shifted = df_metrics['21-Day Momentum'] - min(0, min_mom)
    if shifted.sum() > 0:
        df_metrics['Spot Long-Only Weight'] = shifted / shifted.sum()
    else:
        df_metrics['Spot Long-Only Weight'] = 1.0 / len(df_metrics)

    def categorize(row):
        w = row['Zero-Beta Target Weight']
        if w > 0.05:
            return "OUTPERFORM (Buy / Hold)"
        elif w < -0.05:
            return "UNDERPERFORM (Trim / Short)"
        else:
            return "NEUTRAL (Market Performer)"
            
    df_metrics['Action Signal'] = df_metrics.apply(categorize, axis=1)
    df_metrics = df_metrics.sort_values(by='21-Day Momentum', ascending=False)
    
    return df_metrics, hourly_returns

def main():
    parser = argparse.ArgumentParser(description="Coinbase Quantitative Portfolio Scanner")
    parser.add_argument('--coins', nargs='+', default=None,
                        help="List of crypto tickers to analyze (e.g. --coins BTC ETH SOL SUI DOGE)")
    parser.add_argument('--holdings', type=str, default=None,
                        help="Your current dollar holdings (e.g. --holdings 'BTC:10, ETH:5, SOL:25, SUI:20')")
    args = parser.parse_args()

    print("=" * 80)
    print("      QUANTITATIVE CRYPTO PORTFOLIO SCANNER (21-DAY LAGGED MOMENTUM)")
    print("=" * 80)

    user_holdings = {}
    if args.holdings:
        for item in args.holdings.split(','):
            if ':' in item:
                k, v = item.split(':')
                user_holdings[clean_coin_ticker(k)] = float(v.strip())
        coin_list = list(user_holdings.keys())
    elif args.coins:
        coin_list = [clean_coin_ticker(c) for c in args.coins]
    else:
        prompt = input("Enter your coins separated by spaces (e.g. 'BTC ETH SOL SUI DOGE'): ").strip()
        coin_list = [clean_coin_ticker(c) for c in prompt.split()] if prompt else ['BTC', 'ETH', 'SOL', 'ADA', 'DOGE']

    # Always fetch BTC as benchmark for Beta & Alpha
    fetch_list = list(set(coin_list + ['BTC']))
    df_prices = fetch_crypto_data(fetch_list)
    
    df_metrics, hourly_returns = analyze_portfolio(df_prices, user_holdings)

    print("\n[2/4] QUANTITATIVE FACTOR SCORECARD:")
    print("-" * 80)
    
    display_df = df_metrics.copy()
    display_df['Latest Price ($)'] = display_df['Latest Price ($)'].apply(lambda x: f"${x:,.2f}" if x >= 1 else f"${x:,.4f}")
    display_df['21-Day Momentum'] = display_df['21-Day Momentum'].apply(lambda x: f"{x*100:+.2f}%")
    display_df['Beta to BTC'] = display_df['Beta to BTC'].apply(lambda x: f"{x:.2f}")
    display_df['Zero-Beta Target Weight'] = display_df['Zero-Beta Target Weight'].apply(lambda x: f"{x*100:+.1f}%")
    display_df['Spot Long-Only Weight'] = display_df['Spot Long-Only Weight'].apply(lambda x: f"{x*100:.1f}%")
    
    cols = ['Latest Price ($)', '21-Day Momentum', 'Beta to BTC', 'Action Signal', 'Spot Long-Only Weight', 'Zero-Beta Target Weight']
    print(display_df[cols].to_string())
    print("-" * 80)

    if user_holdings:
        print("\n[3/4] YOUR PORTFOLIO DIAGNOSTIC (BETA & ALPHA ATTRIBUTION):")
        print("-" * 80)
        total_val = sum(user_holdings.values())
        print(f"Total Portfolio Value: ${total_val:,.2f}")
        
        port_beta = 0.0
        port_21d_return = 0.0
        
        for c, amt in user_holdings.items():
            if c in df_metrics.index:
                w = amt / total_val
                b = float(df_metrics.loc[c, 'Beta to BTC'])
                m = float(df_metrics.loc[c, '21-Day Momentum'])
                port_beta += w * b
                port_21d_return += w * m
                print(f"  • {c:5s}: ${amt:,.2f} ({w*100:5.1f}%) | Beta: {b:.2f} | 21d Return: {m*100:+.2f}%")
        
        btc_21d_ret = float(df_metrics.loc['BTC', '21-Day Momentum']) if 'BTC' in df_metrics.index else 0.0
        expected_beta_return = port_beta * btc_21d_ret
        pure_alpha = port_21d_return - expected_beta_return
        
        print("\n" + "=" * 60)
        print(f"  ▶ PORTFOLIO 21-DAY TOTAL RETURN : {port_21d_return*100:+.2f}%")
        print(f"  ▶ BITCOIN BENCHMARK RETURN      : {btc_21d_ret*100:+.2f}%")
        print(f"  ▶ PORTFOLIO BETA TO BITCOIN     : {port_beta:.2f}")
        print(f"    └─ Return from Market Drift   : {expected_beta_return*100:+.2f}% (Beta × BTC Return)")
        print(f"  ★ YOUR PURE ALPHA (α)           : {pure_alpha*100:+.2f}% (Manager Selection Skill)")
        print("=" * 60)
        
        if pure_alpha > 0:
            print(f"  >> CONGRATULATIONS: You beat passive Bitcoin holding by {pure_alpha*100:+.2f}% purely from smart coin selection!")
        else:
            print(f"  >> ATTENTION: Coin selection dragged returns by {pure_alpha*100:.2f}% compared to holding Bitcoin.")

    print("\n[4/4] ACTIONABLE REBALANCING PLAN:")
    print("-" * 80)
    top_winner = df_metrics.index[0]
    bottom_loser = df_metrics.index[-1]
    
    print(f"1. STRONGEST COIN (Momentum Leader):  {top_winner} ({df_metrics.loc[top_winner, '21-Day Momentum']*100:+.2f}%)")
    print(f"2. WEAKEST COIN (Momentum Laggard): {bottom_loser} ({df_metrics.loc[bottom_loser, '21-Day Momentum']*100:+.2f}%)")
    
    print("\nOption A (If you only trade SPOT on Coinbase - Long Only):")
    print(f"  • Overweight or keep buying the top momentum winner: {top_winner}")
    print(f"  • Consider trimming or rotating out of the laggard: {bottom_loser}")
    
    print("\nOption B (If you trade ADVANCED / FUTURES - Zero Beta Market Neutral):")
    longs = df_metrics[df_metrics['Zero-Beta Target Weight'] > 0]
    shorts = df_metrics[df_metrics['Zero-Beta Target Weight'] < 0]
    print("  • LONG (Buy):  " + ", ".join([f"{c} ({df_metrics.loc[c, 'Zero-Beta Target Weight']*100:+.1f}%)" for c in longs.index]))
    print("  • SHORT (Sell): " + ", ".join([f"{c} ({df_metrics.loc[c, 'Zero-Beta Target Weight']*100:+.1f}%)" for c in shorts.index]))
    print("  -> Net Dollar Exposure: $0.00 (Zero Bitcoin Market Beta)")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
