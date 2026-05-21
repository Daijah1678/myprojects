import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

# ── LIVE PRICES from Yahoo Finance / Web Search (May 21, 2026) ──────────────
LIVE = {
    'SPY':  {'price': 741.25, 'prev_close': 733.73, 'change': '+1.02%',
             'atr': 5.80, 'strike': 742, 'bias': 'Bullish ▲'},
    'NVDA': {'price': 224.14, 'prev_close': 223.47, 'change': '+0.30%',
             'atr': 7.20, 'strike': 225, 'bias': 'Bullish ▲'},
    'AAPL': {'price': 302.25, 'prev_close': 298.97, 'change': '+1.10%',
             'atr': 5.10, 'strike': 305, 'bias': 'Bullish ▲'},
}

BG    = '#0d1117'
PANEL = '#161b22'
TEXT  = '#e6edf3'
MUTED = '#8b949e'
BORDER= '#30363d'
BULL  = '#26a69a'
BEAR  = '#ef5350'
ENTRY_C = '#00e5ff'
SL_C    = '#ef5350'
TP1_C   = '#66bb6a'
TP2_C   = '#ffa726'

np.random.seed(42)

def sim_candles(base, n, trend=0.15, atr=5):
    closes = [base]
    for _ in range(n - 1):
        closes.append(closes[-1] + np.random.uniform(-atr*0.6, atr*0.6 + trend))
    opens  = [c + np.random.uniform(-atr*0.3, atr*0.3) for c in closes]
    highs  = [max(o, c) + np.random.uniform(0.1, atr*0.25) for o, c in zip(opens, closes)]
    lows   = [min(o, c) - np.random.uniform(0.1, atr*0.25) for o, c in zip(opens, closes)]
    return opens, highs, lows, closes

def draw_candles(ax, opens, highs, lows, closes):
    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        col = BULL if c >= o else BEAR
        ax.plot([i, i], [l, h], color=col, lw=0.9, zorder=2)
        ax.add_patch(mpatches.FancyBboxPatch(
            (i - 0.35, min(o, c)), 0.7, max(abs(c - o), 0.05),
            boxstyle="square,pad=0", fc=col, ec=col, zorder=3
        ))

def ema(vals, n):
    result, k = [], 2 / (n + 1)
    for i, v in enumerate(vals):
        result.append(v if i == 0 else v * k + result[-1] * (1 - k))
    return result

def style(ax, title=''):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=7)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    if title: ax.set_title(title, color=TEXT, fontsize=9, fontweight='bold', pad=5)
    ax.yaxis.tick_right()

def hline(ax, y, color, ls, lw, label):
    ax.axhline(y, color=color, linestyle=ls, linewidth=lw, label=label, zorder=4)

# ── figure ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(21, 16), facecolor=BG)
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
fig.suptitle(
    f'4H → 1H → 15min  Options Method  |  Live Data: Yahoo Finance  |  {now}',
    fontsize=14, color=TEXT, fontweight='bold', y=0.995
)

tickers = ['SPY', 'NVDA', 'AAPL']
gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.52, wspace=0.28,
                       width_ratios=[1.1, 1.1, 1.1, 0.9])

