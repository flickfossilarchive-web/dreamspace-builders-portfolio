import json
from pathlib import Path
import numpy as np
import pandas as pd
from test_nifty_v17_relative_momentum import data, run

RESULT=Path('nifty_v17_relative_momentum_results.json')

def main():
    frozen=json.loads(RESULT.read_text()); d=data(); bench=float(frozen['buy_hold_tri_cagr'])
    tests=[]
    # Every variant below is a full rerun from the same raw dataset and signal engine.
    for cost in [0.0000,0.0005,0.0010,0.0015,0.0030]:
        _,m=run(d,cost=cost,slippage=cost)
        tests.append({'name':f'cost_slippage_{cost:.4f}','cagr':m['cagr'],'max_drawdown':m['max_drawdown'],'sharpe':m['sharpe'],'rebalances':m['rebalances'],'beats_benchmark':m['cagr']>bench})
    params=[]
    for name,kwargs in [
        ('momentum_40d',{'mom_days':40}),('momentum_60d',{'mom_days':60}),('momentum_90d',{'mom_days':90}),('momentum_126d',{'mom_days':126}),
        ('vol_40d',{'vol_days':40}),('vol_90d',{'vol_days':90}),
        ('leaders_1',{'leaders_n':1}),('leaders_3',{'leaders_n':3}),
        ('defensive_60pct',{'defensive_exposure':0.60}),('defensive_80pct',{'defensive_exposure':0.80}),
        ('weekly_rebalance',{'rebalance':'weekly'}),('monthly_rebalance',{'rebalance':'monthly'})]:
        _,m=run(d,**kwargs)
        params.append({'name':name,'cagr':m['cagr'],'max_drawdown':m['max_drawdown'],'sharpe':m['sharpe'],'rebalances':m['rebalances'],'beats_benchmark':m['cagr']>bench})
    # Bootstrap daily strategy returns from the independently rerun base equity curve.
    base_s,base=run(d); daily=base_s.pct_change().dropna().to_numpy(); rng=np.random.default_rng(1729); n=2000
    boot=[]
    for _ in range(n):
        sample=rng.choice(daily,size=len(daily),replace=True); wealth=float(np.prod(1+sample)); yrs=(len(sample)/252); boot.append(wealth**(1/yrs)-1 if wealth>0 else -1.0)
    q=np.quantile(boot,[.05,.50,.95]); bootstrap={'iterations':n,'median_cagr':float(q[1]),'p05_cagr':float(q[0]),'p95_cagr':float(q[2]),'positive_probability':float(np.mean(np.array(boot)>0))}
    out={'strategy':'V17 independent robustness suite','benchmark_cagr':bench,'base':base,'cost_sensitivity':tests,'parameter_perturbations':params,'bootstrap':bootstrap,'gate':{'all_cost_variants_independently_backtested':len(tests)==5,'all_parameter_variants_independently_backtested':len(params)==12,'deployable':False},'warnings':['Gold and Nasdaq use research proxies, not exact Indian execution instruments.','Bootstrap is a statistical stress test, not proof of future returns.','Deployment remains blocked until the full suite is reviewed.']}
    json.dump(out,open('v17_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
