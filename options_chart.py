import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

fig = plt.figure(figsize=(18, 14), facecolor='#0d1117')
fig.suptitle(
    '4H → 1H → 15min Options Trading Method  |  Educational Example Only',
    fontsize=15, color='white', fontweight='bold', y=0.98
)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# ── shared candle helper ─────────────────────────────────────────────────────
def draw_candles(ax, opens, highs, lows, closes, width=0.4):
    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        color = '#26a69a' if c >= o else '#ef5350'
        ax.plot([i, i], [l, h], color=color, linewidth=1.2)
        ax.add_patch(mpatches.FancyBboxPatch(
            (i - width/2, min(o, c)), width, abs(c - o),
            boxstyle="square,pad=0", facecolor=color, edgecolor=color
        ))

def style_ax(ax, title):
    ax.set_facecolor('#161b22')
    ax.tick_params(colors='#8b949e', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363d')
    ax.set_title(title, color='#e6edf3', fontsize=10, fontweight='bold', pad=6)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position('right')

# ── colour constants ─────────────────────────────────────────────────────────
ENTRY   = '#00e5ff'
SL      = '#ef5350'
TP1     = '#66bb6a'
TP2     = '#ffa726'
ZONE    = '#ffa72620'

# ════════════════════════════════════════════════════════════════════════════
# STOCK 1 — SPY  (top row, all 3 timeframes)
# ════════════════════════════════════════════════════════════════════════════
spy_base = 528.0

# --- 4H ---
ax1 = fig.add_subplot(gs[0, 0])
np.random.seed(1)
o4 = [spy_base + np.random.uniform(-3, 3) for _ in range(12)]
c4 = [o + np.random.uniform(-4, 5) for o in o4]
h4 = [max(o, c) + np.random.uniform(0.5, 2) for o, c in zip(o4, c4)]
l4 = [min(o, c) - np.random.uniform(0.5, 2) for o, c in zip(o4, c4)]
# force bullish trend
for i in range(12):
    c4[i] = spy_base - 6 + i * 1.1 + np.random.uniform(-1, 1)
    o4[i] = c4[i] + np.random.uniform(-2, 2)
    h4[i] = max(o4[i], c4[i]) + np.random.uniform(0.3, 1.5)
    l4[i] = min(o4[i], c4[i]) - np.random.uniform(0.3, 1.5)

draw_candles(ax1, o4, h4, l4, c4)
support4 = spy_base - 2
ax1.axhline(support4, color='#ffa726', linestyle='--', linewidth=1, label='4H Support')
ax1.axhspan(support4 - 1, support4 + 1, color=ZONE, zorder=0)
style_ax(ax1, 'SPY  |  4H  —  Establish Bias (Bullish)')
ax1.set_xticks(range(12))
ax1.set_xticklabels([f'd{i+1}' for i in range(12)], fontsize=7, color='#8b949e')
ax1.legend(fontsize=7, facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3', loc='upper left')

# --- 1H ---
ax2 = fig.add_subplot(gs[0, 1])
np.random.seed(2)
base1h = c4[-3]
c1 = [base1h + np.random.uniform(-1, 1.5) * (1 + i*0.05) for i in range(16)]
o1 = [c - np.random.uniform(-1.5, 1.5) for c in c1]
h1 = [max(o, c) + np.random.uniform(0.2, 1) for o, c in zip(o1, c1)]
l1 = [min(o, c) - np.random.uniform(0.2, 1) for o, c in zip(o1, c1)]

draw_candles(ax2, o1, h1, l1, c1)
support1h = min(l1[8:12])
ax2.axhline(support1h, color='#ffa726', linestyle='--', linewidth=1, label='1H Key Level')
ax2.axhspan(support1h - 0.5, support1h + 0.5, color=ZONE, zorder=0)
style_ax(ax2, 'SPY  |  1H  —  Confirm Levels')
ax2.set_xticks(range(16))
ax2.set_xticklabels([f'h{i+1}' for i in range(16)], fontsize=6, color='#8b949e')
ax2.legend(fontsize=7, facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3', loc='upper left')

# --- 15min ENTRY ---
ax3 = fig.add_subplot(gs[0, 2])
np.random.seed(3)
entry_price = support1h + 0.4
sl_price    = entry_price - 1.80
tp1_price   = entry_price + 2.50
tp2_price   = entry_price + 4.80

c15 = [support1h + 2 - np.random.uniform(0, 0.8) for _ in range(6)] + \
      [support1h + np.random.uniform(-0.3, 0.3) for _ in range(4)] + \
      [entry_price + i * 0.6 + np.random.uniform(-0.2, 0.2) for i in range(10)]
o15 = [c + np.random.uniform(-0.5, 0.5) for c in c15]
h15 = [max(o, c) + np.random.uniform(0.1, 0.5) for o, c in zip(o15, c15)]
l15 = [min(o, c) - np.random.uniform(0.1, 0.5) for o, c in zip(o15, c15)]

draw_candles(ax3, o15, h15, l15, c15)
ax3.axhline(entry_price, color=ENTRY, linestyle='-',  linewidth=1.5, label=f'ENTRY  ~${entry_price:.2f}')
ax3.axhline(sl_price,    color=SL,    linestyle='--', linewidth=1.2, label=f'STOP   ~${sl_price:.2f}')
ax3.axhline(tp1_price,   color=TP1,   linestyle='--', linewidth=1.2, label=f'TP1    ~${tp1_price:.2f}')
ax3.axhline(tp2_price,   color=TP2,   linestyle='--', linewidth=1.2, label=f'TP2    ~${tp2_price:.2f}')
ax3.axvspan(9, 10, color='#00e5ff15', zorder=0)
ax3.annotate('Entry\nCandle', xy=(9.5, entry_price), color=ENTRY,
             fontsize=7, ha='center', va='bottom')
style_ax(ax3, 'SPY  |  15min  —  Entry Trigger')
ax3.set_xticks(range(20))
ax3.set_xticklabels([f'{i+1}' for i in range(20)], fontsize=6, color='#8b949e')
ax3.legend(fontsize=7, facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3', loc='upper left')

# ════════════════════════════════════════════════════════════════════════════
# STOCK 2 — NVDA  (bottom left: summary trade card)
# ════════════════════════════════════════════════════════════════════════════
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor('#161b22')
ax4.axis('off')

nvda_entry = 118.50
nvda_sl    = 116.20
nvda_tp1   = 121.80
nvda_tp2   = 125.00
nvda_option_buy  = 3.40   # example call premium
nvda_option_sell = 6.80

card_text = (
    "NVDA  |  CALL OPTION SETUP\n"
    "──────────────────────────────\n"
    f"4H Bias      :  Bullish (above 50 EMA)\n"
    f"1H Level     :  Support @ ${nvda_entry:.2f} zone\n"
    f"15min Trigger:  Rejection hammer candle\n\n"
    f"  BUY CALL  @  ~${nvda_option_buy:.2f} premium\n"
    f"  Strike       :  $120  |  1–2 wk DTE\n\n"
    f"  Entry (stock):  ${nvda_entry:.2f}\n"
    f"  Stop Loss    :  ${nvda_sl:.2f}  (-${nvda_entry - nvda_sl:.2f})\n"
    f"  Take Profit 1:  ${nvda_tp1:.2f}  (+${nvda_tp1 - nvda_entry:.2f})\n"
    f"  Take Profit 2:  ${nvda_tp2:.2f}  (+${nvda_tp2 - nvda_entry:.2f})\n\n"
    f"  SELL CALL    :  ~${nvda_option_sell:.2f}  (~2x premium)\n"
    f"  R:R Ratio    :  2 : 1"
)
ax4.text(0.05, 0.95, card_text, transform=ax4.transAxes,
         fontsize=9, color='#e6edf3', va='top', fontfamily='monospace',
         bbox=dict(facecolor='#21262d', edgecolor='#00e5ff', linewidth=1.5, pad=10))
ax4.set_title('NVDA  |  Trade Card  (Illustrative)', color='#e6edf3',
              fontsize=10, fontweight='bold')

# ════════════════════════════════════════════════════════════════════════════
# STOCK 3 — AAPL  (bottom middle: summary trade card)
# ════════════════════════════════════════════════════════════════════════════
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor('#161b22')
ax5.axis('off')

aapl_entry = 211.00
aapl_sl    = 208.50
aapl_tp1   = 215.00
aapl_tp2   = 219.50
aapl_option_buy  = 2.80
aapl_option_sell = 5.60

card_text2 = (
    "AAPL  |  CALL OPTION SETUP\n"
    "──────────────────────────────\n"
    f"4H Bias      :  Bullish (trending up)\n"
    f"1H Level     :  Support @ ${aapl_entry:.2f} zone\n"
    f"15min Trigger:  Bullish engulfing candle\n\n"
    f"  BUY CALL  @  ~${aapl_option_buy:.2f} premium\n"
    f"  Strike       :  $212.50  |  1–2 wk DTE\n\n"
    f"  Entry (stock):  ${aapl_entry:.2f}\n"
    f"  Stop Loss    :  ${aapl_sl:.2f}  (-${aapl_entry - aapl_sl:.2f})\n"
    f"  Take Profit 1:  ${aapl_tp1:.2f}  (+${aapl_tp1 - aapl_entry:.2f})\n"
    f"  Take Profit 2:  ${aapl_tp2:.2f}  (+${aapl_tp2 - aapl_entry:.2f})\n\n"
    f"  SELL CALL    :  ~${aapl_option_sell:.2f}  (~2x premium)\n"
    f"  R:R Ratio    :  2 : 1"
)
ax5.text(0.05, 0.95, card_text2, transform=ax5.transAxes,
         fontsize=9, color='#e6edf3', va='top', fontfamily='monospace',
         bbox=dict(facecolor='#21262d', edgecolor='#26a69a', linewidth=1.5, pad=10))
ax5.set_title('AAPL  |  Trade Card  (Illustrative)', color='#e6edf3',
              fontsize=10, fontweight='bold')

# ════════════════════════════════════════════════════════════════════════════
# Legend / Method Key  (bottom right)
# ════════════════════════════════════════════════════════════════════════════
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor('#161b22')
ax6.axis('off')

method_text = (
    "METHOD KEY  (4H → 1H → 15min)\n"
    "──────────────────────────────\n"
    "STEP 1  —  4H Chart\n"
    "  • Is price above/below 50 EMA?\n"
    "  • Mark major swing highs & lows\n"
    "  • Confirm overall bias direction\n\n"
    "STEP 2  —  1H Chart\n"
    "  • Identify key S/R levels\n"
    "  • Wait for price to reach zone\n"
    "  • Confirm trend alignment\n\n"
    "STEP 3  —  15min Chart\n"
    "  • Watch for rejection candle\n"
    "  • Enter option on confirmation\n"
    "  • Set stop below swing low\n\n"
    "EXIT RULES\n"
    "  • TP1: Sell 50% at 1H resistance\n"
    "  • TP2: Trail stop on remaining\n"
    "  • Exit ALL if 4H bias breaks\n\n"
    "⚠  EDUCATIONAL ONLY — NOT FINANCIAL ADVICE"
)
ax6.text(0.05, 0.97, method_text, transform=ax6.transAxes,
         fontsize=8.5, color='#e6edf3', va='top', fontfamily='monospace',
         bbox=dict(facecolor='#21262d', edgecolor='#ffa726', linewidth=1.5, pad=10))
ax6.set_title('Method Reference', color='#e6edf3', fontsize=10, fontweight='bold')

# ── watermark ────────────────────────────────────────────────────────────────
fig.text(0.5, 0.01,
         '⚠  ILLUSTRATIVE PRICES ONLY — Verify live prices on TradingView & Yahoo Finance before trading',
         ha='center', fontsize=9, color='#ef5350', style='italic')

plt.savefig('/home/user/myprojects/options_trading_chart.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
print("Chart saved.")
