import json, numpy as np, pandas as pd
import test_nifty_v20_relative_core as v20

def metrics(s):
 s=s.dropna(); r=s.pct_change().fillna(0); y=(s.index[-1]-s.index[0]).days/365.25
 return {'cagr':float(s.iloc[-1]**(1/y)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252))}

def bootstrap(s,n=2000,seed=20):
 r=s.pct_change().dropna().to_numpy(); rng=np.random.default_rng(seed); out=[]; block=20
 for _ in range(n):
  z=[]
  while len(z)<len(r):
   j=int(rng.integers(0,max(1,len(r)-block+1))); z.extend(r[j:j+block])
  a=np.cumprod(1+np.asarray(z[:len(r)])); out.append(a[-1]**(252/len(r))-1)
 a=np.asarray(out); return {'iterations':n,'median_cagr':float(np.median(a)),'p05_cagr':float(np.percentile(a,5)),'p95_cagr':float(np.percentile(a,95)),'positive_probability':float(np.mean(a>0))}

def main():
 d=v20.data(); tri=d.TRI; y=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/y)-1); s,base=v20.run(d,0.001)
 costs=[]
 for b in [0,5,10,15,20,30,40,50]:
  _,m=v20.run(d,b/10000); costs.append({'bps':b,**m,'beats_benchmark':m['cagr']>bench})
 # Pre-registered perturbations around the economic design, not optimized after results.
 variants=[('mom60',60),('mom120',120),('trend150',150),('trend250',250),('core60',0.60),('core80',0.80),('sat20',0.20),('sat35',0.35)]
 rows=[]
 old=(v20.MOM,v20.TREND,v20.CORE_MIN,v20.CORE_MAX,v20.SAT_MAX)
 for name,val in variants:
  try:
   if name.startswith('mom'): v20.MOM=val
   elif name.startswith('trend'): v20.TREND=val
   elif name=='core60': v20.CORE_MIN=.60; v20.CORE_MAX=.60
   elif name=='core80': v20.CORE_MIN=.80; v20.CORE_MAX=.80
   elif name=='sat20': v20.SAT_MAX=.20
   elif name=='sat35': v20.SAT_MAX=.35
   _,m=v20.run(d,.001); rows.append({'name':name,**m,'beats_benchmark':m['cagr']>bench})
  finally: v20.MOM,v20.TREND,v20.CORE_MIN,v20.CORE_MAX,v20.SAT_MAX=old
 wf=[]
 for n,a,b in [('2009-2013','2009-01-01','2013-12-31'),('2014-2018','2014-01-01','2018-12-31'),('2019-2022','2019-01-01','2022-12-31'),('2023-2026','2023-01-01',str(d.index[-1].date()))]: wf.append({'name':n,**metrics(s.loc[a:b])})
 boot=bootstrap(s)
 gate={'base_beats_nifty':base['cagr']>bench,'cost_20bps_beats':next(x for x in costs if x['bps']==20)['beats_benchmark'],'all_parameter_variants_profitable':all(x['cagr']>0 for x in rows),'all_walk_forward_profitable':all(x['cagr']>0 for x in wf),'bootstrap_positive_probability_ge_0_95':boot['positive_probability']>=.95}
 out={'strategy':'V20 NIFTY-relative core with conditional diversifiers final robustness','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'base':base,'cost_sensitivity':costs,'parameter_perturbations':rows,'walk_forward':wf,'bootstrap':boot,'investment_gate':{**gate,'pass':all(gate.values())}}
 json.dump(out,open('nifty_v20_final_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
