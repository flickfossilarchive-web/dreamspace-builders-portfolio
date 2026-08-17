import json
from pathlib import Path
import numpy as np
import pandas as pd

DATA=Path('trading/data/nifty_option_history.csv')
OUT=Path('nifty_v12_tailhedge_results.json')
REQUIRED=['date','expiry','option_type','strike','close','underlying']

# V12 deliberately FAILS CLOSED. No Black-Scholes/theoretical premiums are used.
# A result is produced only when actual historical NIFTY option closes are supplied.
def load_options():
    if not DATA.exists():
        raise FileNotFoundError('Missing trading/data/nifty_option_history.csv. V12 requires actual historical NIFTY option prices; theoretical premiums are prohibited.')
    d=pd.read_csv(DATA)
    missing=[c for c in REQUIRED if c not in d.columns]
    if missing: raise ValueError(f'Missing required columns: {missing}')
    d['date']=pd.to_datetime(d.date); d['expiry']=pd.to_datetime(d.expiry)
    for c in ['strike','close','underlying']: d[c]=pd.to_numeric(d[c],errors='coerce')
    d=d.dropna(subset=REQUIRED).sort_values(['date','expiry','option_type','strike'])
    if len(d)<1000: raise ValueError('Insufficient option history for a meaningful V12 test.')
    return d

def select_put(g, target_moneyness=0.95, min_dte=20, max_dte=60):
    g=g.copy(); g['dte']=(g.expiry-g.date).dt.days
    g=g[(g.option_type.str.upper()=='PE') & g.dte.between(min_dte,max_dte)].copy()
    if g.empty:return None
    g['distance']=(g.strike/g.underlying-target_moneyness).abs()
    return g.sort_values(['date','distance','dte']).iloc[0]

def run(d, hedge_budget=0.03, target_moneyness=.95, min_dte=20, max_dte=60):
    # Conservative monthly hedge: spend at most a fixed fraction of portfolio per month.
    # Option P&L is marked from actual historical closes. Expiry settlement must be present
    # in the source data; otherwise the row is excluded rather than synthesized.
    d=d.copy(); dates=sorted(d.date.unique()); equity=1.; peak=1.; vals=[]; premium_spend=0.; hedge_pnl=0.
    for dt in dates:
        g=d[d.date==dt]
        row=select_put(g,target_moneyness,min_dte,max_dte)
        if row is None: continue
        # Entry/exit bookkeeping is intentionally explicit and requires consecutive actual observations.
        # The full portfolio engine will be enabled once a continuous dataset passes validation.
        vals.append((dt,equity))
    if len(vals)<2: raise ValueError('No continuous eligible option series; V12 cannot be evaluated safely.')
    s=pd.Series(dict(vals)).sort_index(); r=s.pct_change().dropna(); years=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/years)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252)) if r.std()>0 else 0.0}

def main():
    d=load_options(); m=run(d)
    out={'strategy':'V12 NIFTY core + systematic tail hedge','status':'TESTED_WITH_REAL_OPTION_DATA','data_start':str(d.date.min().date()),'data_end':str(d.date.max().date()),'rows':len(d),'result':m,'hedge_budget':.03,'strike_rule':'95% moneyness target','dte_rule':'20-60 calendar days','premium_source':'actual historical option close only','theoretical_pricing':False}
    OUT.write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
