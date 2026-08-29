import json, os
import numpy as np
import pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'
MOM=int(os.getenv('V18_MOM','126')); VOL=int(os.getenv('V18_VOL','60')); TREND=int(os.getenv('V18_TREND','200'))
LEADERS=int(os.getenv('V18_LEADERS','2')); DEFENSIVE=float(os.getenv('V18_DEFENSIVE','0.70'))
COST=float(os.getenv('V18_COST','0.0005')); SLIPPAGE=float(os.getenv('V18_SLIPPAGE','0.0005'))
REB=os.getenv('V18_REBALANCE','monthly'); TURNOVER_MIN=float(os.getenv('V18_TURNOVER_MIN','0.05'))
ASSETS={'NIFTY':'^NSEI','GOLD':'GC=F','NASDAQ':'^IXIC'}; USD_ASSETS={'GOLD','NASDAQ'}; CASH='CASH'

def series(ticker,name):
    d=yf.download(ticker,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'No data {name}')
    s=d['Close'] if not isinstance(d.columns,pd.MultiIndex) else d['Close']
    if isinstance(s,pd.DataFrame): s=s.iloc[:,0]
    s=pd.to_numeric(s,errors='coerce').rename(name); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def data():
    prices={n:series(t,n) for n,t in ASSETS.items()}
    fx=series('INR=X','USDINR')
    p=pd.DataFrame(prices).join(fx,how='inner').sort_index().ffill()
    for n in USD_ASSETS: p[n]=p[n]*p['USDINR']
    p=p.drop(columns=['USDINR']).dropna()
    # USD cash is deliberately not used; uninvested capital is treated as zero-return cash.
    tri=tri_history(p.index[0].date(),p.index[-1].date())
    return p.join(tri,how='inner').dropna(subset=['TRI'])

def run(d):
    x=d.copy();
    for n in ASSETS:
        x[n+'_MOM']=x[n].pct_change(MOM); x[n+'_VOL']=x[n].pct_change().rolling(VOL).std()*np.sqrt(252); x[n+'_TREND']=x[n]/x[n].rolling(TREND).mean()-1
    ret=x[list(ASSETS)].pct_change().fillna(0); cur=pd.Series({'NIFTY':0.55,'GOLD':0.20,'NASDAQ':0.15}); eq=1.; vals=[]; alloc=[]; rebalances=0
    for i in range(1,len(x)):
        p=i-1
        new_period=i==1 or (x.index[i].month!=x.index[i-1].month if REB=='monthly' else x.index[i].isocalendar().week!=x.index[i-1].isocalendar().week)
        if new_period:
            mom={n:x[n+'_MOM'].iloc[p] for n in ASSETS}; vol={n:x[n+'_VOL'].iloc[p] for n in ASSETS}; trend={n:x[n+'_TREND'].iloc[p] for n in ASSETS}
            if all(np.isfinite(v) and v>0 for v in vol.values()) and all(np.isfinite(v) for v in mom.values()):
                ranked=sorted(ASSETS,key=lambda n:mom[n],reverse=True)
                eligible=[n for n in ranked if mom[n]>0 and trend[n]>0]
                leaders=eligible[:LEADERS] or [ranked[0]]
                inv={n:1/vol[n] for n in leaders}; z=sum(inv.values()); risk={n:inv[n]/z for n in leaders}
                exposure=1.0 if x['NIFTY'].iloc[p] >= x['NIFTY'].rolling(TREND).mean().iloc[p] else DEFENSIVE
                target=pd.Series(0.,index=cur.index)
                for n,w in risk.items(): target[n]=w*exposure
                turnover=float((target-cur).abs().sum())
                if turnover>=TURNOVER_MIN or rebalances==0:
                    eq*=max(0,1-turnover*(COST+SLIPPAGE)); cur=target; rebalances+=1
        alloc.append(cur.copy()); eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':rebalances,'avg_weights':{k:float(v) for k,v in pd.DataFrame(alloc).mean().items()}}

def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    out={'strategy':'V18 INR-normalized dual-momentum, inverse-volatility, trend-confirmed, turnover-aware portfolio','benchmark':'NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_tri_cagr':bench,'full':m,'parameters':{'momentum_days':MOM,'vol_days':VOL,'trend_days':TREND,'leaders':LEADERS,'defensive_exposure':DEFENSIVE,'turnover_min':TURNOVER_MIN,'rebalance':REB,'cost':COST,'slippage':SLIPPAGE},'warnings':['Gold and Nasdaq are converted to INR using USDINR before signal/return calculation.','They remain research proxies, not exact Indian ETFs.','Uninvested cash receives zero return; this is conservative.','Signals use prior-day data.']}
    json.dump(out,open('nifty_v18_inr_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
