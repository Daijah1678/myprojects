import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TICKERS = ['SPY', 'NVDA', 'AAPL']
BG      = '#0d1117'
PANEL   = '#161b22'
TEXT    = '#e6edf3'
MUTED   = '#8b949e'
BORDER  = '#30363d'
BULL    = '#26a69a'
BEAR    = '#ef5350'
ENTRY   = '#00e5ff'
SL_C    = '#ef5350'
TP1_C   = '#66bb6a'
TP2_C   = '#ffa726'


def fetch(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    df.dropna(inplace=True)
    # flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def draw_candles(ax, df, max_bars=60):
    df = df.tail(max_bars).copy()
    df.reset_index(inplace=True)
    xs = range(len(df))
    for i, row in enumerate(df.itertuples()):
        bull = row.Close >= row.Open
        c    = BULL if bull else BEAR
        ax.plot([i, i], [row.Low, row.High], color=c, lw=0.9, zorder=2)
        ax.add_patch(mpatches.FancyBboxPatch(
            (i - 0.35, min(row.Open, row.Close)),
            0.7, max(abs(row.Close - row.Open), 0.01),
            boxstyle="square,pad=0", fc=c, ec=c, zorder=3
        ))
    return df


def style_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.set_title(title, color=TEXT, fontsize=9, fontweight='bold', pad=5)
    ax.yaxis.tick_right()


def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()


def trade_levels(df):
    close  = df['Close'].iloc[-1]
    recent_low = df['Low'].tail(10).min()
    atr    = (df['High'] - df['Low']).tail(14).mean()
    entry  = round(float(close), 2)
    stop   = round(float(entry - atr * 1.2), 2)
    tp1    = round(float(entry + atr * 2.0), 2)
    tp2    = round(float(entry + atr * 3.5), 2)
    return entry, stop, tp1, tp2


# ── fetch live data ──────────────────────────────────────────────────────────
print("Fetching live data from Yahoo Finance…")
data = {}
for t in TICKERS:
    data[t] = {
        '4h':  fetch(t, '60d',  '1h'),   # use 1h and resample to 4h
        '1h':  fetch(t, '5d',   '1h'),
        '15m': fetch(t, '2d',   '15m'),
    }
    # resample 1h → 4h
    df1h = data[t]['4h']
    df4h = df1h.resample('4h').agg(
        {'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}
    ).dropna()
    data[t]['4h'] = df4h

now_str = datetime.now().strftime('%Y-%m-%d  %H:%M UTC')
print(f"Data fetched at {now_str}")

# ── build figure ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 15), facecolor=BG)
fig.suptitle(
    f'4H → 1H → 15min  Options Method  |  Live Yahoo Finance Data  |  {now_str}',
    fontsize=13, color=TEXT, fontweight='bold', y=0.99
)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.3)

for row_idx, ticker in enumerate(TICKERS):
    df4  = data[ticker]['4h']
    df1  = data[ticker]['1h']
    df15 = data[ticker]['15m']

    entry, stop, tp1, tp2 = trade_levels(df15)
    current_price = round(float(df15['Close'].iloc[-1]), 2)

    # ── 4H panel ────────────────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[row_idx, 0])
    drawn4 = draw_candles(ax4, df4, max_bars=40)
    e50 = ema(drawn4['Close'], 10)   # ~50-period on 4h = 10 bars shown
    ax4.plot(range(len(drawn4)), e50, color='#ffa726', lw=1, label='50 EMA')
    bias = 'Bullish ▲' if drawn4['Close'].iloc[-1] > e50.iloc[-1] else 'Bearish ▼'
    bias_col = BULL if 'Bullish' in bias else BEAR
    ax4.set_title(f'{ticker}  4H  —  Bias: {bias}  |  ${current_price}',
                  color=bias_col, fontsize=9, fontweight='bold', pad=5)
    style_ax(ax4, '')
    ax4.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
               labelcolor=TEXT, loc='upper left')

    # ── 1H panel ────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[row_idx, 1])
    drawn1 = draw_candles(ax1, df1, max_bars=24)
    support = drawn1['Low'].tail(12).min()
    resist  = drawn1['High'].tail(12).max()
    ax1.axhline(support, color='#26a69a', ls='--', lw=1, label=f'Support ${support:.2f}')
    ax1.axhline(resist,  color='#ef5350', ls='--', lw=1, label=f'Resist  ${resist:.2f}')
    ax1.axhspan(support - support*0.002, support + support*0.002,
                color='#26a69a18', zorder=0)
    style_ax(ax1, f'{ticker}  1H  —  Key Levels')
    ax1.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
               labelcolor=TEXT, loc='upper left')

    # ── 15min ENTRY panel ───────────────────────────────────────────────────
    ax15 = fig.add_subplot(gs[row_idx, 2])
    drawn15 = draw_candles(ax15, df15, max_bars=30)
    n = len(drawn15)

    ax15.axhline(entry, color=ENTRY,  ls='-',  lw=1.5, label=f'Entry  ${entry}')
    ax15.axhline(stop,  color=SL_C,   ls='--', lw=1.2, label=f'Stop   ${stop}')
    ax15.axhline(tp1,   color=TP1_C,  ls='--', lw=1.2, label=f'TP1    ${tp1}')
    ax15.axhline(tp2,   color=TP2_C,  ls='--', lw=1.2, label=f'TP2    ${tp2}')

    rr = round((tp1 - entry) / max(entry - stop, 0.01), 1)

    # shaded zones
    ax15.axhspan(stop, entry, color='#ef535015', zorder=0)
    ax15.axhspan(entry, tp1,  color='#26a69a15', zorder=0)

    ax15.set_title(
        f'{ticker}  15min  —  Entry ${entry}  |  R:R {rr}:1',
        color=ENTRY, fontsize=9, fontweight='bold', pad=5
    )
    style_ax(ax15, '')
    ax15.legend(fontsize=6, facecolor=PANEL, edgecolor=BORDER,
                labelcolor=TEXT, loc='upper left')

# ── footer ───────────────────────────────────────────────────────────────────
fig.text(0.5, 0.002,
         '⚠  Live data via Yahoo Finance  |  For educational purposes only  |  Not financial advice  |  Verify before trading',
         ha='center', fontsize=8, color='#ef5350', style='italic')

out = '/home/user/myprojects/live_options_chart.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
print(f"Chart saved → {out}")
