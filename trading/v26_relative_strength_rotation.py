import json
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import data

COST=0.001; SLIPPAGE=0.001; FAST=126; SLOW=252; TREND=200; VOL=60; FLOOR=0.40

# V26 hypothesis locked ex-ante: fully-invested cross-asset relative-strength rotation.
# Rank NIFTY, gold and Nasdaq by average 6m/12m momentum; require positive 200d trend;
# hold top two with inverse-vol weights, while retaining a 40% NIFTY floor. No leverage.

def assets(idx):
    out=pd.DataFrame(index=idx)
    for k,t in {'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}.items():
        x=yf.download(t,start=str(idx[0].date()),end=str((idx[-1]+pd.Timedelta(days=1)).date()),auto_adjust=False,progress=False)
        if isinstance(x.columns,pd.MultiIndex): x=x.xs(t,axis=1,level=1)
        if 'Close' not in x or len(x)<1000: raise RuntimeError(f'insufficient {k} history')
        x.index=pd.to_datetime(x.index).tz_localize(None); out[k]=x.Close.reindex(idx).ffill()
    return out.dropna()

def boot(rr,n=2000,block=21,seed=26):
    rng=np.random.default_rng(seed); a=np.asarray(rr,float); a=a[np.isfinite(a)]; vals=[]; m=len(a)
    for _ in range(n):
        z=[]
        while len(z)<m: j=int(rng.integers(0,m)); z.extend(a[j:j+block])
        z=np.asarray(z[:m]); vals.append(np.prod(1+z)**(252/m)-1)
    q=np.quantile(vals,[.05,.5,.95]); return {'n':n,'p05_cagr':float(q[0]),'median_cagr':float(q[1]),'p95_cagr':float(q[2]),'positive_probability':float(np.mean(np.asarray(vals)>0))}

def run(d,a,cost=COST,slippage=SLIPPAGE,fast=FAST,slow=SLOW,trend=TREND,floor=FLOOR):
    r=a.pct_change().fillna(0); eq=1.; w=pd.Series({'NIFTY':1.,'GOLD':0.,'NASDAQ':0.}); vals=[]; trades=0; turnover=0.
    for i in range(1,len(d)):
        p=i-1; month=(i==1 or d.index[i].month!=d.index[i-1].month or d.index[i].year!=d.index[i-1].year)
        if month and p>=slow:
            mom=.5*(a.iloc[p]/a.iloc[p-fast]-1)+.5*(a.iloc[p]/a.iloc[p-slow]-1)
            ma=a.iloc[:p+1].rolling(trend).mean().iloc[-1]; vv=r.iloc[:p+1].rolling(VOL).std().iloc[-1]*np.sqrt(252)
            elig=[k for k in a.columns if np.isfinite(mom[k]) and mom[k]>0 and a.iloc[p][k]>ma[k] and np.isfinite(vv[k]) and vv[k]>0]
            rank=sorted(elig,key=lambda k:float(mom[k]),reverse=True)[:2]; target=pd.Series(0.,index=a.columns); target['NIFTY']=floor
            others=[k for k in rank if k!='NIFTY']
            if others:
                inv=pd.Series({k:1/vv[k] for k in others}); target.loc[others]=(1-floor)*inv/inv.sum()
            elif 'NIFTY' in rank: target['NIFTY']=1.
            else: target['NIFTY']=1.
            t=float(np.abs(target-w).sum())/2
            if t>=.05: eq*=max(0,1-t*(cost+slippage)); turnover+=t; trades+=1; w=target
        eq*=1+float((w*r.iloc[i]).sum()); vals.append((d.index[i],eq))
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'turnover':turnover}

def metrics(s):
    s=s.dropna(); rr=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float((s.iloc[-1]/s.iloc[0])**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); a=assets(d.index); d=d.join(a,how='inner').dropna(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1); s,base=run(d,a)
    costs={str(int(c*10000)):run(d,a,cost=c,slippage=c)[1] for c in [0,.0005,.001,.0015,.002,.003,.004,.005]}
    pert={n:run(d,a,fast=f,slow=sl,trend=t,floor=fl)[1] for n,f,sl,t,fl in [('fast90',90,252,200,.4),('fast180',180,252,200,.4),('slow189',126,189,200,.4),('trend150',126,252,150,.4),('trend250',126,252,250,.4),('floor30',126,252,200,.3),('floor50',126,252,200,.5),('slow300',126,300,200,.4)]}
    wf=[]
    for n,x,y in [('2008-2012','2008-01-01','2012-12-31'),('2013-2017','2013-01-01','2017-12-31'),('2018-2021','2018-01-01','2021-12-31'),('2022-present','2022-01-01',str(d.index[-1].date()))]:
        z=s.loc[x:y]
        if len(z)>50: wf.append({'name':n,**metrics(z)})
    out={'strategy':'V26 fully-invested cross-asset relative-strength rotation','benchmark_cagr':bench,'base':base,'cost_sensitivity':costs,'parameter_perturbations':pert,'walk_forward':wf,'bootstrap':boot(s.pct_change().dropna().values),'rules':{'monthly_rebalance':True,'signals_previous_session':True,'no_leverage':True,'nifty_floor':FLOOR,'universe':['NIFTY','GOLD','NASDAQ']},'gate':{'primary_cost_bps':20,'base_cagr_gt_benchmark':True,'20bps_cagr_gt_benchmark':True,'sharpe_ge':.80,'max_dd_better_than':-.30,'all_perturbations_positive':True,'all_walk_forward_positive':True,'bootstrap_positive_probability_ge':.95}}
    json.dump(out,open('v26_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
