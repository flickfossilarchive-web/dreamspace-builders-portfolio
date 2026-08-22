import json, numpy as np, pandas as pd
import test_nifty_v22_trend_overlay as v22
VARIANTS=[('base',252,200,126,21,1.00,.70,.30,.30,.50),('mom189',189,200,126,21,1.00,.70,.30,.30,.50),('mom126',126,200,126,21,1.00,.70,.30,.30,.50),('trend150',252,150,126,21,1.00,.70,.30,.30,.50),('trend250',252,250,126,21,1.00,.70,.30,.30,.50),('gold90',252,200,90,21,1.00,.70,.30,.30,.50),('gold180',252,200,180,21,1.00,.70,.30,.30,.50),('reb42',252,200,126,42,1.00,.70,.30,.30,.50),('neutral60',252,200,126,21,1.00,.60,.40,.30,.50),('neutral80',252,200,126,21,1.00,.80,.20,.30,.50),('riskoff20',252,200,126,21,1.00,.70,.30,.20,.60),('riskoff40',252,200,126,21,1.00,.70,.30,.40,.40)]

def run_variant(d,p,cost):
    keys=['MOM','TREND','GOLD_MOM','REBALANCE_DAYS','RISK_ON_NIFTY','NEUTRAL_NIFTY','NEUTRAL_GOLD','RISK_OFF_NIFTY','RISK_OFF_GOLD']; old={k:getattr(v22,k) for k in keys}
    try:
        for k,val in zip(keys,p[1:]): setattr(v22,k,val)
        return v22.run(d,cost)
    finally:
        for k,val in old.items(): setattr(v22,k,val)

def metrics(s):
    s=s.dropna(); r=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252))}

def bootstrap(s,n=2000,seed=22):
    r=s.pct_change().dropna().to_numpy(); rng=np.random.default_rng(seed); out=[]; block=20
    for _ in range(n):
        z=[]
        while len(z)<len(r):
            j=int(rng.integers(0,max(1,len(r)-block+1))); z.extend(r[j:j+block])
        x=np.cumprod(1+np.asarray(z[:len(r)])); out.append(x[-1]**(252/len(r))-1)
    a=np.asarray(out); return {'iterations':n,'median_cagr':float(np.median(a)),'p05_cagr':float(np.percentile(a,5)),'p95_cagr':float(np.percentile(a,95)),'positive_probability':float(np.mean(a>0))}

def main():
    d=v22.data(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    rows=[]
    for p in VARIANTS:
        s,m=run_variant(d,p,.001); rows.append({'name':p[0],**m,'beats_benchmark':m['cagr']>bench})
    costs=[]
    for b in [0,5,10,15,20,30,40,50]:
        _,m=run_variant(d,VARIANTS[0],b/10000); costs.append({'bps':b,**m,'beats_benchmark':m['cagr']>bench})
    base_s,_=run_variant(d,VARIANTS[0],.001); wf=[]
    for name,a,b in [('2009-2013','2009-01-01','2013-12-31'),('2014-2018','2014-01-01','2018-12-31'),('2019-2022','2019-01-01','2022-12-31'),('2023-2026','2023-01-01',str(d.index[-1].date()))]: wf.append({'name':name,**metrics(base_s.loc[a:b])})
    boot=bootstrap(base_s); c20=next(x for x in costs if x['bps']==20)
    gate={'cost_20bps_beats':c20['beats_benchmark'],'all_parameter_variants_profitable':all(x['cagr']>0 for x in rows),'all_walk_forward_profitable':all(x['cagr']>0 for x in wf),'bootstrap_positive_probability_ge_0_95':boot['positive_probability']>=.95,'base_beats_nifty':rows[0]['beats_benchmark'],'drawdown_under_30pct':rows[0]['max_drawdown']>-0.30,'sharpe_ge_080':rows[0]['sharpe']>=.80}
    out={'strategy':'V22 NIFTY trend-following overlay','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'base':rows[0],'parameter_perturbations':rows,'cost_sensitivity':costs,'walk_forward':wf,'bootstrap':boot,'investment_gate':{**gate,'pass':all(gate.values())}}
    json.dump(out,open('nifty_v22_final_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
