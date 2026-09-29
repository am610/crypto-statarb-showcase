#!/usr/bin/env python3
"""
=============================================================================
Personal & Public Web Portfolio Scanner
WSQ Crypto StatArb Framework
=============================================================================
Run locally:
    python3 app.py
Then open:
    http://localhost:5000
=============================================================================
"""

import os
import sys
import json
import warnings
import datetime
import urllib.request
import numpy as np
import pandas as pd
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string

warnings.filterwarnings('ignore', category=FutureWarning)

app = Flask(__name__)

# Known Yahoo symbol mappings
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
    end = datetime.datetime.now(datetime.timezone.utc)
    all_rows = []
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
    url = f"https://api.binance.us/api/v3/klines?symbol={coin}USDT&interval=1h&limit=600"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list) and len(data) > 0:
                times = [pd.to_datetime(row[0], unit='ms', utc=True) for row in data]
                closes = [float(row[4]) for row in data]
                return pd.Series(closes, index=times, name=coin)
    except Exception:
        pass
    return None

def fetch_single_coin(coin: str, period='1mo', interval='1h'):
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

    cb_s = fetch_coinbase_candles(coin)
    if cb_s is not None and len(cb_s) > 48:
        return cb_s

    bn_s = fetch_binance_candles(coin)
    if bn_s is not None and len(bn_s) > 48:
        return bn_s

    return None

