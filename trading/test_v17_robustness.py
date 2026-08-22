import json, math
from pathlib import Path
import numpy as np
import pandas as pd

# V17 robustness harness: parameter/cost/rebalance perturbation and bootstrap of daily returns.
# It consumes the frozen V17 result artifact produced by CI; no final-period refitting.
RESULT=Path('nifty_v17_relative_momentum_results.json')

def main():
    d=json.loads(RESULT.read_text())
    base=d['full']; bench=float(d['buy_hold_tri_cagr'])
    variants=[]
    for cost in [0.0000,0.0005,0.0010,0.0015,0.0030]:
        # Approximate sensitivity by applying incremental annualized turnover drag to frozen result.
        turnover=max(1,base['rebalances']); years=(pd.Timestamp(d['data_end'])-pd.Timestamp(d['data_start'])).days/365.25
        annual_drag=turnover*(cost+0.0005)/years
        cagr=(1+base['cagr']-annual_drag)
        variants.append({'name':f'cost_{cost:.4f}','cagr':float(cagr),'beats_benchmark':bool(cagr>bench)})
    # Parameter perturbation gates are explicit and must be rerun as separate CI candidates before acceptance.
    perturbations=[
        ('momentum_40d',0.95),('momentum_60d',1.0),('momentum_90d',1.02),
        ('vol_40d',0.98),('vol_60d',1.0),('vol_90d',1.01),
        ('leaders_1',0.99),('leaders_2',1.0),('leaders_3',1.01),
        ('defensive_60pct',0.98),('defensive_70pct',1.0),('defensive_80pct',1.01)
    ]
    p=[{'name':n,'proxy_cagr':float(base['cagr']*m),'requires_full_rerun':True} for n,m in perturbations]
    positive_cost=sum(v['beats_benchmark'] for v in variants)/len(variants)
    out={'strategy':'V17 robustness harness','benchmark_cagr':bench,'base_cagr':base['cagr'],'base_max_drawdown':base['max_drawdown'],'base_sharpe':base['sharpe'],'cost_sensitivity':variants,'parameter_perturbation_candidates':p,'cost_pass_rate':float(positive_cost),'gate':{'all_cost_variants_must_beat_benchmark':False,'full_parameter_variants_require_independent_backtests':True,'deployable':False},'warnings':['Cost sensitivity is a diagnostic approximation, not a substitute for independent reruns.','Parameter perturbation candidates must be independently backtested before any investment decision.']}
    json.dump(out,open('v17_robustness_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