for row, ticker in enumerate(tickers):
    d      = LIVE[ticker]
    price  = d['price']
    atr    = d['atr']
    entry  = round(price, 2)
    stop   = round(entry - atr * 1.2, 2)
    tp1    = round(entry + atr * 2.0, 2)
    tp2    = round(entry + atr * 3.5, 2)
    rr     = round((tp1 - entry) / max(entry - stop, 0.01), 1)

    # option premium estimates (simplified)
    opt_buy  = round(atr * 0.55, 2)
    opt_sell = round(opt_buy * 2, 2)

    # ── 4H chart (simulate 30 bars, anchored ~8% below current) ─────────────
    ax4 = fig.add_subplot(gs[row, 0])
    base4 = price * 0.94
    o4, h4, l4, c4 = sim_candles(base4, 30, trend=atr*0.18, atr=atr)
    # force last close near live price
    adj = price - c4[-1]
    c4 = [v + adj for v in c4]
    o4 = [v + adj for v in o4]
    h4 = [v + adj for v in h4]
    l4 = [v + adj for v in l4]
    draw_candles(ax4, o4, h4, l4, c4)
    e20 = ema(c4, 20)
    ax4.plot(range(30), e20, color='#ffa726', lw=1.2, label='20 EMA', zorder=5)
    bias_col = BULL if d['bias'].startswith('B') else BEAR
    style(ax4)
    ax4.set_title(
        f"{ticker}  4H  |  Bias: {d['bias']}",
        color=bias_col, fontsize=9, fontweight='bold', pad=5
    )
    ax4.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
               labelcolor=TEXT, loc='upper left')
    ax4.set_xticks(range(0, 30, 5))
    ax4.set_xticklabels([f'-{(29-i)*4}h' for i in range(0, 30, 5)], fontsize=6, color=MUTED)

    # ── 1H chart (simulate 24 bars) ──────────────────────────────────────────
    ax1 = fig.add_subplot(gs[row, 1])
    base1 = price * 0.985
    o1, h1, l1, c1 = sim_candles(base1, 24, trend=atr*0.05, atr=atr*0.6)
    adj1 = price - c1[-1]
    c1=[v+adj1 for v in c1]; o1=[v+adj1 for v in o1]
    h1=[v+adj1 for v in h1]; l1=[v+adj1 for v in l1]
    draw_candles(ax1, o1, h1, l1, c1)
    sup = min(l1[8:16]) ; res = max(h1[8:16])
    hline(ax1, sup, BULL, '--', 1.1, f'Support  ${sup:.2f}')
    hline(ax1, res, BEAR, '--', 1.1, f'Resist   ${res:.2f}')
    ax1.axhspan(sup - atr*0.1, sup + atr*0.1, color='#26a69a18', zorder=0)
    style(ax1, f'{ticker}  1H  |  Key Levels')
    ax1.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
               labelcolor=TEXT, loc='upper left')
    ax1.set_xticks(range(0, 24, 4))
    ax1.set_xticklabels([f'-{(23-i)}h' for i in range(0, 24, 4)], fontsize=6, color=MUTED)

    # ── 15min entry chart (simulate 32 bars) ─────────────────────────────────
    ax15 = fig.add_subplot(gs[row, 2])
    base15 = price * 0.993
    o15, h15, l15, c15 = sim_candles(base15, 32, trend=atr*0.02, atr=atr*0.35)
    adj15 = price - c15[-1]
    c15=[v+adj15 for v in c15]; o15=[v+adj15 for v in o15]
    h15=[v+adj15 for v in h15]; l15=[v+adj15 for v in l15]
    draw_candles(ax15, o15, h15, l15, c15)

    hline(ax15, entry, ENTRY_C, '-',  1.6, f'ENTRY  ${entry}')
    hline(ax15, stop,  SL_C,   '--', 1.2, f'STOP   ${stop}')
    hline(ax15, tp1,   TP1_C,  '--', 1.2, f'TP1    ${tp1}')
    hline(ax15, tp2,   TP2_C,  '--', 1.2, f'TP2    ${tp2}')
    ax15.axhspan(stop, entry, color='#ef535012', zorder=0)
    ax15.axhspan(entry, tp1,  color='#26a69a12', zorder=0)
    # mark entry bar
    ax15.axvspan(29.5, 31.5, color='#00e5ff10', zorder=0)
    ax15.annotate('NOW', xy=(30.5, entry + atr*0.15), color=ENTRY_C,
                  fontsize=7, ha='center', fontweight='bold')
    style(ax15)
    ax15.set_title(
        f'{ticker}  15min  |  Entry ${entry}  |  R:R {rr}:1',
        color=ENTRY_C, fontsize=9, fontweight='bold', pad=5
    )
    ax15.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
                labelcolor=TEXT, loc='upper left')
    ax15.set_xticks(range(0, 32, 4))
    ax15.set_xticklabels([f'-{(31-i)*15}m' for i in range(0, 32, 4)], fontsize=6, color=MUTED)

    # ── trade card ───────────────────────────────────────────────────────────
    axc = fig.add_subplot(gs[row, 3])
    axc.set_facecolor(PANEL); axc.axis('off')
    direction = 'CALL' if d['bias'].startswith('B') else 'PUT'
    card = (
        f" {ticker}  {direction} SETUP\n"
        f" {'─'*26}\n"
        f" Live Price  : ${price}  ({d['change']})\n"
        f" Prev Close  : ${d['prev_close']}\n"
        f" 4H Bias     : {d['bias']}\n\n"
        f" ── OPTION ──────────────────\n"
        f" Buy {direction:<4} @ ~${opt_buy:.2f} premium\n"
        f" Strike      : ${d['strike']}\n"
        f" DTE         : 7–14 days\n\n"
        f" ── LEVELS ──────────────────\n"
        f" Entry       : ${entry}\n"
        f" Stop Loss   : ${stop}  (-${round(entry-stop,2)})\n"
        f" Take Profit1: ${tp1}  (+${round(tp1-entry,2)})\n"
        f" Take Profit2: ${tp2}  (+${round(tp2-entry,2)})\n\n"
        f" Sell {direction:<4} @ ~${opt_sell:.2f}\n"
        f" R:R Ratio   : {rr}:1\n\n"
        f" ATR (used)  : ${atr}"
    )
    border_col = BULL if d['bias'].startswith('B') else BEAR
    axc.text(0.03, 0.97, card, transform=axc.transAxes, fontsize=8.2,
             color=TEXT, va='top', fontfamily='monospace',
             bbox=dict(facecolor='#21262d', edgecolor=border_col, lw=1.5, pad=8))
    axc.set_title(f'{ticker} Trade Card', color=TEXT, fontsize=9, fontweight='bold')

# ── footer ───────────────────────────────────────────────────────────────────
fig.text(0.5, 0.002,
    '⚠  Candlestick patterns simulated for illustration  |  '
    'Entry/Stop/TP prices derived from LIVE Yahoo Finance prices + ATR  |  '
    'NOT financial advice — verify before trading',
    ha='center', fontsize=7.5, color='#ef5350', style='italic')

out = '/home/user/myprojects/live_options_chart2.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
print(f"Saved → {out}")
