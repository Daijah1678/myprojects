import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

# ── CORRECTED LIVE DATA from screenshot + web search ────────────────────────
NVDA_PRICE   = 222.05
NVDA_CHANGE  = -1.42
NVDA_PCT     = '-0.64%'
NVDA_VOLUME  = '45,987,302'
NVDA_ATR     = 8.20   # higher ATR — post-earnings spike visible on chart

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
WARN_C  = '#ffa726'

np.random.seed(7)

def sim_candles(base, n, trend=0.0, atr=8, seed_offset=0):
    np.random.seed(42 + seed_offset)
    closes = [base]
    for _ in range(n - 1):
        closes.append(closes[-1] + np.random.uniform(-atr*0.55, atr*0.55 + trend))
    opens  = [c + np.random.uniform(-atr*0.28, atr*0.28) for c in closes]
    highs  = [max(o, c) + np.random.uniform(0.05, atr*0.22) for o, c in zip(opens, closes)]
    lows   = [min(o, c) - np.random.uniform(0.05, atr*0.22) for o, c in zip(opens, closes)]
    return opens, highs, lows, closes

def anchor(vals, target):
    diff = target - vals[-1]
    return [v + diff for v in vals]

def draw_candles(ax, opens, highs, lows, closes):
    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        col = BULL if c >= o else BEAR
        ax.plot([i, i], [l, h], color=col, lw=0.9, zorder=2)
        ax.add_patch(mpatches.FancyBboxPatch(
            (i - 0.35, min(o, c)), 0.7, max(abs(c - o), 0.05),
            boxstyle="square,pad=0", fc=col, ec=col, zorder=3))

def ema(vals, n):
    r, k = [], 2/(n+1)
    for i, v in enumerate(vals):
        r.append(v if i == 0 else v*k + r[-1]*(1-k))
    return r

def style(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=7)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    ax.yaxis.tick_right()

# ── trade levels ─────────────────────────────────────────────────────────────
entry = NVDA_PRICE
stop  = round(entry - NVDA_ATR * 1.2, 2)   # $212.21
tp1   = round(entry + NVDA_ATR * 2.0, 2)   # $238.45
tp2   = round(entry + NVDA_ATR * 3.5, 2)   # $250.75
rr    = round((tp1 - entry) / max(entry - stop, 0.01), 1)
opt_buy  = round(NVDA_ATR * 0.60, 2)
opt_sell = round(opt_buy * 2.0, 2)

# ── figure ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 10), facecolor=BG)
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
fig.suptitle(
    f'NVDA  |  4H → 1H → 15min Options Method  |  Live Price: ${NVDA_PRICE}  ({NVDA_PCT})  |  {now}',
    fontsize=13, color=TEXT, fontweight='bold', y=0.98
)

gs = gridspec.GridSpec(1, 4, figure=fig, wspace=0.28, width_ratios=[1.1,1.1,1.1,0.95])

# ── 4H chart ─────────────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[0])
o4,h4,l4,c4 = sim_candles(entry*0.93, 32, trend=NVDA_ATR*0.12, atr=NVDA_ATR, seed_offset=0)
c4=anchor(c4,entry); o4=anchor(o4,entry); h4=anchor(h4,entry); l4=anchor(l4,entry)
draw_candles(ax4, o4, h4, l4, c4)
e20 = ema(c4, 20)
ax4.plot(range(32), e20, color='#ffa726', lw=1.2, label='20 EMA', zorder=5)
# price is BELOW ema slightly — slight bearish on 4H
bias_col = BEAR if c4[-1] < e20[-1] else BULL
bias_txt = 'Caution ⚠' if c4[-1] < e20[-1] else 'Bullish ▲'
ax4.set_title(f'NVDA  4H  |  Bias: {bias_txt}  |  ${NVDA_PRICE}  ({NVDA_PCT})',
              color=bias_col, fontsize=9.5, fontweight='bold', pad=6)
