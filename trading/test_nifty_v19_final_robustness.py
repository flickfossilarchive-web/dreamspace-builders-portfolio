import json, numpy as np, pandas as pd
import test_nifty_v19_regime_risk_budget as v19

VARIANTS=[
('base',126,60,200,0.14,0.55,21,0.15),('mom90',90,60,200,0.14,0.55,21,0.15),('mom252',252,60,200,0.14,0.55,21,0.15),
('vol40',126,40,200,0.14,0.55,21,0.15),('vol90',126,90,200,0.14,0.55,21,0.15),('trend150',126,60,150,0.14,0.55,21,0.15),
('trend250',126,60,250,0.14,0.55,21,0.15),('target10',126,60,200,0.10,0.55,21,0.15),('target18',126,60,200,0.18,0.55,21,0.15),
('cap45',126,60,200,0.14,0.45,21,0.15),('cap65',126,60,200,0.14,0.65,21,0.15),('reb14',126,60,200,0.14,0.55,14,0.15),
('reb42',126,60,200,0.14,0.55,42,0.15),('turn10',126,60,200,0.14,0.55,21,0.10),('turn25',126,60,200,0.14,0.55,21,0.25)]

def run_variant(d,p,cost):
    keys=['MOM','VOL','TREND','TARGET_VOL','MAX_RISK_ASSET','REBALANCE_DAYS','TURNOVER_TRIGGER']; old={k:getattr(v19,k) for k in keys}
    try:
        for k,val in zip(keys,p[1:]): setattr(v19,k,val)
        return v19.run(d,cost)
    finally:
        for k,val in old.items(): setattr(v19,k,val)

def metrics(s):
    s=s.dropna(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/yrs)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def bootstrap(s,n=2000,seed=19):
    r=s.pct_change().dropna().to_numpy(); rng=np.random.default_rng(seed); out=[]; block=20
    for _ in range(n):
        z=[]
        while len(z)<len(r):
            j=int(rng.integers(0,max(1,len(r)-block+1))); z.extend(r[j:j+block])
        x=np.cumprod(1+np.asarray(z[:len(r)])); out.append(x[-1]**(252/len(r))-1)
    return {'iterations':n,'median_cagr':float(np.median(out)),'p05_cagr':float(np.percentile(out,5)),'p95_cagr':float(np.percentile(out,95)),'positive_probability':float(np.mean(np.asarray(out)>0))}

def main():
    d=v19.data(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    rows=[]
    for p in VARIANTS:
        s,m=run_variant(d,p,0.001); rows.append({'name':p[0],**m,'beats_benchmark':m['cagr']>bench})
    base_s,_=run_variant(d,VARIANTS[0],0.001)
    costs=[]
    for b in [0,5,10,15,20,30,40,50]:
        s,m=run_variant(d,VARIANTS[0],b/10000); costs.append({'bps':b,**m,'beats_benchmark':m['cagr']>bench})
    wf=[]
    for name,a,b in [('2009-2013','2009-01-01','2013-12-31'),('2014-2018','2014-01-01','2018-12-31'),('2019-2022','2019-01-01','2022-12-31'),('2023-2026','2023-01-01',str(d.index[-1].date()))]: wf.append({'name':name,**metrics(base_s.loc[a:b])})
    boot=bootstrap(base_s)
    gate={'cost_20bps_beats':next(x for x in costs if x['bps']==20)['beats_benchmark'],'all_parameter_variants_profitable':all(x['cagr']>0 for x in rows),'all_walk_forward_profitable':all(x['cagr']>0 for x in wf),'bootstrap_positive_probability_ge_0_95':boot['positive_probability']>=0.95,'base_beats_nifty':rows[0]['beats_benchmark']}
    out={'strategy':'V19 INR regime risk-budget final robustness','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'base':rows[0],'parameter_perturbations':rows,'cost_sensitivity':costs,'walk_forward':wf,'bootstrap':boot,'investment_gate':{**gate,'pass':all(gate.values())}}
    json.dump(out,open('nifty_v19_final_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
