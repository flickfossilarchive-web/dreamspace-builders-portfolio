import json
import numpy as np
import pandas as pd
from test_nifty_v10_regime import data

COST=0.0005
SLIPPAGE=0.0005
TARGET_VOL=0.15
MIN_EXP=0.40
MAX_EXP=1.00
LOOKBACK=20

# V11-B: fixed volatility-targeting policy. No parameter is fit on the test set.
def build(d):
    x=d.copy(); c=x.Close.astype(float)
    x['rv20']=c.pct_change().rolling(LOOKBACK).std()*np.sqrt(252)
    return x

def target_exp(rv):
    if not np.isfinite(rv) or rv<=0: return MAX_EXP
    return float(np.clip(TARGET_VOL/rv,MIN_EXP,MAX_EXP))

def run(x):
    tri=x.TRI.astype(float); r=tri.pct_change().fillna(0)
    eq=1.; exp=1.; vals=[]; exps=[]; trades=0
    for i in range(1,len(x)):
        p=i-1; rv=x.rv20.iloc[p]
        if not np.isfinite(rv):
            eq*=1+r.iloc[i]; vals.append((x.index[i],eq)); exps.append(exp); continue
        target=target_exp(rv)
        weekly=(i==1 or x.index[i].isocalendar().week!=x.index[i-1].isocalendar().week or x.index[i].year!=x.index[i-1].year)
        if weekly and abs(target-exp)>=0.05:
            eq*=max(0,1-abs(target-exp)*(COST+SLIPPAGE)); exp=target; trades+=1
        eq*=1+exp*r.iloc[i]; vals.append((x.index[i],eq)); exps.append(exp)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'avg_exposure':float(np.mean(exps))}

def metrics(s):
    x=s.dropna()
    if len(x)<2:return {}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def failure_analysis(x):
    # Diagnostic only: no optimization. Quantifies the damage in the V11-A concept
    # using its already-declared score and records major market windows.
    c=x.Close.astype(float); tri=x.TRI.astype(float)
    windows=[('2008_crisis','2008-01-01','2009-12-31'),('2011_selloff','2011-01-01','2011-12-31'),('2018_selloff','2018-01-01','2018-12-31'),('2020_crash','2020-01-01','2020-12-31'),('2022_selloff','2022-01-01','2022-12-31'),('2025_2026','2025-01-01',str(x.index[-1].date()))]
    out=[]
    for name,a,b in windows:
        out.append({'window':name,'nifty_tri':metrics(tri.loc[a:b])})
    return out

def main():
    d=build(data()); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    out={'strategy':'V11-B fixed 15% annualized volatility target on NIFTY; exposure clipped 40%-100%','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':'Official NIFTY 50 Total Return Index','buy_hold_tri_cagr':bench,'full':m,'parameters':{'target_vol':TARGET_VOL,'min_exposure':MIN_EXP,'max_exposure':MAX_EXP,'lookback_days':LOOKBACK,'rebalance':'weekly','min_change':0.05,'cost':COST,'slippage':SLIPPAGE},'lookahead':'none; previous-close realized volatility and next-session TRI returns','failure_analysis_nifty_windows':failure_analysis(d)}
    json.dump(out,open('nifty_v11_voltarget_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
