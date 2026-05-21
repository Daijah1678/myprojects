import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

# ── LIVE DATA — screenshot + Yahoo Finance / web search ──────────────────────
IWM_PRICE    = 278.63
IWM_CHANGE   = -1.26
IWM_PCT      = '-0.45%'
IWM_VOLUME   = '4,050,731'
IWM_52WK_LOW = 199.65
IWM_52WK_HI  = 287.58
IWM_SUPPORT  = 266.42   # from Barchart cheat sheet
IWM_RESIST   = 282.61   # from Barchart cheat sheet
IWM_ATR      = 4.80

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

def sim_candles(base, n, trend=0.0, atr=4, seed=0):
    np.random.seed(seed)
    closes = [base]
    for _ in range(n - 1):
        closes.append(closes[-1] + np.random.uniform(-atr*0.55, atr*0.55 + trend))
    opens = [c + np.random.uniform(-atr*0.28, atr*0.28) for c in closes]
    highs = [max(o,c) + np.random.uniform(0.05, atr*0.22) for o,c in zip(opens,closes)]
    lows  = [min(o,c) - np.random.uniform(0.05, atr*0.22) for o,c in zip(opens,closes)]
    return opens, highs, lows, closes

def anchor(vals, target):
    d = target - vals[-1]
    return [v + d for v in vals]

def draw_candles(ax, o, h, l, c):
    for i, (ov,hv,lv,cv) in enumerate(zip(o,h,l,c)):
        col = BULL if cv >= ov else BEAR
        ax.plot([i,i],[lv,hv], color=col, lw=0.9, zorder=2)
        ax.add_patch(mpatches.FancyBboxPatch(
            (i-0.35, min(ov,cv)), 0.7, max(abs(cv-ov),0.05),
            boxstyle="square,pad=0", fc=col, ec=col, zorder=3))

def ema(vals, n):
    r, k = [], 2/(n+1)
    for i,v in enumerate(vals):
        r.append(v if i==0 else v*k + r[-1]*(1-k))
    return r

def style(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=7)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    ax.yaxis.tick_right()

# ── trade levels ─────────────────────────────────────────────────────────────
entry = IWM_PRICE
stop  = round(entry - IWM_ATR * 1.2, 2)    # $272.87
tp1   = round(entry + IWM_ATR * 2.0, 2)    # $288.23  (near 52wk high $287.58)
tp2   = round(entry + IWM_ATR * 3.5, 2)    # $295.43
rr    = round((tp1 - entry) / max(entry - stop, 0.01), 1)
opt_buy  = round(IWM_ATR * 0.55, 2)
opt_sell = round(opt_buy * 2.0, 2)

# ── figure ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 10), facecolor=BG)
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
fig.suptitle(
    f'IWM (iShares Russell 2000)  |  4H → 1H → 15min Method  |'
    f'  Live: ${IWM_PRICE}  ({IWM_PCT})  |  {now}',
    fontsize=13, color=TEXT, fontweight='bold', y=0.98
)

gs = gridspec.GridSpec(1, 4, figure=fig, wspace=0.28, width_ratios=[1.1,1.1,1.1,0.95])

# ── 4H chart ─────────────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[0])
o4,h4,l4,c4 = sim_candles(entry*0.935, 32, trend=IWM_ATR*0.10, atr=IWM_ATR, seed=1)
c4=anchor(c4,entry); o4=anchor(o4,entry); h4=anchor(h4,entry); l4=anchor(l4,entry)
draw_candles(ax4, o4, h4, l4, c4)
e20 = ema(c4, 20)
ax4.plot(range(32), e20, color='#ffa726', lw=1.2, label='20 EMA', zorder=5)

# IWM is near resistance zone — cautious bias
bias_col = '#ffa726'
bias_txt = 'Neutral ⚠  Near Resist'
ax4.axhline(IWM_RESIST, color=BEAR, ls=':', lw=1.0, alpha=0.7, label=f'Resist ${IWM_RESIST}')
ax4.axhline(IWM_SUPPORT, color=BULL, ls=':', lw=1.0, alpha=0.7, label=f'Support ${IWM_SUPPORT}')
ax4.set_title(f'IWM  4H  |  {bias_txt}  |  ${IWM_PRICE}',
              color=bias_col, fontsize=9.5, fontweight='bold', pad=6)
style(ax4)
ax4.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax4.set_xticks(range(0,32,5))
ax4.set_xticklabels([f'-{(31-i)*4}h' for i in range(0,32,5)], fontsize=6, color=MUTED)

