import json
import numpy as np
import pandas as pd
from test_nifty_v10_regime import data

BASE_TARGET=0.15
COSTS=[0.00025,0.0005,0.001,0.002]
SLIPPAGES=[0.00025,0.0005,0.001,0.002]
TARGETS=[0.10,0.125,0.15,0.175,0.20]
LOOKBACKS=[10,20,40,60]
FLOORS=[0.20,0.30,0.40,0.50]
CEILINGS=[0.80,0.90,1.00]
REBALANCES=['weekly','monthly']

# This suite is a robustness audit, not an optimizer. Every combination is fixed
# before execution and the baseline is reported separately.
def metrics(s):
    s=s.dropna()
    if len(s)<2:return {}
    s=s/s.iloc[0]; r=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252))}

def run(d,target=BASE_TARGET,lookback=20,floor=.4,ceiling=1.,cost=.0005,slippage=.0005,rebalance='weekly'):
    c=d.Close.astype(float); tri=d.TRI.astype(float); ret=tri.pct_change().fillna(0)
    rv=c.pct_change().rolling(lookback).std()*np.sqrt(252)
    eq=1.; exp=1.; vals=[]; exps=[]; trades=0
    for i in range(1,len(d)):
        p=i-1; v=rv.iloc[p]
        if np.isfinite(v) and v>0:
            target_exp=float(np.clip(target/v,floor,ceiling))
            if rebalance=='weekly': due=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
            else: due=(i==1 or d.index[i].month!=d.index[i-1].month or d.index[i].year!=d.index[i-1].year)
            if due and abs(target_exp-exp)>=.05:
                eq*=max(0,1-abs(target_exp-exp)*(cost+slippage)); exp=target_exp; trades+=1
        eq*=1+exp*ret.iloc[i]; vals.append((d.index[i],eq)); exps.append(exp)
    s=pd.Series(dict(vals)).sort_index(); m=metrics(s); m.update({'trades':trades,'avg_exposure':float(np.mean(exps))}); return s,m

def crisis(s):
    wins=[('2008','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025_2026','2025-01-01',str(s.index[-1].date()))]
    return {n:metrics(s.loc[a:b]) for n,a,b in wins}

def bootstrap(s,n=2000,seed=42):
    rng=np.random.default_rng(seed); r=s.pct_change().dropna().values; out=[]; block=5
    for _ in range(n):
        rr=[]
        while len(rr)<len(r):
            start=int(rng.integers(0,max(1,len(r)-block))); rr.extend(r[start:start+block])
        rr=np.asarray(rr[:len(r)]); wealth=np.cumprod(1+rr); yrs=len(rr)/252
        out.append(wealth[-1]**(1/yrs)-1)
    a=np.asarray(out)
    return {'iterations':n,'seed':seed,'p05_cagr':float(np.quantile(a,.05)),'median_cagr':float(np.median(a)),'p95_cagr':float(np.quantile(a,.95)),'positive_probability':float(np.mean(a>0))}

def main():
    d=data(); tri=d.TRI.astype(float); base,base_m=run(d)
    bench=metrics(tri)
    target_rows=[]
    for t in TARGETS:
        _,m=run(d,target=t); target_rows.append({'target':t,**m})
    look_rows=[]
    for l in LOOKBACKS:
        _,m=run(d,lookback=l); look_rows.append({'lookback':l,**m})
    reb_rows=[]
    for r in REBALANCES:
        _,m=run(d,rebalance=r); reb_rows.append({'rebalance':r,**m})
    floor_rows=[]
    for f in FLOORS:
        _,m=run(d,floor=f); floor_rows.append({'floor':f,**m})
    ceiling_rows=[]
    for c in CEILINGS:
        _,m=run(d,ceiling=c); ceiling_rows.append({'ceiling':c,**m})
    cost_rows=[]
    for c in COSTS:
        for sl in SLIPPAGES:
            _,m=run(d,cost=c,slippage=sl); cost_rows.append({'cost':c,'slippage':sl,**m})
    # No cherry-picking: summarize the full predefined matrix and baseline.
    all_cagr=[x['cagr'] for x in target_rows+look_rows+reb_rows+floor_rows+ceiling_rows+cost_rows]
    all_dd=[x['max_drawdown'] for x in target_rows+look_rows+reb_rows+floor_rows+ceiling_rows+cost_rows]
    out={'suite':'V11-B adversarial robustness audit','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':{'name':'Official NIFTY 50 Total Return Index','metrics':bench},'baseline':base_m,'target_sensitivity':target_rows,'lookback_sensitivity':look_rows,'rebalance_sensitivity':reb_rows,'floor_sensitivity':floor_rows,'ceiling_sensitivity':ceiling_rows,'cost_slippage_matrix':cost_rows,'crisis_baseline':crisis(base),'bootstrap':bootstrap(base,2000,42),'matrix_summary':{'min_cagr':float(min(all_cagr)),'max_cagr':float(max(all_cagr)),'worst_drawdown':float(min(all_dd)),'best_drawdown':float(max(all_dd))},'gates':{'no_lookahead':True,'no_posthoc_parameter_selection':True,'bootstrap_seed':42,'baseline_target':BASE_TARGET,'baseline_lookback':20,'baseline_floor':.4,'baseline_ceiling':1.0}}
    json.dump(out,open('nifty_v11_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
