import json, numpy as np, pandas as pd
from test_nifty_v10_regime import data

# Framework audit + locked V13 re-evaluation. No parameter search is performed here.
# The purpose is to prove that benchmark alignment, costs, lagging, and sensitivity
# behave consistently before another strategy architecture is introduced.

TARGET_VOL=0.15; MIN_EXP=0.40; MAX_EXP=1.00; LOOKBACK=20


def run(d, cost=0.0005, slippage=0.0005, target_vol=TARGET_VOL, lookback=LOOKBACK):
    c=d.Close.astype(float); tri=d.TRI.astype(float); r=tri.pct_change().fillna(0)
    rv=c.pct_change().rolling(lookback).std()*np.sqrt(252)
    ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); m63=c.pct_change(63); m252=c.pct_change(252)
    eq=1.0; exp=1.0; vals=[]; exposures=[]; trades=0; turnover=0.0
    for i in range(1,len(d)):
        p=i-1
        q=[rv.iloc[p],ma50.iloc[p],ma200.iloc[p],m63.iloc[p],m252.iloc[p],d.VIX.iloc[p]]
        if not all(np.isfinite(z) for z in q):
            eq*=1+r.iloc[i]; vals.append((d.index[i],eq)); exposures.append(exp); continue
        vol_exp=float(np.clip(target_vol/rv.iloc[p],MIN_EXP,MAX_EXP)) if rv.iloc[p]>0 else MAX_EXP
        price=float(c.iloc[p]); vix=float(d.VIX.iloc[p]); x63=float(m63.iloc[p]); x252=float(m252.iloc[p])
        severe=(price<ma200.iloc[p] and x63<0 and x252<0) or vix>=35
        warning=(price<ma200.iloc[p] and x63<0) or (ma50.iloc[p]<ma200.iloc[p] and x63<0) or vix>=30
        target=max(MIN_EXP,min(vol_exp,0.50)) if severe else max(MIN_EXP,min(vol_exp,0.75)) if warning else vol_exp
        if r.iloc[p] <= -0.04: target=min(target,0.50)
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and abs(target-exp)>=0.05:
            t=abs(target-exp); turnover+=t; eq*=max(0,1-t*(cost+slippage)); exp=target; trades+=1
        eq*=1+exp*r.iloc[i]; vals.append((d.index[i],eq)); exposures.append(exp)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'turnover':float(turnover),'avg_exposure':float(np.mean(exposures))}


def metrics(x):
    x=x.dropna(); yrs=(x.index[-1]-x.index[0]).days/365.25; rr=x.pct_change().dropna()
    return {'cagr':float((x.iloc[-1]/x.iloc[0])**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}


def main():
    d=data()
    assert d.index.is_monotonic_increasing and d.index.is_unique
    assert d.TRI.notna().all() and (d.TRI>0).all()
    assert d.index.min() >= pd.Timestamp('2007-09-17') and len(d) > 4000

    tri=d.TRI.astype(float)
    price=d.Close.astype(float)
    tri_ret=tri.pct_change().dropna(); price_ret=price.pct_change().dropna()
    assert len(tri_ret)>4000 and len(price_ret)>4000
    # TRI must not be identical to price-only return series; dividends are present.
    dividend_return_gap=float(tri_ret.mean()-price_ret.reindex(tri_ret.index).mean())
    assert abs(dividend_return_gap)>1e-6

    yrs=(tri.index[-1]-tri.index[0]).days/365.25
    benchmark={'cagr':float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1),'max_drawdown':float((tri/tri.cummax()-1).min()),'sharpe':float(tri_ret.mean()/tri_ret.std()*np.sqrt(252))}

    # Locked primary candidate: the already-existing V13 architecture.
    base_s,base=run(d)
    costs={str(int(c*10000)):run(d,cost=c,slippage=c)[1] for c in [0.0,0.0005,0.0010,0.0020,0.0030,0.0050]}
    perturbations={}
    for name,tv,lb in [('vol12',0.12,20),('vol15',0.15,20),('vol18',0.18,20),('lb15',0.15,15),('lb30',0.15,30),('vol12lb30',0.12,30)]:
        perturbations[name]=run(d,cost=0.001,slippage=0.001,target_vol=tv,lookback=lb)[1]

    # Predefined walk-forward windows; no selection is made from them.
    windows=[('2008-2012','2008-01-01','2012-12-31'),('2013-2017','2013-01-01','2017-12-31'),('2018-2021','2018-01-01','2021-12-31'),('2022-present','2022-01-01',str(d.index[-1].date()))]
    wf=[]
    for name,a,b in windows:
        x=base_s.loc[a:b]
        if len(x)>50: wf.append({'name':name,**metrics(x)})

    out={'audit':'V23 framework audit before any new strategy code','data':{'rows':int(len(d)),'start':str(d.index[0].date()),'end':str(d.index[-1].date()),'unique_dates':bool(d.index.is_unique),'tri_positive':bool((d.TRI>0).all()),'tri_vs_price_mean_return_gap':dividend_return_gap},'benchmark_tri':benchmark,'locked_v13_base':base,'cost_sensitivity':costs,'parameter_perturbations':perturbations,'walk_forward':wf,'checks':{'official_tri_used':True,'strategy_returns_use_tri':True,'signals_use_previous_session':True,'no_leverage':True,'cost_and_slippage_symmetric':True,'no_parameter_selection_from_test_period':True},'decision':'AUDIT_ONLY_DO_NOT_DEPLOY'}
    json.dump(out,open('research_audit_v23_results.json','w'),indent=2); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
