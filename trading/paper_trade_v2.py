from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from stock_alpha_v2 import load_membership,fetch_prices

def signal(px,mem,asof,top_n=20):
    hist=px.loc[:asof].iloc[:-1]
    if len(hist)<260: raise ValueError('insufficient history before signal date')
    eligible=[]
    for s in px.columns:
        m=mem[mem.symbol.eq(s)]
        if not m.empty and ((m.valid_from<=asof)&(m.valid_to.isna()|(m.valid_to>asof))).any(): eligible.append(s)
    if len(eligible)<top_n: raise ValueError('insufficient PIT-eligible symbols')
    h=hist[eligible]; p=h.iloc[-1]
    score=pd.concat([(p/h.iloc[-253]-1).rename('mom'),(p/h.iloc[-22]-1).rename('short'),(p/h.iloc[-201]-1).rename('trend'),(-h.pct_change().iloc[-63:].std()*np.sqrt(252)).rename('lowvol')],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    if len(score)<top_n: raise ValueError('insufficient factor observations')
    z=(score-score.mean())/score.std(ddof=0).replace(0,np.nan);z['score']=.4*z.mom+.2*z.short+.2*z.trend+.2*z.lowvol
    picks=list(z.score.nlargest(top_n).index)
    w={s:1/top_n for s in picks}
    return picks,w

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--membership',default='data/pit/index_membership_history.csv');ap.add_argument('--out',default='data/paper_trade_v2');ap.add_argument('--asof',default=None);a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    mem=load_membership(a.membership);symbols=sorted(mem.symbol.unique());px=fetch_prices(symbols,'2014-01-01',pd.Timestamp.utcnow().strftime('%Y-%m-%d'))
    if px.empty: raise RuntimeError('no price data')
    asof=pd.Timestamp(a.asof) if a.asof else px.index.max()
    # Signals are generated strictly from data available before asof.
    picks,w=signal(px,mem,asof)
    latest=px.loc[:asof].iloc[-1]
    rows=[]
    for s in picks:
        if pd.isna(latest.get(s)): raise RuntimeError(f'missing execution reference price: {s}')
        rows.append({'symbol':s,'target_weight':w[s],'reference_price':float(latest[s])})
    portfolio=pd.DataFrame(rows).sort_values('symbol')
    if not np.isclose(portfolio.target_weight.sum(),1.0): raise AssertionError('weights do not sum to 1')
    if len(portfolio)!=20 or portfolio.symbol.nunique()!=20: raise AssertionError('position constraint violated')
    payload={'mode':'PAPER_ONLY','strategy':'Stock Alpha V2','asof':str(asof.date()),'execution_rule':'next available session; no same-session execution','positions':portfolio.to_dict('records'),'cash_weight':0.0,'real_orders':False,'rules_hash':hashlib.sha256(Path('trading/stock_alpha_v2.py').read_bytes()).hexdigest()}
    (out/'paper_portfolio.json').write_text(json.dumps(payload,indent=2));(out/'paper_portfolio.csv').write_text(portfolio.to_csv(index=False));print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
