from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from stock_alpha_v1 import load_membership,fetch_prices,backtest

def metrics(r):
 r=r.dropna(); n=len(r); years=n/252
 if n==0:return {'days':0,'cagr':None,'sharpe':None,'max_drawdown':None}
 eq=(1+r).cumprod(); dd=float((eq/eq.cummax()-1).min())
 return {'days':int(n),'cagr':float(eq.iloc[-1]**(1/years)-1) if years else None,'sharpe':float(np.sqrt(252)*r.mean()/r.std()) if n>1 and r.std()>0 else None,'max_drawdown':dd}

def cost_sensitivity(px,mem):
 return {str(bps):metrics(backtest(px,mem,cost=bps/10000)[0])|{'turnover':backtest(px,mem,cost=bps/10000)[1]} for bps in [20,30,50]}

def walkforward(px,mem):
 cuts=[('2018-01-01','2020-12-31'),('2021-01-01','2022-12-31'),('2023-01-01','2024-12-31'),('2025-01-01','2026-08-01')]
 out={}
 for a,b in cuts:
  sub=px.loc[a:b];r,t=backtest(sub,mem,cost=.002);out[f'{a}:{b}']=metrics(r)|{'turnover':t}
 return out

def perturbations(px,mem):
 # Fixed before evaluation; no variant is selected post hoc.
 out={}
 for n in [10,15,25,30]:
  r,t=backtest(px,mem,cost=.002,top_n=n);out[f'top{n}']=metrics(r)|{'turnover':t}
 return out

def bootstrap(r,B=2000,seed=7):
 r=r.dropna().to_numpy()
 if len(r)<252:return {'iterations':B,'positive_probability':None}
 rng=np.random.default_rng(seed); block=21; vals=[]
 for _ in range(B):
  chunks=[]
  while len(chunks)*block<len(r):
   i=rng.integers(0,len(r));chunks.extend(r[i:min(i+block,len(r))])
  x=np.asarray(chunks[:len(r)]); vals.append((1+x).prod()**(252/len(x))-1)
 vals=np.asarray(vals)
 return {'iterations':B,'positive_probability':float((vals>0).mean()),'median_cagr':float(np.median(vals)),'p05_cagr':float(np.quantile(vals,.05)),'p95_cagr':float(np.quantile(vals,.95))}

def crisis(px,mem):
 periods={'2008-2009':('2008-01-01','2009-12-31'),'2011':('2011-01-01','2011-12-31'),'2018':('2018-01-01','2018-12-31'),'2020':('2020-01-01','2020-12-31'),'2022':('2022-01-01','2022-12-31')}
 out={}
 for k,(a,b) in periods.items():
  r,t=backtest(px.loc[a:b],mem,cost=.002);out[k]=metrics(r)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--membership',default='data/pit/index_membership_history.csv');ap.add_argument('--out',default='data/stock_alpha_v1_robustness');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 mem=load_membership(a.membership);symbols=sorted(mem.symbol.unique());px=fetch_prices(symbols,'2008-01-01','2026-08-01')
 base,turn=backtest(px,mem,cost=.002)
 wf=walkforward(px,mem);boot=bootstrap(base)
 result={'strategy':'Stock Alpha V1 Robustness','baseline':metrics(base)|{'turnover':turn},'cost_sensitivity':cost_sensitivity(px,mem),'walk_forward':wf,'crisis_periods':crisis(px,mem),'locked_perturbations':perturbations(px,mem),'bootstrap':boot,'data_quality':{'symbols':len(symbols),'price_columns':len(px.columns),'missing_fraction':float(px.isna().mean().mean())},'gate':{'cagr_gt_12pct':bool(metrics(base)['cagr'] is not None and metrics(base)['cagr']>0.12),'sharpe_ge_1':bool(metrics(base)['sharpe'] is not None and metrics(base)['sharpe']>=1.0),'drawdown_better_than_30pct':bool(metrics(base)['max_drawdown'] is not None and metrics(base)['max_drawdown']>=-0.30),'bootstrap_positive_ge_95pct':bool(boot['positive_probability'] is not None and boot['positive_probability']>=.95),'all_walk_forward_positive':all(v['cagr'] is not None and v['cagr']>0 for v in wf.values())}}
 result['investment_gate']=all(result['gate'].values())
 (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
