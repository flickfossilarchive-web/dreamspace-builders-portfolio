import json, numpy as np, pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history

START='2007-09-17'
MOM=90; TREND=200; VOL=60; REBALANCE_DAYS=21
RISK_ON=1.00; NEUTRAL=0.85; RISK_OFF=0.65
GOLD_MAX=0.20; NASDAQ_MAX=0.15; COST=0.001

def series(t,n):
    d=yf.download(t,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(n)
    s=d['Close']; s=s.iloc[:,0] if isinstance(s,pd.DataFrame) else s
    s=pd.to_numeric(s,errors='coerce').rename(n); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def data():
    r=pd.concat([series('^NSEI','NIFTY'),series('GC=F','GOLD'),series('^IXIC','NASDAQ'),series('INR=X','USDINR')],axis=1).sort_index().ffill()
    p=pd.DataFrame(index=r.index); p['NIFTY']=r.NIFTY; p['GOLD']=r.GOLD*r.USDINR; p['NASDAQ']=r.NASDAQ*r.USDINR; p['CASH']=1.
    tri=tri_history(p.index[0].date(),p.index[-1].date()); return p.join(tri,how='inner').dropna(subset=['TRI'])

def run(d,total_cost=COST):
    x=d.copy(); names=['NIFTY','GOLD','NASDAQ']
    for n in names:
        x[n+'_MOM']=x[n].pct_change(MOM)
        x[n+'_VOL']=x[n].pct_change().rolling(VOL).std()*np.sqrt(252)
        x[n+'_TREND']=x[n]/x[n].rolling(TREND).mean()-1
    ret=x[names+['CASH']].pct_change().fillna(0)
    cur=pd.Series({'NIFTY':1.,'GOLD':0.,'NASDAQ':0.,'CASH':0.}); eq=1.; vals=[]; reb=0; last=-REBALANCE_DAYS
    for i in range(1,len(x)):
        if i-last>=REBALANCE_DAYS:
            p=i-1; nm=x.NIFTY_MOM.iloc[p]; nt=x.NIFTY_TREND.iloc[p]; nv=x.NIFTY_VOL.iloc[p]
            strong=np.isfinite(nm) and np.isfinite(nt) and nm>0 and nt>0
            weak=np.isfinite(nm) and np.isfinite(nt) and (nm<0 or nt<0)
            if strong: nifty_w=RISK_ON
            elif weak: nifty_w=RISK_OFF
            else: nifty_w=NEUTRAL
            target=pd.Series(0.,index=cur.index); target.NIFTY=nifty_w
            remaining=1-nifty_w
            if remaining>0:
                candidates=[]
                for n in ['GOLD','NASDAQ']:
                    rel=x[n+'_MOM'].iloc[p]-nm if np.isfinite(x[n+'_MOM'].iloc[p]) and np.isfinite(nm) else -np.inf
                    ok=np.isfinite(x[n+'_MOM'].iloc[p]) and np.isfinite(x[n+'_TREND'].iloc[p]) and x[n+'_MOM'].iloc[p]>0 and x[n+'_TREND'].iloc[p]>0 and rel>0
                    if ok: candidates.append((rel,n))
                candidates.sort(reverse=True)
                if candidates:
                    n=candidates[0][1]; target[n]=min(remaining, GOLD_MAX if n=='GOLD' else NASDAQ_MAX)
            target.CASH=1-target[['NIFTY','GOLD','NASDAQ']].sum()
            turnover=float((target-cur).abs().sum()); eq*=max(0,1-turnover*total_cost); cur=target; reb+=1; last=i
        eq*=1+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':reb}

if __name__=='__main__':
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    out={'strategy':'V21 Adaptive NIFTY Core','benchmark_cagr':bench,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'base':m,'beats_nifty':m['cagr']>bench,'parameters':{'momentum_days':MOM,'trend_days':TREND,'vol_days':VOL,'risk_on':RISK_ON,'neutral':NEUTRAL,'risk_off':RISK_OFF,'gold_max':GOLD_MAX,'nasdaq_max':NASDAQ_MAX,'rebalance_days':REBALANCE_DAYS,'cost_bps':10}}
    json.dump(out,open('nifty_v21_results.json','w'),indent=2); print(json.dumps(out,indent=2))
