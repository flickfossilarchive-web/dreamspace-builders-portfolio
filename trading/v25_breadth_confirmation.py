import json
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import data

# V25 hypothesis locked ex-ante:
# Use broad-market participation (NIFTY 500 proxy) as an independent confirmation
# of NIFTY trend. It is a risk filter, not a return sleeve. No leverage.
COST = 0.0010
SLIPPAGE = 0.0010
TREND = 200
BREADTH_TREND = 200
RELATIVE_MOM = 126


def load_broad(start, end):
    # Yahoo's NIFTY 500 symbol is ^CRSLDX. Fail loudly rather than silently
    # substituting a survivorship-biased constituent basket.
    x = yf.download('^CRSLDX', start=start, end=end, auto_adjust=False, progress=False)
    if isinstance(x.columns, pd.MultiIndex):
        x = x.xs('^CRSLDX', axis=1, level=1)
    if 'Close' not in x or len(x) < 1000:
        raise RuntimeError('Insufficient NIFTY 500 history; refusing survivorship-biased fallback')
    x.index = pd.to_datetime(x.index).tz_localize(None)
    return x[['Close']].rename(columns={'Close': 'broad'})


def run(d, broad, cost=COST, slippage=SLIPPAGE, trend=TREND, breadth_trend=BREADTH_TREND, relative_mom=RELATIVE_MOM):
    n = d.Close.astype(float)
    tri = d.TRI.astype(float)
    b = broad.broad.reindex(d.index).ffill()
    ma_n = n.rolling(trend).mean()
    ma_b = b.rolling(breadth_trend).mean()
    rel = b.pct_change(relative_mom) - n.pct_change(relative_mom)
    nr = tri.pct_change().fillna(0)

    # State map: full exposure when NIFTY and broad market agree; only reduce
    # when both are genuinely weak. Neutral is a modest 90% risk state.
    w = 1.0
    eq = 1.0
    vals = []
    trades = 0
    turnover = 0.0
    exposures = []
    for i in range(1, len(d)):
        p = i - 1
        weekly = (i == 1 or d.index[i].isocalendar().week != d.index[i-1].isocalendar().week or d.index[i].year != d.index[i-1].year)
        if weekly and all(np.isfinite(x) for x in (ma_n.iloc[p], ma_b.iloc[p], rel.iloc[p])):
            n_up = n.iloc[p] > ma_n.iloc[p]
            b_up = b.iloc[p] > ma_b.iloc[p]
            rel_up = rel.iloc[p] > 0
            if n_up and b_up and rel_up:
                target = 1.00
            elif (not n_up) and (not b_up) and (not rel_up):
                target = 0.70
            else:
                target = 0.90
            if abs(target - w) >= 0.05:
                t = abs(target - w)
                turnover += t
                eq *= max(0.0, 1.0 - t * (cost + slippage))
                w = target
                trades += 1
        eq *= 1.0 + w * nr.iloc[i]
        vals.append((d.index[i], eq))
        exposures.append(w)

    s = pd.Series(dict(vals)).sort_index()
    rr = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return s, {
        'cagr': float(s.iloc[-1] ** (1 / yrs) - 1),
        'total_return': float(s.iloc[-1] - 1),
        'max_drawdown': float((s / s.cummax() - 1).min()),
        'sharpe': float(rr.mean() / rr.std() * np.sqrt(252)),
        'trades': trades,
        'turnover': turnover,
        'avg_nifty_weight': float(np.mean(exposures)),
    }


def metrics(x):
    x = x.dropna()
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    rr = x.pct_change().dropna()
    return {
        'cagr': float((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1),
        'max_drawdown': float((x / x.cummax() - 1).min()),
        'sharpe': float(rr.mean() / rr.std() * np.sqrt(252)),
    }


def main():
    d = data()
    broad = load_broad(str(d.index[0].date()), str((d.index[-1] + pd.Timedelta(days=1)).date()))
    d = d.join(broad, how='inner').dropna()
    tri = d.TRI
    yrs = (tri.index[-1] - tri.index[0]).days / 365.25
    bench = float((tri.iloc[-1] / tri.iloc[0]) ** (1 / yrs) - 1)

    base_s, base = run(d, broad)
    costs = {str(int(c * 10000)): run(d, broad, cost=c, slippage=c)[1] for c in [0, .0005, .001, .0015, .002, .003, .004, .005]}
    perturbations = {}
    for name, tr, bt, rm in [
        ('trend150', 150, 200, 126), ('trend250', 250, 200, 126),
        ('breadth150', 200, 150, 126), ('breadth250', 200, 250, 126),
        ('rel90', 200, 200, 90), ('rel180', 200, 200, 180),
        ('rel60', 150, 150, 60), ('all_long', 9999, 9999, 126),
    ]:
        if name == 'all_long':
            perturbations[name] = {'cagr': bench, 'max_drawdown': float((tri / tri.cummax() - 1).min()), 'sharpe': float(tri.pct_change().dropna().mean() / tri.pct_change().dropna().std() * np.sqrt(252)), 'trades': 0, 'turnover': 0.0, 'avg_nifty_weight': 1.0}
        else:
            perturbations[name] = run(d, broad, trend=tr, breadth_trend=bt, relative_mom=rm)[1]

    windows = [
        ('2008-2012', '2008-01-01', '2012-12-31'),
        ('2013-2017', '2013-01-01', '2017-12-31'),
        ('2018-2021', '2018-01-01', '2021-12-31'),
        ('2022-present', '2022-01-01', str(d.index[-1].date())),
    ]
    wf = []
    for name, a, b in windows:
        x = base_s.loc[a:b]
        if len(x) > 50:
            wf.append({'name': name, **metrics(x)})

    out = {
        'strategy': 'V25 NIFTY trend with NIFTY 500 breadth/relative-strength confirmation',
        'benchmark_cagr': bench,
        'base': base,
        'cost_sensitivity': costs,
        'parameter_perturbations': perturbations,
        'walk_forward': wf,
        'rules': {
            'risk_on': 'NIFTY > MA200 AND NIFTY500 > MA200 AND NIFTY500 126d relative momentum vs NIFTY > 0 => 100%',
            'risk_off': 'all three conditions negative => 70%',
            'neutral': 'otherwise => 90%',
            'rebalance': 'weekly thresholded',
            'signals': 'previous session only',
            'leverage': 'none',
            'breadth_proxy': 'NIFTY 500 index, not current constituents',
        },
        'gate': {
            'cost_bps_primary': 20,
            'required_base_cagr_gt_benchmark': True,
            'required_20bps_cagr_gt_benchmark': True,
            'required_all_perturbations_positive': True,
            'required_all_walk_forward_positive': True,
            'required_sharpe_ge': 0.80,
            'required_max_dd_better_than': -0.30,
        },
    }
    json.dump(out, open('v25_results.json', 'w'), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
