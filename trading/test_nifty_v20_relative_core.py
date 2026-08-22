import json, numpy as np, pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'; ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}; MOM=90; TREND=200; VOL=60; COST=0.001; REBALANCE_DAYS=21
CORE_MIN=0.55; CORE_MAX=0.85; SAT_MAX=0.30

def series(t,n):
 d=yf.download(t,start=START,auto_adjust=False,progress=False)
 if d is None or d.empty: raise RuntimeError(n)
 s=d['Close']; s=s.iloc[:,0] if isinstance(s,pd.DataFrame) else s
 s=pd.to_numeric(s,errors='coerce').rename(n); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def data():
 r=pd.concat([series(t,n) for n,t in ASSETS.items()]+[series('INR=X','USDINR')],axis=1).sort_index().ffill()
 p=pd.DataFrame(index=r.index); p['NIFTY']=r.NIFTY; p['GOLD']=r.GOLD*r.USDINR; p['NASDAQ']=r.NASDAQ*r.USDINR; p['CASH']=1.
 tri=tri_history(p.index[0].date(),p.index[-1].date()); return p.join(tri,how='inner').dropna(subset=['TRI'])

def run(d,total_cost=COST):
 x=d.copy(); names=list(ASSETS)
 for n in names:
  x[n+'_MOM']=x[n].pct_change(MOM); x[n+'_VOL']=x[n].pct_change().rolling(VOL).std()*np.sqrt(252); x[n+'_TREND']=x[n]/x[n].rolling(TREND).mean()-1
 ret=x[names+['CASH']].pct_change().fillna(0); cur=pd.Series({'NIFTY':.70,'GOLD':0.,'NASDAQ':0.,'CASH':.30}); eq=1.; vals=[]; last=-REBALANCE_DAYS
 for i in range(1,len(x)):
  if i-last>=REBALANCE_DAYS:
   p=i-1; scores={n:(x[n+'_MOM'].iloc[p]-x['NIFTY_MOM'].iloc[p])/(x[n+'_VOL'].iloc[p]+1e-12) for n in ['GOLD','NASDAQ']}
   target=pd.Series(0.,index=cur.index)
   nifty_ok=np.isfinite(x['NIFTY_MOM'].iloc[p]) and np.isfinite(x['NIFTY_TREND'].iloc[p]) and x['NIFTY_MOM'].iloc[p]>0 and x['NIFTY_TREND'].iloc[p]>0
   target['NIFTY']=CORE_MAX if nifty_ok else CORE_MIN
   eligible=[n for n in ['GOLD','NASDAQ'] if np.isfinite(scores[n]) and x[n+'_MOM'].iloc[p]>0 and x[n+'_TREND'].iloc[p]>0 and scores[n]>0]
   if eligible:
    n=max(eligible,key=lambda z:scores[z]); target[n]=min(SAT_MAX,1-target['NIFTY']); target['NIFTY']=1-target[n]-max(0,1-target['NIFTY']-target[n])
   target['CASH']=1-target[['NIFTY','GOLD','NASDAQ']].sum(); t=float((target-cur).abs().sum()); eq*=max(0,1-t*total_cost); cur=target; last=i
  eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
 s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
 return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':int(last//REBALANCE_DAYS+1),'avg_annual_turnover':float(((s/s.shift(1)-1).abs().sum())/yrs)}

def main():
 d=data(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1); s,m=run(d); costs=[]
 for b in [0,5,10,15,20,30,40,50]:
  _,mm=run(d,b/10000); costs.append({'bps':b,**mm,'beats_benchmark':mm['cagr']>bench})
 out={'strategy':'V20 NIFTY-relative core with conditional diversifiers','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'full':m,'cost_sensitivity':costs,'parameters':{'momentum_days':MOM,'trend_days':TREND,'vol_days':VOL,'core_min':CORE_MIN,'core_max':CORE_MAX,'satellite_max':SAT_MAX,'rebalance_days':REBALANCE_DAYS,'base_cost_bps':10},'warnings':['Gold/Nasdaq research proxies converted to INR using USDINR.','Signals use prior-day data.','90-day momentum is a pre-registered hypothesis from V19 robustness, not selected after V20 results.']}
 json.dump(out,open('nifty_v20_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
