import json
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005; MOM=126; VOL=60; TREND=200
ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}; CASH='CASH'; CASH_TICKER='^IRX'

def series(ticker,name):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data {name}')
    s=d['Close'] if not isinstance(d.columns,pd.MultiIndex) else d['Close']
    if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    s=pd.to_numeric(s,errors='coerce').rename(name); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def cash():
    s=series(CASH_TICKER,CASH); rate=s.ffill().clip(lower=0)/100; return ((1+(1+rate)**(1/252)-1).cumprod()).rename(CASH)

def data():
    p=pd.concat([series(t,n) for n,t in ASSETS.items()]+[cash()],axis=1).sort_index().ffill().dropna()
    tri=tri_history(p.index[0].date(),p.index[-1].date()); d=p.join(tri,how='inner').dropna(subset=['TRI'])
    for n in ASSETS:
        d[n+'_MOM']=d[n].pct_change(MOM); d[n+'_VOL']=d[n].pct_change().rolling(VOL).std()*np.sqrt(252); d[n+'_TREND']=d[n]/d[n].rolling(TREND).mean()-1
    return d

def run(d, mom_days=MOM, vol_days=VOL, trend_days=TREND, leaders_n=2, defensive_exposure=0.70, cost=COST, slippage=SLIPPAGE, rebalance='monthly'):
    # Recompute every signal window from raw prices for genuinely independent parameter tests.
    x=d.copy()
    for n in ASSETS:
        x[n+'_MOM_T']=x[n].pct_change(mom_days)
        x[n+'_VOL_T']=x[n].pct_change().rolling(vol_days).std()*np.sqrt(252)
        x[n+'_TREND_T']=x[n]/x[n].rolling(trend_days).mean()-1
    ret=x[list(ASSETS)+[CASH]].pct_change().fillna(0)
    cur=pd.Series({'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15,'CASH':0.10}); eq=1.; vals=[]; alloc=[]; rebalances=0; defensive=0
    for i in range(1,len(x)):
        p=i-1
        new_period = i==1 or (x.index[i].month!=x.index[i-1].month if rebalance=='monthly' else x.index[i].isocalendar().week!=x.index[i-1].isocalendar().week)
        if new_period:
            mom={n:x[n+'_MOM_T'].iloc[p] for n in ASSETS}; vol={n:x[n+'_VOL_T'].iloc[p] for n in ASSETS}; trend={n:x[n+'_TREND_T'].iloc[p] for n in ASSETS}
            if all(np.isfinite(v) and v>0 for v in vol.values()) and all(np.isfinite(v) for v in mom.values()):
                ranked=sorted(ASSETS,key=lambda n:mom[n],reverse=True); leaders=[n for n in ranked if trend[n]>-0.05][:leaders_n]
                if not leaders: leaders=ranked[:1]
                inv={n:1/vol[n] for n in leaders}; z=sum(inv.values()); risk={n:inv[n]/z for n in leaders}
                exposure=1.0 if x['NIFTY'].iloc[p] >= x['NIFTY'].rolling(trend_days).mean().iloc[p] else defensive_exposure
                target=pd.Series(0.,index=cur.index)
                for n,w in risk.items(): target[n]=w*exposure
                target[CASH]=1-target[list(ASSETS)].sum()
                turnover=float((target-cur).abs().sum()); eq*=max(0,1-turnover*(cost+slippage)); cur=target; rebalances+=1
        if cur[CASH]>0.1000001: defensive+=1
        alloc.append(cur.copy()); eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    m={'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':rebalances,'defensive_fraction':float(defensive/max(1,len(s))),'avg_weights':{k:float(v) for k,v in pd.DataFrame(alloc).mean().items()}}
    return s,m

def window(s,a,b):
    x=s.loc[a:b]
    if len(x)<2:return {'cagr':None,'max_drawdown':None,'sharpe':None}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    ws=[('2008-2009','2008-01-01','2009-12-31'),('2011','2011-01-01','2011-12-31'),('2015-2016','2015-01-01','2016-12-31'),('2018','2018-01-01','2018-12-31'),('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31'),('2025-2026','2025-01-01',str(d.index[-1].date()))]
    out={'strategy':'V17 relative-momentum diversified portfolio; monthly top-2 selection; inverse-vol sizing; NIFTY trend exposure filter','benchmark':'Official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'windows':[{'name':n,'start':a,'end':b,**window(s,a,b)} for n,a,b in ws],'parameters':{'momentum_days':MOM,'vol_days':VOL,'trend_days':TREND,'leaders':2,'normal_exposure':1.0,'defensive_exposure':0.70,'rebalance':'monthly','cost':COST,'slippage':SLIPPAGE},'warnings':['GC=F and ^IXIC are research proxies, not exact Indian execution.','^IRX is a U.S. T-bill rate proxy.','No leverage; signals use prior-day data.','No final-period parameter fitting.']}
    json.dump(out,open('nifty_v17_relative_momentum_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
