import json, numpy as np, pandas as pd
from test_nifty_v10_regime import data

COST=0.0005; SLIPPAGE=0.0005
TARGET_VOL=0.15; MIN_EXP=0.40; MAX_EXP=1.00; LOOKBACK=20

# V13: fixed, pre-declared risk architecture. No parameter fitting on test data.
# Layer 1: volatility budget. Layer 2: trend/crash brake. Layer 3: weekly hysteresis.
def run(d):
    c=d.Close.astype(float); tri=d.TRI.astype(float); r=tri.pct_change().fillna(0)
    rv=c.pct_change().rolling(LOOKBACK).std()*np.sqrt(252)
    ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); m63=c.pct_change(63); m252=c.pct_change(252)
    eq=1.; exp=1.; vals=[]; exposures=[]; trades=0
    for i in range(1,len(d)):
        p=i-1
        if not all(np.isfinite(z) for z in [rv.iloc[p],ma50.iloc[p],ma200.iloc[p],m63.iloc[p],m252.iloc[p],d.VIX.iloc[p]]):
            eq*=1+r.iloc[i]; vals.append((d.index[i],eq)); exposures.append(exp); continue
        vol_exp=float(np.clip(TARGET_VOL/rv.iloc[p],MIN_EXP,MAX_EXP)) if rv.iloc[p]>0 else MAX_EXP
        price=float(c.iloc[p]); vix=float(d.VIX.iloc[p]); x63=float(m63.iloc[p]); x252=float(m252.iloc[p])
        severe=(price<ma200.iloc[p] and x63<0 and x252<0) or vix>=35
        warning=(price<ma200.iloc[p] and x63<0) or (ma50.iloc[p]<ma200.iloc[p] and x63<0) or vix>=30
        recovery=(price>=ma50.iloc[p] and x63>0 and x252>0 and vix<30)
        # Trend brake multiplies the volatility budget; it never creates leverage.
        if severe: target=max(MIN_EXP, min(vol_exp,0.50))
        elif warning: target=max(MIN_EXP, min(vol_exp,0.75))
        elif recovery: target=vol_exp
        else: target=vol_exp
        # Crash-gap brake: after an extreme prior close-to-close loss, cap the next session.
        if r.iloc[p] <= -0.04: target=min(target,0.50)
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and abs(target-exp)>=0.05:
            eq*=max(0,1-abs(target-exp)*(COST+SLIPPAGE)); exp=target; trades+=1
        eq*=1+exp*r.iloc[i]; vals.append((d.index[i],eq)); exposures.append(exp)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    m={'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'avg_exposure':float(np.mean(exposures))}
    return s,m

def period(s,a,b):
    x=s.loc[a:b]
    if len(x)<2:return {}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    windows=[('2008','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2015-2016','2015-01-01','2016-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025-2026','2025-01-01',str(d.index[-1].date()))]
    out={'strategy':'V13 fixed volatility-budget core with trend/crash brake; no leverage','benchmark':'Official NIFTY 50 Total Return Index','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'windows':[{'name':n,'start':a,'end':b,**period(s,a,b)} for n,a,b in windows],'parameters':{'target_vol':TARGET_VOL,'lookback':LOOKBACK,'min_exposure':MIN_EXP,'max_exposure':MAX_EXP,'warning_cap':0.75,'severe_cap':0.50,'gap_cap':0.50,'rebalance':'weekly','minimum_change':0.05,'cost':COST,'slippage':SLIPPAGE},'lookahead':'none; signals use previous close and next-session TRI return'}
    json.dump(out,open('nifty_v13_core_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
