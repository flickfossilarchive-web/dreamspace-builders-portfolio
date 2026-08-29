import json, math
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005; LOOKBACK=60; TREND_WINDOW=200
RISK_ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}; CASH='CASH'; CASH_TICKER='^IRX'
BASE_RISK={'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15}; RISK_CAPS={'NIFTY':0.70,'GOLD':0.30,'NASDAQ':0.25}
NORMAL_EXPOSURE=0.90; DEFENSIVE_EXPOSURE=0.60

def load(name,ticker):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data for {name} ({ticker})')
    if isinstance(d.columns,pd.MultiIndex):
        s=d['Close'] if 'Close' in d.columns.get_level_values(0) else d.xs('Close',axis=1,level=1)
        if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    else: s=d['Close']
    s=pd.to_numeric(s,errors='coerce').rename(name); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def load_cash():
    d=yf.download(CASH_TICKER,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data for CASH ({CASH_TICKER})')
    if isinstance(d.columns,pd.MultiIndex):
        s=d['Close'] if 'Close' in d.columns.get_level_values(0) else d.xs('Close',axis=1,level=1)
        if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    else: s=d['Close']
    s=pd.to_numeric(s,errors='coerce'); s.index=pd.to_datetime(s.index).tz_localize(None)
    rate=s.ffill().clip(lower=0)/100; daily=(1+rate)**(1/252)-1
    return (1+daily).cumprod().rename(CASH)

def data():
    p=pd.concat([load(n,t) for n,t in RISK_ASSETS.items()]+[load_cash()],axis=1).sort_index()
    coverage={c:int(p[c].notna().sum()) for c in p}
    if any(v<500 for v in coverage.values()): raise RuntimeError(f'Insufficient observations: {coverage}')
    p=p.ffill().dropna(); tri=tri_history(p.index[0].date(),p.index[-1].date()); out=p.join(tri,how='inner').dropna(subset=['TRI'])
    if len(out)<500: raise RuntimeError(f'Insufficient common history: {len(out)}')
    out['NIFTY_SMA200']=out['NIFTY'].rolling(TREND_WINDOW).mean(); out['NIFTY_MOM60']=out['NIFTY'].pct_change(LOOKBACK)
    return out

def risk_weights(vol):
    inv=1/vol; raw=pd.Series(BASE_RISK,index=vol.index)*inv/inv.mean(); caps=pd.Series(RISK_CAPS,index=vol.index)
    w=pd.Series(0.0,index=vol.index); free=list(vol.index); remaining=1.0
    for _ in range(len(vol)+5):
        if not free: break
        pool=raw[free].sum()
        if pool<=0: raise RuntimeError('Invalid inverse-vol weights')
        proposal=raw[free]/pool*remaining; capped=[k for k in free if proposal[k]>=caps[k]-1e-10]
        if not capped: w.loc[free]=proposal; remaining=0.0; break
        for k in capped: w[k]=float(caps[k]); remaining-=w[k]
        free=[k for k in free if k not in capped]
    if abs(w.sum()-1)>1e-8 or any(w[k]>caps[k]+1e-8 for k in w.index): raise RuntimeError(f'Risk weight failure: {w.to_dict()}')
    return w

def run(d):
    r=d[list(RISK_ASSETS)+[CASH]].pct_change().fillna(0); rv=r[list(RISK_ASSETS)].rolling(LOOKBACK).std()*np.sqrt(252)
    current=pd.Series({'NIFTY':.55,'GOLD':.20,'NASDAQ':.15,'CASH':.10}); vals=[]; allocations=[]; defensive_days=0; rebalances=0; eq=1.0
    for i in range(1,len(d)):
        p=i-1
        if i==1 or d.index[i].month!=d.index[i-1].month:
            v=rv.iloc[p]
            if v.notna().all() and (v>0).all():
                risk=risk_weights(v)
                defensive=bool(d['NIFTY'].iloc[p] < d['NIFTY_SMA200'].iloc[p] and d['NIFTY_MOM60'].iloc[p] < 0)
                exposure=DEFENSIVE_EXPOSURE if defensive else NORMAL_EXPOSURE
                target=risk*exposure; target[CASH]=1-exposure
                if abs(target.sum()-1)>1e-8: raise RuntimeError(f'Allocation normalization failed: {target.to_dict()}')
                turnover=float((target-current).abs().sum()); eq*=max(0,1-turnover*(COST+SLIPPAGE)); current=target; rebalances+=1
        if current[CASH]>0.100000001: defensive_days+=1
        allocations.append(current.copy()); eq*=1+float((current*r.iloc[i]).sum()); vals.append((d.index[i],eq))
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':rebalances,'defensive_days':defensive_days,'defensive_fraction':float(defensive_days/max(1,len(s))),'avg_weights':{k:float(v) for k,v in pd.DataFrame(allocations).mean().items()}}

def period(s,a,b):
    x=s.loc[a:b]
    if len(x)<2:return {}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    windows=[('2008-2009','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2015-2016','2015-01-01','2016-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025-2026','2025-01-01',str(d.index[-1].date()))]
    out={'strategy':'V16 diversified confirmed-regime portfolio; 60-day inverse-vol; defensive only when NIFTY is below 200-day SMA and 60-day momentum is negative; monthly rebalance','benchmark':'Official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'windows':[{'name':n,'start':a,'end':b,**period(s,a,b)} for n,a,b in windows],'parameters':{'base_risk_weights':BASE_RISK,'risk_caps':RISK_CAPS,'normal_exposure':NORMAL_EXPOSURE,'defensive_exposure':DEFENSIVE_EXPOSURE,'trend_window_days':TREND_WINDOW,'momentum_window_days':LOOKBACK,'vol_lookback_days':LOOKBACK,'rebalance':'monthly','cost':COST,'slippage':SLIPPAGE,'risk_assets':RISK_ASSETS,'cash_proxy':CASH_TICKER},'warnings':['^IRX is a U.S. Treasury-bill rate proxy, not Indian cash.','GC=F and ^IXIC are research proxies, not exact Indian execution.','No leverage; no final-test parameter fitting.','Regime inputs use prior-day values to avoid same-day look-ahead.']}
    json.dump(out,open('nifty_v16_confirmed_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