# ── 1H chart ─────────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[1])
o1,h1,l1,c1 = sim_candles(entry*0.989, 24, trend=IWM_ATR*0.01, atr=IWM_ATR*0.6, seed=11)
c1=anchor(c1,entry); o1=anchor(o1,entry); h1=anchor(h1,entry); l1=anchor(l1,entry)
draw_candles(ax1, o1, h1, l1, c1)
sup1h = round(min(l1[8:18]), 2)
res1h = round(max(h1[6:16]), 2)
ax1.axhline(sup1h, color=BULL, ls='--', lw=1.1, label=f'1H Support  ${sup1h:.2f}')
ax1.axhline(res1h, color=BEAR, ls='--', lw=1.1, label=f'1H Resist   ${res1h:.2f}')
ax1.axhline(IWM_52WK_HI, color='#ce93d8', ls=':', lw=1.0, label=f'52wk High ${IWM_52WK_HI}')
ax1.axhspan(sup1h - IWM_ATR*0.1, sup1h + IWM_ATR*0.1, color='#26a69a15', zorder=0)
ax1.set_title('IWM  1H  |  Key Levels', color=TEXT, fontsize=9.5, fontweight='bold', pad=6)
style(ax1)
ax1.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax1.set_xticks(range(0,24,4))
ax1.set_xticklabels([f'-{(23-i)}h' for i in range(0,24,4)], fontsize=6, color=MUTED)

# ── 15min entry chart ─────────────────────────────────────────────────────────
ax15 = fig.add_subplot(gs[2])
o15,h15,l15,c15 = sim_candles(entry*0.993, 32, trend=IWM_ATR*0.005, atr=IWM_ATR*0.35, seed=21)
c15=anchor(c15,entry); o15=anchor(o15,entry); h15=anchor(h15,entry); l15=anchor(l15,entry)
draw_candles(ax15, o15, h15, l15, c15)

ax15.axhline(entry,  color=ENTRY_C, ls='-',  lw=1.8, label=f'ENTRY  ${entry}',  zorder=5)
ax15.axhline(stop,   color=SL_C,   ls='--', lw=1.3, label=f'STOP   ${stop}',   zorder=5)
ax15.axhline(tp1,    color=TP1_C,  ls='--', lw=1.3, label=f'TP1    ${tp1}',    zorder=5)
ax15.axhline(tp2,    color=TP2_C,  ls='--', lw=1.3, label=f'TP2    ${tp2}',    zorder=5)
ax15.axhspan(stop, entry, color='#ef535015', zorder=0)
ax15.axhspan(entry, tp1,  color='#26a69a12', zorder=0)
ax15.axvspan(29.5, 31.5, color='#00e5ff10', zorder=0)
ax15.annotate('NOW', xy=(30.5, entry + IWM_ATR*0.2), color=ENTRY_C,
              fontsize=7.5, ha='center', fontweight='bold')
ax15.set_title(f'IWM  15min  |  Entry ${entry}  |  R:R {rr}:1',
               color=ENTRY_C, fontsize=9.5, fontweight='bold', pad=6)
style(ax15)
ax15.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, loc='upper left')
ax15.set_xticks(range(0,32,4))
ax15.set_xticklabels([f'-{(31-i)*15}m' for i in range(0,32,4)], fontsize=6, color=MUTED)

# ── trade card ───────────────────────────────────────────────────────────────
axc = fig.add_subplot(gs[3])
axc.set_facecolor(PANEL); axc.axis('off')
card = (
    f" IWM  CALL OPTION SETUP\n"
    f" {'─'*27}\n"
    f" Live Price  : ${IWM_PRICE}  ({IWM_PCT})\n"
    f" Change      : -${abs(IWM_CHANGE):.2f} today\n"
    f" Volume      : {IWM_VOLUME}\n"
    f" 52wk High   : ${IWM_52WK_HI}\n"
    f" ATR (14)    : ${IWM_ATR}\n\n"
    f" ── OPTION ───────────────────\n"
    f" Buy CALL  @ ~${opt_buy:.2f} premium\n"
    f" Strike      : $280  (OTM)\n"
    f" DTE         : 7–14 days\n\n"
    f" ── LEVELS ───────────────────\n"
    f" Entry       : ${entry}\n"
    f" Stop Loss   : ${stop}\n"
    f"   Risk      : -${round(entry-stop,2)} per share\n"
    f" Take Profit1: ${tp1}\n"
    f"   (near 52wk high ${IWM_52WK_HI})\n"
    f"   Gain      : +${round(tp1-entry,2)} per share\n"
    f" Take Profit2: ${tp2}\n"
    f"   Gain      : +${round(tp2-entry,2)} per share\n\n"
    f" Sell CALL @ ~${opt_sell:.2f}\n"
    f" R:R Ratio   : {rr}:1\n\n"
    f" ── CAUTION ──────────────────\n"
    f" Price near key resistance\n"
    f" ${IWM_RESIST} & 52wk high ${IWM_52WK_HI}\n"
    f" Wait for 4H breakout confirm\n"
    f" before entering call"
)
axc.text(0.03, 0.97, card, transform=axc.transAxes, fontsize=8.2,
         color=TEXT, va='top', fontfamily='monospace',
         bbox=dict(facecolor='#21262d', edgecolor='#ffa726', lw=1.8, pad=9))
axc.set_title('IWM  Trade Card', color=TEXT, fontsize=10, fontweight='bold')

fig.text(0.5, 0.01,
    '⚠  Live price $278.63 from screenshot  |  Support/Resist from Barchart  |  '
    'Candlesticks illustrative  |  NOT financial advice',
    ha='center', fontsize=7.5, color='#ef5350', style='italic')

out = '/home/user/myprojects/iwm_live_chart.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
print(f"Saved → {out}")
