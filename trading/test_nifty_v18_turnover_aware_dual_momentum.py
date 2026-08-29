import json
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'
ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}
CASH='CASH'; CASH_TICKER='^IRX'
MOM=126; VOL=60; TREND=200; LEADERS=2
DEFENSIVE_EXPOSURE=0.70
BASE_TOTAL_COST=0.0010  # 10 bps total round-trip drag per unit turnover
TURNOVER_TRIGGER=0.20   # ignore small target changes
DRIFT_TRIGGER=0.10      # force rebalance if any live weight drifts >10pp from target

def series(ticker,name):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data {name}')
    s=d['Close'] if not isinstance(d.columns,pd.MultiIndex) else d['Close']
    if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    s=pd.to_numeric(s,errors='coerce').rename(name)
    s.index=pd.to_datetime(s.index).tz_localize(None)
    return s

def cash():
    s=series(CASH_TICKER,CASH)
    rate=s.ffill().clip(lower=0)/100
    return ((1+(1+rate)**(1/252)-1).cumprod()).rename(CASH)

def data():
    p=pd.concat([series(t,n) for n,t in ASSETS.items()]+[cash()],axis=1).sort_index().ffill().dropna()
    tri=tri_history(p.index[0].date(),p.index[-1].date())
    d=p.join(tri,how='inner').dropna(subset=['TRI'])
    return d

def run(d,total_cost=BASE_TOTAL_COST):
    x=d.copy()
    for n in ASSETS:
        x[n+'_MOM']=x[n].pct_change(MOM)
        x[n+'_VOL']=x[n].pct_change().rolling(VOL).std()*np.sqrt(252)
        x[n+'_TREND']=x[n]/x[n].rolling(TREND).mean()-1
    ret=x[list(ASSETS)+[CASH]].pct_change().fillna(0)
    cur=pd.Series({'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15,'CASH':0.10},dtype=float)
    eq=1.0; vals=[]; alloc=[]; rebalances=0; turnover_total=0.0; defensive_days=0
    for i in range(1,len(x)):
        p=i-1
        monthly=i==1 or x.index[i].month!=x.index[i-1].month
        if monthly:
            mom={n:x[n+'_MOM'].iloc[p] for n in ASSETS}
            vol={n:x[n+'_VOL'].iloc[p] for n in ASSETS}
            trend={n:x[n+'_TREND'].iloc[p] for n in ASSETS}
            valid=[n for n in ASSETS if np.isfinite(mom[n]) and np.isfinite(vol[n]) and vol[n]>0 and np.isfinite(trend[n])]
            eligible=[n for n in valid if mom[n]>0 and trend[n]>0]
            ranked=sorted(eligible,key=lambda n:mom[n]/vol[n],reverse=True)[:LEADERS]
            if not ranked and valid:
                # Preserve a small risk budget only when the best asset still has positive relative momentum.
                ranked=[max(valid,key=lambda n:mom[n])]
            target=pd.Series(0.0,index=cur.index)
            if ranked:
                inv={n:1/vol[n] for n in ranked}; z=sum(inv.values())
                exposure=1.0 if x['NIFTY'].iloc[p] >= x['NIFTY'].rolling(TREND).mean().iloc[p] else DEFENSIVE_EXPOSURE
                for n in ranked: target[n]=exposure*inv[n]/z
            target[CASH]=1-target[list(ASSETS)].sum()
            turnover=float((target-cur).abs().sum())
            drift=float((target-cur).abs().max())
            if turnover>=TURNOVER_TRIGGER or drift>=DRIFT_TRIGGER or i==1:
                eq*=max(0.0,1-turnover*total_cost)
                turnover_total+=turnover; cur=target; rebalances+=1
        if cur[CASH] >= 0.999: defensive_days+=1
        alloc.append(cur.copy()); eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    m={'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':rebalances,'turnover_total':turnover_total,'avg_annual_turnover':float(turnover_total/yrs),'cash_fraction':float(defensive_days/max(1,len(s))),'avg_weights':{k:float(v) for k,v in pd.DataFrame(alloc).mean().items()}}
    return s,m

def window(s,a,b):
    x=s.loc[a:b]
    if len(x)<2:return {'cagr':None,'max_drawdown':None,'sharpe':None}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); s,m=run(d,BASE_TOTAL_COST); tri=d.TRI
    yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    costs=[]
    for bps in [0,5,10,15,20,30,50]:
        _,mm=run(d,bps/10000)
        costs.append({'total_cost_bps':bps,**mm,'beats_benchmark':mm['cagr']>bench})
    ws=[('2008-2009','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2015-2016','2015-01-01','2016-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025-2026','2025-01-01',str(d.index[-1].date()))]
    out={'strategy':'V18 turnover-aware dual momentum: positive absolute momentum + positive 200D trend, top-2 momentum/vol, inverse-vol, NIFTY trend exposure, monthly rebalance with turnover/drift hysteresis','benchmark':'Official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'cost_sensitivity':costs,'windows':[{'name':n,'start':a,'end':b,**window(s,a,b)} for n,a,b in ws],'parameters':{'momentum_days':MOM,'vol_days':VOL,'trend_days':TREND,'leaders':LEADERS,'defensive_exposure':DEFENSIVE_EXPOSURE,'turnover_trigger':TURNOVER_TRIGGER,'drift_trigger':DRIFT_TRIGGER,'base_total_cost_bps':10},'warnings':['Gold and Nasdaq are research proxies, not exact Indian execution instruments.','Cash uses U.S. T-bill proxy.','Signals use prior-day data; no look-ahead.','Parameters are fixed ex ante for this candidate; no final-period fitting.']}
    json.dump(out,open('nifty_v18_turnover_aware_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
