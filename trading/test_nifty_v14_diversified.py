import json, numpy as np, pandas as pd, yfinance as yf
from test_nifty_v10_regime import tri_history
START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005; LOOKBACK=60
RISK_ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}; CASH='CASH'; CASH_TICKER='BIL'
BASE_RISK={'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15}; RISK_CAPS={'NIFTY':0.70,'GOLD':0.30,'NASDAQ':0.25}; CASH_BASE=0.10; CASH_MIN=0.10; CASH_MAX=0.30

def load(name,ticker):
 d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
 if d is None or d.empty: raise RuntimeError(f'No data for {name} ({ticker})')
 if isinstance(d.columns,pd.MultiIndex):
  s=d['Close'] if 'Close' in d.columns.get_level_values(0) else d.xs('Close',axis=1,level=1)
  if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
 else: s=d['Close']
 s=pd.to_numeric(s,errors='coerce').rename(name); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def data():
 p=pd.concat([load(n,t) for n,t in RISK_ASSETS.items()]+[load(CASH,CASH_TICKER)],axis=1).sort_index(); coverage={c:int(p[c].notna().sum()) for c in p}
 if any(v<500 for v in coverage.values()): raise RuntimeError(f'Insufficient observations: {coverage}')
 p=p.ffill().dropna(); tri=tri_history(p.index[0].date(),p.index[-1].date()); out=p.join(tri,how='inner').dropna(subset=['TRI'])
 if len(out)<500: raise RuntimeError(f'Insufficient common history: {len(out)}')
 print(json.dumps({'data_integrity':{'columns':list(out.columns),'rows':len(out),'start':str(out.index[0].date()),'end':str(out.index[-1].date()),'raw_coverage':coverage}},indent=2)); return out

def risk_weights(v):
 inv=1/v; w=pd.Series(BASE_RISK)*inv/inv.mean(); w=w.clip(lower=0)
 for _ in range(20):
  over={k:max(0,float(w[k]-RISK_CAPS[k])) for k in w.index}; excess=sum(over.values())
  if excess<1e-10: break
  for k in w.index: w[k]=min(float(w[k]),RISK_CAPS[k])
  room=[k for k in w.index if w[k]<RISK_CAPS[k]-1e-10]
  if not room: break
  for k in room: w[k]=float(w[k])+excess/len(room)
 return w/w.sum()

def run(d):
 r=d[list(RISK_ASSETS)+[CASH]].pct_change().fillna(0); rv=r[list(RISK_ASSETS)].rolling(LOOKBACK).std()*np.sqrt(252); current=pd.Series({'NIFTY':.55,'GOLD':.20,'NASDAQ':.15,'CASH':.10}); vals=[]; eq=1.; trades=0
 for i in range(1,len(d)):
  p=i-1
  if i==1 or d.index[i].month!=d.index[i-1].month:
   v=rv.iloc[p]
   if v.notna().all() and (v>0).all():
    risk=risk_weights(v); target=risk*0.90; target[CASH]=CASH_BASE
    if target[CASH]<CASH_MIN or target[CASH]>CASH_MAX or abs(target.sum()-1)>1e-9 or any(target[k]>RISK_CAPS[k]*.90+1e-9 for k in RISK_ASSETS): raise RuntimeError('Allocation sanity gate failed')
    turnover=float((target-current).abs().sum()); eq*=max(0,1-turnover*(COST+SLIPPAGE)); current=target; trades+=1
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
 out={'strategy':'V14 diversified risk sleeves; inverse-vol only on risky assets; fixed 10% cash; monthly rebalance','benchmark':'Official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'windows':[{'name':n,'start':a,'end':b,**period(s,a,b)} for n,a,b in windows],'parameters':{'base_risk_weights':BASE_RISK,'risk_caps':RISK_CAPS,'cash_fixed':CASH_BASE,'cash_bounds':[CASH_MIN,CASH_MAX],'lookback_days':LOOKBACK,'rebalance':'monthly','cost':COST,'slippage':SLIPPAGE,'risk_assets':RISK_ASSETS,'cash_proxy':CASH_TICKER},'warnings':['BIL is a U.S. 1-3 month Treasury-bill ETF used as a stable cash-like research proxy, not Indian cash.','GC=F and ^IXIC are research proxies, not exact Indian execution.','No leverage; no final-test parameter fitting.','Cash excluded from inverse-vol weighting.']}
 json.dump(out,open('nifty_v14_diversified_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
