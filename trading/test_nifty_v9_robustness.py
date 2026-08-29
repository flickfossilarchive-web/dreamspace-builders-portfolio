import json, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location('v9','trading/test_nifty_v9_tri_overlay.py'); v9=importlib.util.module_from_spec(spec); spec.loader.exec_module(v9)
OUT=Path('nifty_v9_robustness_results.json')

def simulate(d,cap=.10,cost=.0005,slip=.0005,rebalance='weekly',fast=50,slow=200,mf_n=63,ms_n=252):
    c=d.Close.astype(float); tri=d.TRI.astype(float); r=tri.pct_change().fillna(0.0)
    ma_f=c.rolling(fast).mean(); ma_s=c.rolling(slow).mean(); mf=c.pct_change(mf_n); ms=c.pct_change(ms_n)
    equity=1.; peak=1.; exposure=1.; rows=[]; trades=0; prev=None
    for i in range(1,len(d)):
        p=i-1; vals=[ma_f.iloc[p],ma_s.iloc[p],mf.iloc[p],ms.iloc[p],d.VIX.iloc[p]]
        if not all(np.isfinite(x) for x in vals): equity*=1+exposure*r.iloc[i]; peak=max(peak,equity); rows.append((d.index[i],equity,exposure)); continue
        a,b,x,y,v=vals; dd=equity/peak-1.; cut=0.
        if c.iloc[p]<b and x<0 and y<0: cut=cap
        elif c.iloc[p]<b and x<0: cut=cap*.65
        elif a<b and x<0: cut=cap*.35
        if v>=35: cut=max(cut,cap)
        elif v>=30: cut=max(cut,cap*.75)
        elif v>=25: cut=max(cut,cap*.40)
        if dd<=-.15: cut=max(cut,cap*.75)
        elif dd<=-.10: cut=max(cut,cap*.40)
        target=1-min(cap,cut)
        period=(d.index[i].year,d.index[i].month) if rebalance=='monthly' else (d.index[i].year,int(d.index[i].isocalendar().week))
        if period!=prev and abs(target-exposure)>=.025:
            tv=abs(target-exposure); equity*=max(0,1-tv*(cost+slip)); exposure=target; trades+=1
        prev=period; equity*=1+exposure*r.iloc[i]; peak=max(peak,equity); rows.append((d.index[i],equity,exposure))
    return pd.DataFrame(rows,columns=['Date','Equity','Exposure']).set_index('Date'),trades

def metrics(s):
    x=s.Equity; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'total_return':float(x.iloc[-1]-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)) if rr.std() else 0.,'trades':int((s.Exposure.diff()!=0).sum()),'avg_exposure':float(s.Exposure.mean())}

def window(s,a,b):
    q=s.loc[a:b].copy()
    if len(q)<2:return {}
    q.Equity/=q.Equity.iloc[0]; return metrics(q)

def bootstrap(s,n=2000,seed=42):
    rng=np.random.default_rng(seed); r=s.Equity.pct_change().dropna().to_numpy(); vals=[]
    for _ in range(n):
        z=rng.choice(r,len(r),replace=True); vals.append(np.prod(1+z)**(252/len(z))-1)
    vals=np.asarray(vals)
    return {'iterations':n,'seed':seed,'cagr_p05':float(np.percentile(vals,5)),'cagr_median':float(np.percentile(vals,50)),'cagr_p95':float(np.percentile(vals,95)),'prob_positive':float((vals>0).mean())}

def main():
    d=v9.data(); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    out={'suite':'V9 full robustness audit','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':'Official NIFTY 50 Total Return Index','buy_hold_tri_cagr':bench}
    base,_=simulate(d); out['base']=metrics(base)
    out['cost_slippage']={f'{c:.4f}/{s:.4f}':metrics(simulate(d,cost=c,slip=s)[0]) for c,s in [(.00025,.00025),(.0005,.0005),(.001,.001),(.002,.002),(.003,.003)]}
    out['overlay_caps']={str(c):metrics(simulate(d,cap=c)[0]) for c in [.05,.10,.15,.20]}
    out['rebalance']={r:metrics(simulate(d,rebalance=r)[0]) for r in ['weekly','monthly']}
    ps={'baseline':(50,200,63,252),'ma_fast_45':(45,200,63,252),'ma_fast_55':(55,200,63,252),'ma_slow_180':(50,180,63,252),'ma_slow_220':(50,220,63,252),'mom_56':(50,200,56,252),'mom_70':(50,200,70,252),'mom_240':(50,200,63,240),'mom_270':(50,200,63,270)}
    out['parameter_perturbation']={k:metrics(simulate(d,fast=a,slow=b,mf_n=c,ms_n=e)[0]) for k,(a,b,c,e) in ps.items()}
    out['crisis_periods']={k:window(base,a,b) for k,(a,b) in {'2008':('2008-01-01','2009-03-31'),'2011':('2011-01-01','2011-12-31'),'2018':('2018-01-01','2018-12-31'),'2020':('2020-01-01','2020-12-31'),'2022':('2022-01-01','2022-12-31')}.items()}
    wf=[('2014-01-01','2016-12-31'),('2017-01-01','2019-12-31'),('2020-01-01','2022-12-31'),('2023-01-01',str(d.index[-1].date()))]
    out['walk_forward']={f'{a}->{b}':window(base,a,b) for a,b in wf}
    out['bootstrap']=bootstrap(base)
    pv=[v['cagr'] for v in out['parameter_perturbation'].values()]; high=out['cost_slippage']['0.0030/0.0030']['cagr']
    out['gates']={'all_parameter_variants_profitable':all(x>0 for x in pv),'high_cost_profitable':high>0,'monthly_rebalance_profitable':out['rebalance']['monthly']['cagr']>0,'bootstrap_positive_probability':out['bootstrap']['prob_positive'],'beats_tri_cagr':out['base']['cagr']>bench,'investable':False}
    out['verdict']='ROBUSTNESS_COMPLETE_NOT_INVESTABLE' if not out['gates']['beats_tri_cagr'] else 'ROBUSTNESS_COMPLETE_REQUIRES_PAPER_TRADING_REVIEW'
    out['research_note']='Fixed robustness matrix; no parameter selection after observing results. TRI drives portfolio returns; NIFTY price index drives signals. Costs/slippage apply to exposure changes.'
    OUT.write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
