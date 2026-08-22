from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd,yfinance as yf
from stock_alpha_v2 import load_membership,fetch_prices

# Hard safety invariant: this engine can only generate paper portfolios.
real_orders=False
PAPER_ONLY=True

# Keep this exact assignment explicit so CI can mechanically verify the live-order kill switch.
assert real_orders is False

def signal(px,mem,asof,top_n=20):
    asof=pd.Timestamp(asof); hist=px.loc[:asof].iloc[:-1]
    if len(hist)<260: raise ValueError('insufficient history before signal date')
    current=px.loc[:asof].ffill(limit=2).iloc[-1]; eligible=[]
    for s in px.columns:
        m=mem[mem.symbol.eq(s)]
        if not m.empty and ((m.valid_from<=asof)&(m.valid_to.isna()|(m.valid_to>asof))).any() and pd.notna(current.get(s)): eligible.append(s)
    if len(eligible)<top_n: raise ValueError('insufficient PIT-eligible symbols with recent prices')
    h=hist[eligible]; p=h.iloc[-1]
    score=pd.concat([(p/h.iloc[-253]-1).rename('mom'),(p/h.iloc[-22]-1).rename('short'),(p/h.iloc[-201]-1).rename('trend'),(-h.pct_change().iloc[-63:].std()*np.sqrt(252)).rename('lowvol')],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    if len(score)<top_n: raise ValueError('insufficient factor observations')
    z=(score-score.mean())/score.std(ddof=0).replace(0,np.nan); z['score']=.4*z.mom+.2*z.short+.2*z.trend+.2*z.lowvol
    picks=list(z.score.nlargest(top_n).index); return picks,{s:1/top_n for s in picks},current

def risk_scale(px,picks,asof,benchmark):
    hist=px.loc[:asof,picks].iloc[:-1]
    if len(hist)<63: raise ValueError('insufficient risk history')
    port=hist.pct_change().mean(axis=1).dropna(); vol=float(port.iloc[-63:].std()*np.sqrt(252)); scale=1.0 if not np.isfinite(vol) or vol<=0 else float(np.clip(.18/vol,.25,1.0))
    idx=benchmark.loc[:asof].dropna()
    if len(idx)<200: raise ValueError('insufficient NIFTY regime history')
    bull=bool(idx.iloc[-1] >= idx.rolling(200).mean().iloc[-1])
    if not bull: scale=min(scale,.50)
    return scale,bull,vol

def main():
    if real_orders is not False or PAPER_ONLY is not True: raise RuntimeError('paper-only safety invariant violated')
    ap=argparse.ArgumentParser(); ap.add_argument('--membership',default='data/pit/index_membership_history.csv'); ap.add_argument('--out',default='data/paper_trade_v2'); ap.add_argument('--asof',default=None); a=ap.parse_args()
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True); mem=load_membership(a.membership); symbols=sorted(mem.symbol.unique()); end=(pd.Timestamp.now(tz='UTC').tz_localize(None)+pd.Timedelta(days=1)).strftime('%Y-%m-%d'); px=fetch_prices(symbols,'2014-01-01',end)
    if px.empty: raise RuntimeError('no price data')
    asof=pd.Timestamp(a.asof) if a.asof else pd.Timestamp(px.index.max());
    if asof not in px.index: asof=px.index[px.index<=asof].max()
    picks,w,current=signal(px,mem,asof); bm=yf.download('^NSEI',start='2014-01-01',end=end,auto_adjust=True,progress=False)['Close']; bm=bm.iloc[:,0] if isinstance(bm,pd.DataFrame) else bm; scale,bull,vol=risk_scale(px,picks,asof,bm)
    portfolio=pd.DataFrame([{'symbol':s,'target_weight':w[s]*scale,'reference_price':float(current[s])} for s in sorted(picks)]); cash=float(1-scale)
    if len(portfolio)!=20 or portfolio.symbol.nunique()!=20: raise AssertionError('position constraint violated')
    if not np.isclose(portfolio.target_weight.sum()+cash,1.0): raise AssertionError('weights plus cash do not sum to 1')
    payload={'mode':'PAPER_ONLY','strategy':'Stock Alpha V2','asof':str(asof.date()),'execution_rule':'next available session; no same-session execution','positions':portfolio.to_dict('records'),'cash_weight':cash,'gross_exposure':scale,'regime_bull':bull,'estimated_63d_annualized_vol':vol,'real_orders':False,'rules_hash':hashlib.sha256(Path('trading/stock_alpha_v2.py').read_bytes()).hexdigest()}
    (out/'paper_portfolio.json').write_text(json.dumps(payload,indent=2)); portfolio.to_csv(out/'paper_portfolio.csv',index=False); print(json.dumps(payload,indent=2))
if __name__=='__main__': main()
