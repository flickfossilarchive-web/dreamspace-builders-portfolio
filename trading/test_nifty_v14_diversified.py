import json, numpy as np, pandas as pd, yfinance as yf
from test_nifty_v10_regime import tri_history
START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005; LOOKBACK=60; TARGET_VOL=0.12
ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC','CASH':'^IRX'}
BASE={'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15,'CASH':0.10}; CAPS={'NIFTY':0.70,'GOLD':0.30,'NASDAQ':0.25,'CASH':0.20}
def load(name,ticker):
 d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
 if d is None or d.empty: raise RuntimeError(f'No data for {name} ({ticker})')
 if isinstance(d.columns,pd.MultiIndex):
  if 'Close' in d.columns.get_level_values(0): s=d['Close']
  elif 'Close' in d.columns.get_level_values(1): s=d.xs('Close',axis=1,level=1)
  else: raise RuntimeError(f'No Close field for {name}')
  if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
 else: s=d['Close']
 s=pd.to_numeric(s,errors='coerce').rename(name); s.index=pd.to_datetime(s.index).tz_localize(None); return s
def data():
 p=pd.concat([load(n,t) for n,t in ASSETS.items()],axis=1).sort_index(); coverage={c:int(p[c].notna().sum()) for c in p}
 if any(v<500 for v in coverage.values()): raise RuntimeError(f'Insufficient observations: {coverage}')
 y=p.CASH.ffill().clip(lower=0)/100/252; p.CASH=(1+y).cumprod(); p=p.ffill().dropna()
 if list(p.columns)!=list(ASSETS): raise RuntimeError(f'Asset schema mismatch: {list(p.columns)}')
 tri=tri_history(p.index[0].date(),p.index[-1].date()); out=p.join(tri,how='inner').dropna(subset=['TRI'])
 if len(out)<500: raise RuntimeError(f'Insufficient common history: {len(out)}')
 print(json.dumps({'data_integrity':{'columns':list(out.columns),'rows':len(out),'start':str(out.index[0].date()),'end':str(out.index[-1].date()),'raw_coverage':coverage}},indent=2)); return out
def run(d):
 r=d[list(ASSETS)].pct_change().fillna(0); rv=r.rolling(LOOKBACK).std()*np.sqrt(252); current=pd.Series(BASE,dtype=float); vals=[]; eq=1.; trades=0
 for i in range(1,len(d)):
  p=i-1
  if i==1 or d.index[i].month!=d.index[i-1].month:
   v=rv.iloc[p]
   if v.notna().all() and (v>0).all():
    inv=1/v; target=pd.Series(BASE,dtype=float)*inv/inv.mean(); target=target.clip(upper=pd.Series(CAPS)); target=target/target.sum(); turnover=float((target-current).abs().sum()); eq*=max(0,1-turnover*(COST+SLIPPAGE)); current=target; trades+=1
  eq*=1+float((current*r.iloc[i]).sum()); vals.append((d.index[i],eq))
 s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
 return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'avg_weights':current.to_dict()}
def period(s,a,b):
 x=s.loc[a:b]
 if len(x)<2:return {}
 x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
 return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}
def main():
 d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1); windows=[('2008','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2015-2016','2015-01-01','2016-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025-2026','2025-01-01',str(d.index[-1].date()))]
 out={'strategy':'V14 diversified fixed sleeves + 60d inverse-vol risk budget; monthly rebalance','benchmark':'Official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'windows':[{'name':n,'start':a,'end':b,**period(s,a,b)} for n,a,b in windows],'parameters':{'base_weights':BASE,'caps':CAPS,'lookback_days':LOOKBACK,'target_vol':TARGET_VOL,'rebalance':'monthly','cost':COST,'slippage':SLIPPAGE,'assets':ASSETS},'warnings':['GC=F, ^IXIC and ^IRX are research proxies, not exact Indian execution.','No leverage; no final-test parameter fitting.']}
 json.dump(out,open('nifty_v14_diversified_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
