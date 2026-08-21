import json
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'
ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}
FX='INR=X'
MOM=126; VOL=60; TREND=200
MAX_RISK_ASSET=0.55
MIN_SCORE=0.0
TARGET_VOL=0.14
COST=0.0010
REBALANCE_DAYS=21
TURNOVER_TRIGGER=0.15


def series(ticker,name):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data {name}')
    s=d['Close'] if not isinstance(d.columns,pd.MultiIndex) else d['Close']
    if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    s=pd.to_numeric(s,errors='coerce').rename(name)
    s.index=pd.to_datetime(s.index).tz_localize(None)
    return s


def data():
    raw=pd.concat([series(t,n) for n,t in ASSETS.items()]+[series(FX,'USDINR')],axis=1).sort_index().ffill()
    p=pd.DataFrame(index=raw.index)
    p['NIFTY']=raw['NIFTY']; p['GOLD']=raw['GOLD']*raw['USDINR']; p['NASDAQ']=raw['NASDAQ']*raw['USDINR']
    p['CASH']=1.0
    tri=tri_history(p.index[0].date(),p.index[-1].date())
    return p.join(tri,how='inner').dropna(subset=['TRI'])


def run(d,total_cost=COST):
    x=d.copy()
    for n in ASSETS:
        x[n+'_MOM']=x[n].pct_change(MOM)
        x[n+'_VOL']=x[n].pct_change().rolling(VOL).std()*np.sqrt(252)
        x[n+'_TREND']=x[n]/x[n].rolling(TREND).mean()-1
    ret=x[list(ASSETS)+['CASH']].pct_change().fillna(0)
    cur=pd.Series({'NIFTY':0.55,'GOLD':0.15,'NASDAQ':0.15,'CASH':0.15},dtype=float)
    eq=1.; vals=[]; rebalances=0; turnover=0.; days_since=REBALANCE_DAYS
    for i in range(1,len(x)):
        p=i-1; days_since+=1
        if days_since>=REBALANCE_DAYS:
            mom={n:x[n+'_MOM'].iloc[p] for n in ASSETS}; vol={n:x[n+'_VOL'].iloc[p] for n in ASSETS}; trend={n:x[n+'_TREND'].iloc[p] for n in ASSETS}
            valid=[n for n in ASSETS if np.isfinite(mom[n]) and np.isfinite(vol[n]) and vol[n]>0 and np.isfinite(trend[n])]
            scores={n:(0.6*mom[n]+0.4*trend[n])/vol[n] for n in valid}
            eligible=[n for n in valid if mom[n]>MIN_SCORE and trend[n]>MIN_SCORE]
            target=pd.Series(0.,index=cur.index)
            if eligible:
                ranked=sorted(eligible,key=lambda n:scores[n],reverse=True)
                inv={n:1/vol[n] for n in ranked}; z=sum(inv.values()); raw={n:inv[n]/z for n in ranked}
                raw={n:min(w,MAX_RISK_ASSET) for n,w in raw.items()}; z=sum(raw.values()); raw={n:w/z for n,w in raw.items()}
                regime=1.0 if x['NIFTY'].iloc[p] > x['NIFTY'].rolling(TREND).mean().iloc[p] else 0.55
                for n,w in raw.items(): target[n]=regime*w
                # Volatility target is applied to total risky exposure using a covariance estimate.
                names=list(raw); cov=x[names].pct_change().rolling(VOL).cov().loc[x.index[p]]*252
                w=np.array([raw[n] for n in names]);
                try: port_vol=float(np.sqrt(max(0,w@cov.loc[names,names].to_numpy()@w)))
                except Exception: port_vol=0.0
                if np.isfinite(port_vol) and port_vol>0:
                    target_risk=min(regime,TARGET_VOL/port_vol)
                    for n in names: target[n]=target_risk*raw[n]
            target['CASH']=1-target[list(ASSETS)].sum()
            t=float((target-cur).abs().sum())
            if t>=TURNOVER_TRIGGER or rebalances==0:
                eq*=max(0.,1-t*total_cost); turnover+=t; cur=target; rebalances+=1; days_since=0
        eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':rebalances,'avg_annual_turnover':float(turnover/yrs)}


def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    costs=[]
    for bps in [0,5,10,15,20,30,40]:
        _,mm=run(d,bps/10000); costs.append({'bps':bps,**mm,'beats_benchmark':mm['cagr']>bench})
    out={'strategy':'V19 INR regime risk-budget: dual signal, inverse-vol capped risk budget, portfolio-vol target, 21-day rebalance, turnover gate','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'full':m,'cost_sensitivity':costs,'parameters':{'momentum_days':MOM,'vol_days':VOL,'trend_days':TREND,'target_vol':TARGET_VOL,'max_risk_asset':MAX_RISK_ASSET,'rebalance_days':REBALANCE_DAYS,'turnover_trigger':TURNOVER_TRIGGER,'base_cost_bps':10},'warnings':['Gold/Nasdaq are research proxies converted to INR using USDINR.','Cash is zero-return research cash, conservative.','Signals use prior-day data.','No final-period parameter fitting.']}
    json.dump(out,open('nifty_v19_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