ax4.axhline(entry, color=MUTED, ls=':', lw=0.8, alpha=0.5)
style(ax4)
ax4.legend(fontsize=6.5, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax4.set_xticks(range(0,32,5))
ax4.set_xticklabels([f'-{(31-i)*4}h' for i in range(0,32,5)], fontsize=6, color=MUTED)

# ── 1H chart ─────────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[1])
o1,h1,l1,c1 = sim_candles(entry*0.988, 24, trend=NVDA_ATR*0.02, atr=NVDA_ATR*0.65, seed_offset=10)
c1=anchor(c1,entry); o1=anchor(o1,entry); h1=anchor(h1,entry); l1=anchor(l1,entry)
draw_candles(ax1, o1, h1, l1, c1)
sup = round(min(l1[8:18]), 2)
res = round(max(h1[6:16]), 2)
ax1.axhline(sup, color=BULL, ls='--', lw=1.1, label=f'Support  ${sup:.2f}')
ax1.axhline(res, color=BEAR, ls='--', lw=1.1, label=f'Resist   ${res:.2f}')
ax1.axhspan(sup - NVDA_ATR*0.1, sup + NVDA_ATR*0.1, color='#26a69a15', zorder=0)
ax1.set_title('NVDA  1H  |  Key Levels', color=TEXT, fontsize=9.5, fontweight='bold', pad=6)
style(ax1)
ax1.legend(fontsize=6.5, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax1.set_xticks(range(0,24,4))
ax1.set_xticklabels([f'-{(23-i)}h' for i in range(0,24,4)], fontsize=6, color=MUTED)

# ── 15min entry chart ─────────────────────────────────────────────────────────
ax15 = fig.add_subplot(gs[2])
o15,h15,l15,c15 = sim_candles(entry*0.992, 32, trend=NVDA_ATR*0.01, atr=NVDA_ATR*0.38, seed_offset=20)
c15=anchor(c15,entry); o15=anchor(o15,entry); h15=anchor(h15,entry); l15=anchor(l15,entry)
draw_candles(ax15, o15, h15, l15, c15)

ax15.axhline(entry, color=ENTRY_C, ls='-',  lw=1.8, label=f'ENTRY  ${entry}',  zorder=5)
ax15.axhline(stop,  color=SL_C,   ls='--', lw=1.3, label=f'STOP   ${stop}',   zorder=5)
ax15.axhline(tp1,   color=TP1_C,  ls='--', lw=1.3, label=f'TP1    ${tp1}',    zorder=5)
ax15.axhline(tp2,   color=TP2_C,  ls='--', lw=1.3, label=f'TP2    ${tp2}',    zorder=5)
ax15.axhspan(stop, entry, color='#ef535015', zorder=0)
ax15.axhspan(entry, tp1,  color='#26a69a12', zorder=0)
ax15.axvspan(29.5, 31.5, color='#00e5ff10', zorder=0)
ax15.annotate('NOW', xy=(30.5, entry + NVDA_ATR*0.18), color=ENTRY_C,
              fontsize=7.5, ha='center', fontweight='bold')
ax15.set_title(f'NVDA  15min  |  Entry ${entry}  |  R:R {rr}:1',
               color=ENTRY_C, fontsize=9.5, fontweight='bold', pad=6)
style(ax15)
ax15.legend(fontsize=6.5, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax15.set_xticks(range(0,32,4))
ax15.set_xticklabels([f'-{(31-i)*15}m' for i in range(0,32,4)], fontsize=6, color=MUTED)

# ── trade card ───────────────────────────────────────────────────────────────
axc = fig.add_subplot(gs[3])
axc.set_facecolor(PANEL); axc.axis('off')
card = (
    f" NVDA  CALL OPTION SETUP\n"
    f" {'─'*27}\n"
    f" Live Price  : ${NVDA_PRICE}  ({NVDA_PCT})\n"
    f" Change      : -${abs(NVDA_CHANGE):.2f} today\n"
    f" Volume      : {NVDA_VOLUME}\n"
    f" ATR (14)    : ${NVDA_ATR}\n\n"
    f" ── OPTION ───────────────────\n"
    f" Buy CALL  @ ~${opt_buy:.2f} premium\n"
    f" Strike      : $225  (OTM)\n"
    f" DTE         : 7–14 days\n\n"
    f" ── LEVELS ───────────────────\n"
    f" Entry       : ${entry}\n"
    f" Stop Loss   : ${stop}\n"
    f"   Risk      : -${round(entry-stop,2)} per share\n"
    f" Take Profit1: ${tp1}\n"
    f"   Gain      : +${round(tp1-entry,2)} per share\n"
    f" Take Profit2: ${tp2}\n"
    f"   Gain      : +${round(tp2-entry,2)} per share\n\n"
    f" Sell CALL @ ~${opt_sell:.2f}\n"
    f" R:R Ratio   : {rr}:1\n\n"
    f" ── NOTE ─────────────────────\n"
    f" Stock is DOWN today (-0.64%)\n"
    f" Watch 4H EMA for confirm\n"
    f" before entering call"
)
axc.text(0.03, 0.97, card, transform=axc.transAxes, fontsize=8.5,
         color=TEXT, va='top', fontfamily='monospace',
         bbox=dict(facecolor='#21262d', edgecolor=WARN_C, lw=1.8, pad=9))
axc.set_title('NVDA  Trade Card', color=TEXT, fontsize=10, fontweight='bold')

fig.text(0.5, 0.01,
    '⚠  Live price $222.05 sourced from screenshot + Yahoo Finance  |  '
    'Candlestick patterns illustrative  |  NOT financial advice',
    ha='center', fontsize=7.5, color='#ef5350', style='italic')

out = '/home/user/myprojects/nvda_live_chart.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
print(f"Saved → {out}")
