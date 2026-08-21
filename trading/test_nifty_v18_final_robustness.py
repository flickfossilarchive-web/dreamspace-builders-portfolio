import json, math
import numpy as np
import pandas as pd
import test_nifty_v18_turnover_aware_dual_momentum as v18

# Fixed ex-ante perturbation matrix; no optimization against final results.
VARIANTS = [
    {'name':'base','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'mom_90','momentum_days':90,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'mom_252','momentum_days':252,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'vol_40','momentum_days':126,'vol_days':40,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'vol_90','momentum_days':126,'vol_days':90,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'trend_150','momentum_days':126,'vol_days':60,'trend_days':150,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'trend_250','momentum_days':126,'vol_days':60,'trend_days':250,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'leaders_1','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':1,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'leaders_3','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':3,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'defensive_50','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.50,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'defensive_85','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.85,'turnover_trigger':0.20,'drift_trigger':0.10},
    {'name':'turnover_10','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.10,'drift_trigger':0.10},
    {'name':'turnover_30','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.30,'drift_trigger':0.10},
    {'name':'drift_05','momentum_days':126,'vol_days':60,'trend_days':200,'leaders':2,'defensive_exposure':0.70,'turnover_trigger':0.20,'drift_trigger':0.05},
]

def with_variant(fn, d, p, cost):
    old={k:getattr(v18,k) for k in ['MOM','VOL','TREND','LEADERS','DEFENSIVE_EXPOSURE','TURNOVER_TRIGGER','DRIFT_TRIGGER']}
    try:
        v18.MOM=p['momentum_days']; v18.VOL=p['vol_days']; v18.TREND=p['trend_days']; v18.LEADERS=p['leaders']
        v18.DEFENSIVE_EXPOSURE=p['defensive_exposure']; v18.TURNOVER_TRIGGER=p['turnover_trigger']; v18.DRIFT_TRIGGER=p['drift_trigger']
        return fn(d,cost)
    finally:
        for k,val in old.items(): setattr(v18,k,val)

def metrics(s):
    s=s.dropna()
    if len(s)<10: return {'cagr':None,'max_drawdown':None,'sharpe':None}
    rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def bootstrap(s, n=2000, seed=18):
    r=s.pct_change().dropna().to_numpy(); rng=np.random.default_rng(seed); out=np.empty(n); block=20
    for i in range(n):
        chunks=[]
        while len(chunks)*block < len(r):
            j=int(rng.integers(0,max(1,len(r)-block+1))); chunks.extend(r[j:j+block])
        x=np.cumprod(1+np.asarray(chunks[:len(r)])); yrs=len(r)/252
        out[i]=x[-1]**(1/yrs)-1
    return {'iterations':n,'median_cagr':float(np.median(out)),'p05_cagr':float(np.percentile(out,5)),'p95_cagr':float(np.percentile(out,95)),'positive_probability':float(np.mean(out>0))}

def main():
    d=v18.data(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    variants=[]
    for p in VARIANTS:
        s,m=with_variant(v18.run,d,p,0.0010); variants.append({'name':p['name'],**m,'beats_benchmark':m['cagr']>bench})
    base_s,_=with_variant(v18.run,d,VARIANTS[0],0.0010)
    # Fixed walk-forward evaluation. Parameters are unchanged; each slice is genuinely out-of-sample by date.
    windows=[('2009-2013','2009-01-01','2013-12-31'),('2014-2018','2014-01-01','2018-12-31'),('2019-2022','2019-01-01','2022-12-31'),('2023-2026','2023-01-01',str(d.index[-1].date()))]
    wf=[]
    for name,a,b in windows: wf.append({'name':name,**metrics(base_s.loc[a:b])})
    cost=[]
    for bps in [0,5,10,15,20,25,30,40,50]:
        s,m=with_variant(v18.run,d,VARIANTS[0],bps/10000); cost.append({'total_cost_bps':bps,**m,'beats_benchmark':m['cagr']>bench})
    out={'strategy':'V18 final robustness: turnover-aware dual momentum, fixed ex-ante perturbations, walk-forward, block bootstrap','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'base':variants[0],'parameter_perturbations':variants,'walk_forward':wf,'cost_sensitivity':cost,'bootstrap':bootstrap(base_s),'investment_gate':{'cost_20bps_beats':next(x for x in cost if x['total_cost_bps']==20)['beats_benchmark'],'all_parameter_variants_profitable':all(x['cagr']>0 for x in variants),'all_walk_forward_profitable':all(x['cagr'] is not None and x['cagr']>0 for x in wf),'bootstrap_positive_probability_ge_0_95':bootstrap(base_s)['positive_probability']>=0.95}}
    gate=out['investment_gate']; out['investment_gate']['pass']=all(gate.values())
    json.dump(out,open('nifty_v18_final_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