def run_quant_engine(user_holdings: dict):
    coin_list = list(user_holdings.keys())
    fetch_list = list(set(coin_list + ['BTC']))
    
    series_dict = {}
    for c in fetch_list:
        s = fetch_single_coin(c)
        if s is not None and not s.empty:
            series_dict[c] = s
            
    if not series_dict or 'BTC' not in series_dict:
        raise ValueError("Could not retrieve market benchmark data.")
        
    df_prices = pd.DataFrame(series_dict).dropna(how='all').ffill().bfill()
    
    LOOKBACK_HOURS = 21 * 24
    LAG_HOURS = 4
    if len(df_prices) < LOOKBACK_HOURS + LAG_HOURS:
        LOOKBACK_HOURS = max(24, len(df_prices) - LAG_HOURS - 1)

    p_recent = df_prices.iloc[-LAG_HOURS]
    p_past = df_prices.iloc[-LOOKBACK_HOURS]
    mom_21d = (p_recent - p_past) / p_past
    latest_prices = df_prices.iloc[-1]
    
    hourly_returns = df_prices.pct_change(fill_method=None).dropna()
    btc_ret = hourly_returns['BTC']
    btc_var = btc_ret.var()
    betas = {}
    for c in df_prices.columns:
        if c == 'BTC':
            betas[c] = 1.0
        else:
            cov = hourly_returns[c].cov(btc_ret)
            betas[c] = float(cov / btc_var) if btc_var > 0 else 1.0

    df_metrics = pd.DataFrame({
        'Latest Price': latest_prices,
        '21d Momentum': mom_21d,
        'Beta': pd.Series(betas)
    }).dropna()
    
    # Filter to user coins
    valid_coins = [c for c in coin_list if c in df_metrics.index]
    if not valid_coins:
        raise ValueError("None of the specified coins could be resolved.")
        
    df_sub = df_metrics.loc[valid_coins].copy()
    
    # Ranks & Dollar-Neutral Weights
    df_sub['Rank'] = df_sub['21d Momentum'].rank(ascending=True)
    mean_rank = df_sub['Rank'].mean()
    demeaned = df_sub['Rank'] - mean_rank
    abs_sum = demeaned.abs().sum()
    df_sub['Zero-Beta Weight'] = (demeaned / abs_sum) if abs_sum > 0 else 0.0
    
    # Spot Long-Only Weights
    min_mom = df_sub['21d Momentum'].min()
    shifted = df_sub['21d Momentum'] - min(0, min_mom)
    df_sub['Spot Weight'] = (shifted / shifted.sum()) if shifted.sum() > 0 else (1.0 / len(df_sub))

    def action_tag(w):
        if w > 0.05:
            return "OUTPERFORM (Buy / Hold)"
        elif w < -0.05:
            return "UNDERPERFORM (Trim / Short)"
        return "NEUTRAL (Market Performer)"

    df_sub['Signal'] = df_sub['Zero-Beta Weight'].apply(action_tag)
    df_sub = df_sub.sort_values(by='21d Momentum', ascending=False)
    
    # Portfolio Aggregations
    total_val = sum(user_holdings[c] for c in valid_coins)
    port_beta = 0.0
    port_return = 0.0
    holdings_breakdown = []
    
    for c in valid_coins:
        amt = user_holdings[c]
        w = amt / total_val
        b = float(df_sub.loc[c, 'Beta'])
        m = float(df_sub.loc[c, '21d Momentum'])
        port_beta += w * b
        port_return += w * m
        holdings_breakdown.append({
            'coin': c,
            'amount': amt,
            'weight_pct': round(w * 100, 1),
            'price': round(float(df_sub.loc[c, 'Latest Price']), 4 if df_sub.loc[c, 'Latest Price'] < 1 else 2),
            'momentum_pct': round(m * 100, 2),
            'beta': round(b, 2),
            'signal': df_sub.loc[c, 'Signal'],
            'spot_weight_pct': round(float(df_sub.loc[c, 'Spot Weight']) * 100, 1),
            'zero_beta_weight_pct': round(float(df_sub.loc[c, 'Zero-Beta Weight']) * 100, 1)
        })

    btc_21d_ret = float(df_metrics.loc['BTC', '21d Momentum'])
    market_drift = port_beta * btc_21d_ret
    pure_alpha = port_return - market_drift

    return {
        'total_value': round(total_val, 2),
        'portfolio_return_pct': round(port_return * 100, 2),
        'btc_return_pct': round(btc_21d_ret * 100, 2),
        'portfolio_beta': round(port_beta, 2),
        'market_drift_pct': round(market_drift * 100, 2),
        'pure_alpha_pct': round(pure_alpha * 100, 2),
        'coins': holdings_breakdown,
        'leader': holdings_breakdown[0]['coin'],
        'laggard': holdings_breakdown[-1]['coin']
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QuantCrypto • Institutional Portfolio Diagnostic & Alpha Engine</title>
  <!-- Tailwind CSS & Chart.js CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #090e17; color: #f8fafc; }
    .glass-card { background: rgba(19, 28, 45, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .badge-outperform { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-underperform { background: rgba(244, 63, 94, 0.15); color: #f87171; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-neutral { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
  </style>
</head>
<body class="min-h-screen p-4 sm:p-8 flex flex-col items-center">

  <!-- Header -->
  <header class="w-full max-w-6xl flex flex-col sm:flex-row items-start sm:items-center justify-between pb-8 border-b border-slate-800 gap-4">
    <div>
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-xl shadow-lg shadow-cyan-500/20">Q</div>
        <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-300 to-indigo-300">
          QuantCrypto Portfolio Scanner
        </h1>
      </div>
      <p class="text-xs sm:text-sm text-slate-400 mt-1">21-Day Lagged Momentum • Bitcoin Beta & Alpha Attribution • Dollar-Neutral Rebalancing</p>
    </div>
    <div class="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      Live Data: Yahoo Finance & Coinbase API
    </div>
  </header>

  <!-- Main Container -->
  <main class="w-full max-w-6xl mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">

    <!-- Left Column: Input Form & Presets -->
    <div class="lg:col-span-1 space-y-6">
      <div class="glass-card rounded-2xl p-6 shadow-xl">
        <h2 class="text-lg font-bold text-slate-100 mb-2 flex items-center gap-2">
          <span>💼</span> Your Portfolio Holdings
        </h2>
        <p class="text-xs text-slate-400 mb-4">Enter coins and dollar amounts (e.g. <code>BTC: 10, ETH: 5, SOL: 25, SUI: 20</code>):</p>
        
        <form id="portfolioForm" onsubmit="event.preventDefault(); analyzePortfolio();">
          <div class="mb-4">
            <textarea id="holdingsInput" rows="3" class="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-sm font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 transition" placeholder="BTC:10, ETH:5, SOL:25, SUI:20">BTC:10, ETH:5, SOL:25, SUI:20</textarea>
          </div>

          <!-- Presets -->
          <div class="mb-5">
            <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Or Quick Presets:</label>
            <div class="flex flex-wrap gap-1.5">
              <button type="button" onclick="loadPreset('BTC:10, ETH:5, SOL:25, SUI:20')" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md transition border border-slate-700">My $60 Basket</button>
              <button type="button" onclick="loadPreset('SOL:300, ETH:250, SUI:200, AVAX:150, BTC:100')" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md transition border border-slate-700">Top Layer-1s</button>
              <button type="button" onclick="loadPreset('DOGE:200, PEPE:150, SHIB:100, BTC:50')" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md transition border border-slate-700">Meme Coin Basket</button>
            </div>
          </div>

          <button type="submit" id="submitBtn" class="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold py-3 px-4 rounded-xl shadow-lg shadow-cyan-500/25 transition flex items-center justify-center gap-2">
            <span>⚡ Run Quantitative Audit</span>
          </button>
        </form>
      </div>

      <!-- How it works card -->
      <div class="glass-card rounded-2xl p-6 text-xs text-slate-400 space-y-2 border-slate-800/80">
        <h3 class="font-bold text-slate-200 text-sm">💡 The 3 Quantitative Rules</h3>
        <p><strong>1. Carhart 1-Bar Lag:</strong> Skips the latest 4-hour candle to remove noisy bounces and capture the structural 21-day trend.</p>
        <p><strong>2. Bitcoin Beta (&beta;):</strong> Measures market crash sensitivity. &beta; = 1.0 means you move with Bitcoin. &beta; = 0.0 means market neutral.</p>
        <p><strong>3. Manager Alpha (&alpha;):</strong> Pure coin-picking outperformance over Bitcoin.</p>
      </div>
    </div>

    <!-- Right Column: Live Results -->
    <div class="lg:col-span-2 space-y-6">

      <!-- Loading State -->
      <div id="loading" class="hidden glass-card rounded-2xl p-12 text-center space-y-4">
        <div class="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p class="text-sm text-cyan-300 font-medium">Fetching multi-exchange live price candles and computing factor attribution...</p>
      </div>

      <!-- Error State -->
      <div id="errorAlert" class="hidden bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl text-sm"></div>

      <!-- Content State -->
      <div id="resultsContent" class="space-y-6">

        <!-- Top Stat Hero Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="glass-card rounded-2xl p-4">
            <span class="text-xs text-slate-400 block mb-1">Portfolio Value</span>
            <span id="heroTotalVal" class="text-xl sm:text-2xl font-black text-slate-100">$0.00</span>
            <span id="heroPortRet" class="text-xs font-semibold block mt-1 text-emerald-400">+0.00% (21d)</span>
          </div>

          <div class="glass-card rounded-2xl p-4">
            <span class="text-xs text-slate-400 block mb-1">Bitcoin Benchmark</span>
            <span id="heroBtcRet" class="text-xl sm:text-2xl font-black text-slate-200">+0.00%</span>
            <span class="text-xs text-slate-500 block mt-1">21-Day Baseline</span>
          </div>

          <div class="glass-card rounded-2xl p-4 border-cyan-500/30">
            <span class="text-xs text-cyan-400 block mb-1 font-semibold">Portfolio Beta (&beta;)</span>
            <span id="heroBeta" class="text-xl sm:text-2xl font-black text-cyan-300">1.00</span>
            <span id="heroBetaDesc" class="text-xs text-cyan-500/90 block mt-1">Market Sensitivity</span>
          </div>

          <div class="glass-card rounded-2xl p-4 border-emerald-500/30">
            <span class="text-xs text-emerald-400 block mb-1 font-semibold">Pure Alpha (&alpha;)</span>
            <span id="heroAlpha" class="text-xl sm:text-2xl font-black text-emerald-300">+0.00%</span>
            <span class="text-xs text-emerald-500/90 block mt-1">Manager Skill</span>
          </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="glass-card rounded-2xl p-5">
            <h3 class="text-sm font-bold text-slate-200 mb-3 flex items-center justify-between">
              <span>Current Allocation</span>
              <span class="text-xs text-slate-400">By Dollar Value</span>
            </h3>
            <div class="h-52 flex items-center justify-center">
              <canvas id="allocationChart"></canvas>
            </div>
          </div>

          <div class="glass-card rounded-2xl p-5">
            <h3 class="text-sm font-bold text-slate-200 mb-3 flex items-center justify-between">
              <span>21-Day Performance vs. BTC</span>
              <span class="text-xs text-slate-400">Percent Return</span>
            </h3>
            <div class="h-52 flex items-center justify-center">
              <canvas id="momentumChart"></canvas>
            </div>
          </div>
        </div>

        <!-- Factor Table -->
        <div class="glass-card rounded-2xl overflow-hidden shadow-xl">
          <div class="p-5 border-b border-slate-800 flex items-center justify-between">
            <h3 class="font-bold text-slate-200">Quantitative Factor Scorecard</h3>
            <span class="text-xs text-slate-400">Sorted by 21-Day Momentum</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs sm:text-sm">
              <thead class="bg-slate-950/60 text-slate-400 font-semibold uppercase text-2xs tracking-wider border-b border-slate-800">
                <tr>
                  <th class="py-3 px-4">Coin</th>
                  <th class="py-3 px-4">Price</th>
                  <th class="py-3 px-4">21d Momentum</th>
                  <th class="py-3 px-4">Beta</th>
                  <th class="py-3 px-4">Action Signal</th>
                  <th class="py-3 px-4 text-right">Zero-Beta Target</th>
                </tr>
              </thead>
              <tbody id="coinsTableBody" class="divide-y divide-slate-800/60 font-mono">
                <!-- Dynamically populated -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- Actionable Rebalancing Plan Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="glass-card rounded-2xl p-5 border-blue-500/30">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-bold text-blue-300">Option A: Spot / Coinbase (Long-Only)</h4>
              <span class="text-2xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">No Shorting</span>
            </div>
            <p class="text-xs text-slate-400 mb-3" id="spotPlanText">Analyzing optimal tilts...</p>
            <div class="text-xs text-slate-300 space-y-1" id="spotWeightsList"></div>
          </div>

          <div class="glass-card rounded-2xl p-5 border-emerald-500/30">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-bold text-emerald-300">Option B: Futures / Advanced (Market Neutral)</h4>
              <span class="text-2xs bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded">Zero-Beta</span>
            </div>
            <p class="text-xs text-slate-400 mb-3" id="neutralPlanText">Analyzing long/short hedge...</p>
            <div class="text-xs text-slate-300 space-y-1" id="neutralWeightsList"></div>
          </div>
        </div>

      </div>
    </div>
  </main>

  <footer class="mt-16 text-center text-xs text-slate-500 pb-8">
    <p>Quantitative Crypto Research Lab • Wall Street Quants Portfolio Engine</p>
  </footer>

  <script>
    let allocChart = null;
    let momChart = null;

    function loadPreset(str) {
      document.getElementById('holdingsInput').value = str;
      analyzePortfolio();
    }

    async function analyzePortfolio() {
      const input = document.getElementById('holdingsInput').value.trim();
      const loading = document.getElementById('loading');
      const results = document.getElementById('resultsContent');
      const errBox = document.getElementById('errorAlert');

      loading.classList.remove('hidden');
      results.classList.add('hidden');
      errBox.classList.add('hidden');

      try {
        const resp = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ holdings: input })
        });
        const data = await resp.json();
        
        if (!resp.ok || data.error) {
          throw new Error(data.error || 'Failed to analyze portfolio');
        }

        renderResults(data);
        results.classList.remove('hidden');
      } catch (err) {
        errBox.innerText = 'Error: ' + err.message;
        errBox.classList.remove('hidden');
      } finally {
        loading.classList.add('hidden');
      }
    }

    function renderResults(data) {
      // 1. Hero Cards
      document.getElementById('heroTotalVal').innerText = '$' + data.total_value.toLocaleString();
      const portRet = document.getElementById('heroPortRet');
      portRet.innerText = (data.portfolio_return_pct >= 0 ? '+' : '') + data.portfolio_return_pct + '% (21d)';
      portRet.className = 'text-xs font-semibold block mt-1 ' + (data.portfolio_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400');

      document.getElementById('heroBtcRet').innerText = (data.btc_return_pct >= 0 ? '+' : '') + data.btc_return_pct + '%';
      document.getElementById('heroBeta').innerText = data.portfolio_beta;
      
      const bDesc = document.getElementById('heroBetaDesc');
      if (data.portfolio_beta > 1.25) bDesc.innerText = 'High Market Sensitivity';
      else if (data.portfolio_beta < 0.85) bDesc.innerText = 'Defensive / Stable';
      else bDesc.innerText = 'Balanced with Bitcoin';

      const hAlpha = document.getElementById('heroAlpha');
      hAlpha.innerText = (data.pure_alpha_pct >= 0 ? '+' : '') + data.pure_alpha_pct + '%';
      hAlpha.className = 'text-xl sm:text-2xl font-black ' + (data.pure_alpha_pct >= 0 ? 'text-emerald-300' : 'text-rose-400');

      // 2. Table
      const tbody = document.getElementById('coinsTableBody');
      tbody.innerHTML = '';
      data.coins.forEach(c => {
        let badgeClass = 'badge-neutral';
        if (c.signal.includes('OUTPERFORM')) badgeClass = 'badge-outperform';
        else if (c.signal.includes('UNDERPERFORM')) badgeClass = 'badge-underperform';

        const row = `
          <tr class="hover:bg-slate-900/50 transition">
            <td class="py-3 px-4 font-bold text-slate-100">${c.coin} <span class="text-slate-500 font-normal">($${c.amount})</span></td>
            <td class="py-3 px-4 text-slate-300">$${c.price.toLocaleString()}</td>
            <td class="py-3 px-4 font-bold ${c.momentum_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}">${c.momentum_pct >= 0 ? '+' : ''}${c.momentum_pct}%</td>
            <td class="py-3 px-4 text-slate-300">${c.beta}</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded text-2xs font-semibold ${badgeClass}">${c.signal}</span></td>
            <td class="py-3 px-4 text-right font-bold ${c.zero_beta_weight_pct >= 0 ? 'text-cyan-400' : 'text-rose-400'}">${c.zero_beta_weight_pct >= 0 ? '+' : ''}${c.zero_beta_weight_pct}%</td>
          </tr>
        `;
        tbody.innerHTML += row;
      });

      // 3. Option A & Option B Plans
      document.getElementById('spotPlanText').innerHTML = `Overweight top momentum leader <strong>${data.leader}</strong> and reduce downside risk by trimming <strong>${data.laggard}</strong>.`;
      const spotList = document.getElementById('spotWeightsList');
      spotList.innerHTML = data.coins.map(c => `<div>• <strong>${c.coin}:</strong> Allocate ${c.spot_weight_pct}%</div>`).join('');

      document.getElementById('neutralPlanText').innerText = `Equal $ long & short positions to completely cancel Bitcoin market risk ($0.00 net exposure).`;
      const neutralList = document.getElementById('neutralWeightsList');
      const longs = data.coins.filter(c => c.zero_beta_weight_pct > 0);
      const shorts = data.coins.filter(c => c.zero_beta_weight_pct < 0);
      neutralList.innerHTML = `
        <div class="text-emerald-400"><strong>LONG:</strong> ${longs.map(c => `${c.coin} (+${c.zero_beta_weight_pct}%)`).join(', ')}</div>
        <div class="text-rose-400 mt-1"><strong>SHORT:</strong> ${shorts.map(c => `${c.coin} (${c.zero_beta_weight_pct}%)`).join(', ')}</div>
      `;

      // 4. Charts
      renderCharts(data);
    }

    function renderCharts(data) {
      const labels = data.coins.map(c => c.coin);
      const amounts = data.coins.map(c => c.amount);
      const momVals = data.coins.map(c => c.momentum_pct);
      
      const colors = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

      // Allocation Donut
      if (allocChart) allocChart.destroy();
      const ctx1 = document.getElementById('allocationChart').getContext('2d');
      allocChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: amounts,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: '#0b1120',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });

      // Momentum Bar Chart
      if (momChart) momChart.destroy();
      const ctx2 = document.getElementById('momentumChart').getContext('2d');
      momChart = new Chart(ctx2, {
        type: 'bar',
        data: {
          labels: [...labels, 'BTC Baseline'],
          datasets: [{
            label: '21d Return (%)',
            data: [...momVals, data.btc_return_pct],
            backgroundColor: [...momVals.map(v => v >= 0 ? '#10b981' : '#f43f5e'), '#38bdf8'],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // Run automatically on initial load
    window.addEventListener('DOMContentLoaded', analyzePortfolio);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        req = request.get_json() or {}
        raw_holdings = req.get('holdings', '')
        user_holdings = {}
        for item in raw_holdings.split(','):
            if ':' in item:
                k, v = item.split(':')
                user_holdings[clean_coin_ticker(k)] = float(v.strip())
                
        if not user_holdings:
            return jsonify({'error': 'Please enter at least one coin and dollar amount (e.g. BTC:10, ETH:5)'}), 400

        result = run_quant_engine(user_holdings)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"🚀 QuantCrypto Web App is running!")
    print(f"👉 Open in browser: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
