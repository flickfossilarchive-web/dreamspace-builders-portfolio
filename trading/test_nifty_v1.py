import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

TICKER = '^NSEI'
START = '2007-09-17'
END = None
COST = 0.0005       # 5 bps per traded notional
SLIPPAGE = 0.0005   # 5 bps adverse execution
INITIAL_CAPITAL = 1.0


@dataclass
class BacktestResult:
    equity: pd.Series
    cagr: float
    total_return: float
    max_drawdown: float
    sharpe: float
    trades: int
    turnover: float
    trade_log: list


def load_data():
    d = yf.download(TICKER, start=START, end=END, auto_adjust=False, progress=False)
    if isinstance(d.columns, pd.MultiIndex):
        d = d.xs(TICKER, axis=1, level=1)
    d = d[['Open', 'High', 'Low', 'Close']].dropna().copy()
    d.index = pd.to_datetime(d.index).tz_localize(None)
    d = d[~d.index.duplicated(keep='first')].sort_index()
    if not d.index.is_monotonic_increasing:
        raise AssertionError('Price index is not sorted')
    if (d[['Open', 'High', 'Low', 'Close']] <= 0).any().any():
        raise AssertionError('Non-positive OHLC value detected')
    if (d.High < d.Low).any():
        raise AssertionError('High < Low detected')
    return d


def indicators(d):
    c, h = d.Close.astype(float), d.High.astype(float)
    l = d.Low.astype(float)
    sma50 = c.rolling(50, min_periods=50).mean()
    sma200 = c.rolling(200, min_periods=200).mean()
    mom126 = c.pct_change(126)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr20 = tr.rolling(20, min_periods=20).mean()
    return sma50, sma200, mom126, atr20


def target_exposure(prev_close, prev50, prev200, prev_mom):
    # Signal is formed only from the completed prior bar.
    if not np.isfinite(prev50 + prev200 + prev_mom):
        return 0.0
    if prev_close > prev200 and prev50 > prev200 and prev_mom > 0:
        return 1.0
    if prev_close > prev200:
        return 0.5
    return 0.0


def _trade_to_target(cash, shares, target_value, open_px):
    """Rebalance at the next open with explicit cost and slippage; never use leverage."""
    portfolio = cash + shares * open_px
    target_value = max(0.0, min(float(target_value), portfolio))
    target_shares = target_value / (open_px * (1 + COST + SLIPPAGE))

    # Sell first so cash is available for buys. Sale price includes slippage/cost.
    if target_shares < shares:
        sell_shares = shares - target_shares
        sell_px = open_px * (1 - SLIPPAGE)
        cash += sell_shares * sell_px * (1 - COST)
        shares = target_shares

    # Buy with available cash. The denominator includes both slippage and cost.
    if target_shares > shares:
        buy_px = open_px * (1 + SLIPPAGE)
        affordable = cash / (buy_px * (1 + COST)) if cash > 0 else 0.0
        buy_shares = min(target_shares - shares, affordable)
        cash -= buy_shares * buy_px * (1 + COST)
        shares += buy_shares

    return cash, shares


def backtest(d, start=None, end=None):
    # Indicators are calculated on the complete series before slicing, so OOS windows
    # retain the correct historical warm-up instead of accidentally resetting at a split.
    sma50, sma200, mom126, atr20 = indicators(d)
    idx = d.index
    mask = pd.Series(True, index=idx)
    if start is not None:
        mask &= idx >= pd.Timestamp(start)
    if end is not None:
        mask &= idx <= pd.Timestamp(end)
    dates = idx[mask]
    if len(dates) < 2:
        raise ValueError('Backtest window is too short')

    cash = INITIAL_CAPITAL
    shares = 0.0
    stop = np.nan
    equity_rows = []
    trades = []
    turnover = 0.0
    entry_date = None
    entry_value = None

    # Start from the first requested date. Decisions for date i use i-1 only.
    first_pos = idx.get_loc(dates[0])
    for i in range(max(1, first_pos), len(idx)):
        date = idx[i]
        if date not in dates:
            continue
        prev = i - 1
        prev_close = float(d.Close.iloc[prev])
        prev50 = float(sma50.iloc[prev])
        prev200 = float(sma200.iloc[prev])
        prev_mom = float(mom126.iloc[prev])
        prev_atr = float(atr20.iloc[prev])
        open_px = float(d.Open.iloc[i])
        low_px = float(d.Low.iloc[i])
        close_px = float(d.Close.iloc[i])

        target = target_exposure(prev_close, prev50, prev200, prev_mom)
        current_value_at_open = cash + shares * open_px

        # Update trailing stop from yesterday's completed bar. If the market gaps below
        # the stop, exit at the open; otherwise exit at the stop price.
        stop_triggered = False
        if shares > 0 and np.isfinite(prev_atr):
            candidate = prev_close - 3.0 * prev_atr
            stop = candidate if not np.isfinite(stop) else max(stop, candidate)
            if low_px <= stop:
                stop_triggered = True
                target = 0.0

        if stop_triggered:
            exit_px = open_px * (1 - SLIPPAGE) if open_px < stop else stop * (1 - SLIPPAGE)
            proceeds = shares * exit_px * (1 - COST)
            turnover += shares * open_px
            cash += proceeds
            shares = 0.0
            stop = np.nan
            if entry_date is not None:
                trades.append({
                    'entry': str(entry_date.date()),
                    'exit': str(date.date()),
                    'return': float(cash / entry_value - 1.0),
                    'reason': 'stop',
                })
                entry_date = None
                entry_value = None
        else:
            before = cash + shares * open_px
            cash, shares = _trade_to_target(cash, shares, target * before, open_px)
            after = cash + shares * open_px
            turnover += abs(after - before)

            if target > 0 and entry_date is None and shares > 0:
                entry_date = date
                entry_value = after
                if np.isfinite(prev_atr):
                    stop = open_px * (1 - SLIPPAGE) - 3.0 * prev_atr
            elif target == 0 and shares == 0 and entry_date is not None:
                trades.append({
                    'entry': str(entry_date.date()),
                    'exit': str(date.date()),
                    'return': float(cash / entry_value - 1.0),
                    'reason': 'signal',
                })
                entry_date = None
                entry_value = None
                stop = np.nan

        total = cash + shares * close_px
        if not np.isfinite(total) or total < -1e-12:
            raise AssertionError(f'Invalid equity on {date}: {total}')
        equity_rows.append((date, total))

    eq = pd.Series(dict(equity_rows)).sort_index()
    if len(eq) < 2:
        raise ValueError('No equity observations produced')
    dr = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = eq.iloc[-1] ** (1 / years) - 1 if years > 0 and eq.iloc[-1] > 0 else -1.0
    dd = (eq / eq.cummax() - 1).min()
    sharpe = dr.mean() / dr.std() * np.sqrt(252) if dr.std() > 0 else 0.0
    return BacktestResult(eq, float(cagr), float(eq.iloc[-1] / INITIAL_CAPITAL - 1),
                          float(dd), float(sharpe), len(trades), float(turnover), trades)


