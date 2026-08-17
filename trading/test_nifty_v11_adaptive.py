import json
import numpy as np
import pandas as pd
from test_nifty_v10_regime import data

COST=0.0005
SLIPPAGE=0.0005

# V11-A: transparent adaptive exposure. All rules are fixed before evaluation.
def score(row):
    trend = 1.0 if row.c > row.ma200 else 0.0
    momentum = 1.0 if row.m63 > 0 and row.m252 > 0 else (0.5 if row.m63 > 0 else 0.0)
    vol = 1.0 if row.vix < row.vix_q50 else (0.5 if row.vix < row.vix_q80 else 0.0)
    breadth = row.breadth
    crash = 0.0 if (row.ret5 < -0.06 and row.rv20 > row.rv20_q80) else (0.5 if row.ret10 < -0.08 else 1.0)
    raw = 0.30*trend + 0.20*momentum + 0.20*vol + 0.20*breadth + 0.10*crash
    return float(np.clip(0.40 + 0.60*raw, 0.40, 1.00))

def build(d):
    x=d.copy(); c=x.Close.astype(float)
    x['ma200']=c.rolling(200).mean(); x['m63']=c.pct_change(63); x['m252']=c.pct_change(252)
    x['ret5']=c.pct_change(5); x['ret10']=c.pct_change(10); x['rv20']=c.pct_change().rolling(20).std()*np.sqrt(252)
    x['vix_q50']=x.VIX.expanding(min_periods=252).quantile(.50); x['vix_q80']=x.VIX.expanding(min_periods=252).quantile(.80)
    x['rv20_q80']=x.rv20.expanding(min_periods=252).quantile(.80)
    # Breadth proxy deliberately uses only NIFTY price information available here;
    # no constituent look-through is invented. It measures multi-horizon price health.
    b=(c>c.rolling(50).mean()).astype(float)*.5+(c>c.rolling(200).mean()).astype(float)*.5
    x['breadth']=b
    return x

def run(x):
    tri=x.TRI.astype(float); r=tri.pct_change().fillna(0); eq=1.; peak=1.; exp=1.; vals=[]; exposures=[]; trades=0
    for i in range(1,len(x)):
        p=i-1
        row=x.iloc[p]
        if not np.isfinite(row.ma200) or not np.isfinite(row.vix_q80) or not np.isfinite(row.rv20_q80):
            eq*=1+r.iloc[i]; vals.append((x.index[i],eq)); exposures.append(exp); continue
        target=score(row)
        weekly=(i==1 or x.index[i].isocalendar().week!=x.index[i-1].isocalendar().week or x.index[i].year!=x.index[i-1].year)
        if weekly and abs(target-exp)>=0.05:
            eq*=max(0,1-abs(target-exp)*(COST+SLIPPAGE)); exp=target; trades+=1
        eq*=1+exp*r.iloc[i]; peak=max(peak,eq); vals.append((x.index[i],eq)); exposures.append(exp)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); years=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/years)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'avg_exposure':float(np.mean(exposures))}

def main():
    d=build(data()); s,m=run(d); tri=d.TRI; years=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/years)-1)
    out={'strategy':'V11-A transparent adaptive risk score: trend + momentum + volatility + price-health breadth proxy + crash acceleration','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':'Official NIFTY 50 Total Return Index','buy_hold_tri_cagr':bench,'full':m,'lookahead':'none; previous-close signals and next-session TRI returns','rules':'Fixed weights 30/20/20/20/10; exposure 40%-100%; weekly rebalance; 5 percentage-point minimum change','note':'Breadth is explicitly a price-health proxy because constituent-level history is not assumed. This prevents inventing unavailable breadth data.'}
    json.dump(out,open('nifty_v11_adaptive_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