def buy_hold(d):
    c = d.Close.astype(float)
    r = c.iloc[-1] / c.iloc[0] - 1
    years = (c.index[-1] - c.index[0]).days / 365.25
    return {'total_return': float(r), 'cagr': float((1 + r) ** (1 / years) - 1)}


def synthetic_sanity():
    """Deterministic tests for accounting, no-leverage, and no-lookahead invariants."""
    dates = pd.bdate_range('2020-01-01', periods=500)
    trend = np.linspace(100, 220, len(dates))
    d = pd.DataFrame({'Open': trend, 'High': trend * 1.01, 'Low': trend * 0.99, 'Close': trend}, index=dates)
    r = backtest(d)
    assert np.isfinite(r.equity).all()
    assert (r.equity > 0).all()
    assert r.equity.iloc[-1] > r.equity.iloc[0]

    # Future-data mutation test: changing the last bar cannot alter any prior equity value.
    d2 = d.copy()
    d2.iloc[-1, d2.columns.get_loc('Close')] *= 10
    r2 = backtest(d2)
    common = r.equity.index.intersection(r2.equity.index)
    assert np.allclose(r.equity.loc[common[:-1]], r2.equity.loc[common[:-1]], rtol=0, atol=1e-12)
    return True


def main():
    synthetic_sanity()
    d = load_data()
    full = backtest(d)
    bh = buy_hold(d)

    # Independent chronological validation windows. The engine retains indicator history
    # from the full dataset while evaluating only the stated period.
    windows = [
        ('2010-01-01', '2014-12-31'),
        ('2015-01-01', '2019-12-31'),
        ('2020-01-01', str(d.index[-1].date())),
    ]
    oos = []
    for a, b in windows:
        if pd.Timestamp(a) <= d.index[-1]:
            r = backtest(d, a, b)
            oos.append({
                'start': a, 'end': b, 'cagr': r.cagr,
                'total_return': r.total_return,
                'max_drawdown': r.max_drawdown,
                'sharpe': r.sharpe,
                'trades': r.trades,
                'turnover': r.turnover,
            })

    result = {
        'strategy': 'NIFTY 50 regime + momentum + ATR risk control V1 (fixed engine)',
        'ticker': TICKER,
        'data_start': str(d.index[0].date()),
        'data_end': str(d.index[-1].date()),
        'execution': 'prior completed daily bar decisions; next-open execution',
        'accounting': 'cash + shares marked to close; explicit transaction cost and slippage; no leverage',
        'cost': COST,
        'slippage': SLIPPAGE,
        'full': {
            'cagr': full.cagr,
            'total_return': full.total_return,
            'max_drawdown': full.max_drawdown,
            'sharpe': full.sharpe,
            'trades': full.trades,
            'turnover': full.turnover,
        },
        'buy_and_hold_price_index': bh,
        'out_of_sample_windows': oos,
        'validation': {
            'synthetic_sanity': True,
            'future_data_mutation_test': True,
            'ohlc_integrity_checks': True,
            'positive_equity_check': True,
            'no_leverage': True,
        },
        'benchmark_note': 'NIFTY 50 TR is the proper investor benchmark because it includes dividends; this run uses ^NSEI price history, so TR comparison remains a separate requirement.',
    }
    json.dump(result, open('nifty_v1_results.json', 'w'), indent=2)
    pd.DataFrame({'date': full.equity.index.astype(str), 'equity': full.equity.values}).to_csv('nifty_v1_equity.csv', index=False)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
