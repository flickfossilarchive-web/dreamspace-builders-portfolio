import json, numpy as np, pandas as pd
import yfinance as yf
from test_nifty_v10_regime import tri_history
START='2007-09-17'; MOM=252; TREND=200; GOLD_MOM=126; REBALANCE_DAYS=21; COST=0.001
RISK_ON_NIFTY=1.0; NEUTRAL_NIFTY=0.70; NEUTRAL_GOLD=0.30; RISK_OFF_NIFTY=0.30; RISK_OFF_GOLD=0.50

def series(t,n):
    d=yf.download(t,start=START,auto_adjust=False,progress=False)
    if d is None or d.empty: raise RuntimeError(f'missing {n}')
    s=d['Close']; s=s.iloc[:,0] if isinstance(s,pd.DataFrame) else s
    s=pd.to_numeric(s,errors='coerce').rename(n); s.index=pd.to_datetime(s.index).tz_localize(None); return s

def data():
    r=pd.concat([series('^NSEI','NIFTY'),series('GC=F','GOLD'),series('INR=X','USDINR')],axis=1).sort_index().ffill()
    p=pd.DataFrame(index=r.index); p['NIFTY']=r.NIFTY; p['GOLD']=r.GOLD*r.USDINR; p['CASH']=1.0
    tri=tri_history(p.index[0].date(),p.index[-1].date()); return p.join(tri,how='inner').dropna(subset=['TRI'])

def run(d,total_cost=COST):
    x=d.copy(); x['MOM']=x.NIFTY.pct_change(MOM); x['TREND']=x.NIFTY/x.NIFTY.rolling(TREND).mean()-1; x['GOLD_MOM']=x.GOLD.pct_change(GOLD_MOM)
    ret=x[['NIFTY','GOLD','CASH']].pct_change().fillna(0); cur=pd.Series({'NIFTY':1.0,'GOLD':0.0,'CASH':0.0}); eq=1.0; vals=[]; last=-REBALANCE_DAYS
    for i in range(1,len(x)):
        if i-last>=REBALANCE_DAYS:
            p=i-1; mom=float(x.MOM.iloc[p]); trend=float(x.TREND.iloc[p]); goldmom=float(x.GOLD_MOM.iloc[p])
            if np.isfinite(mom) and np.isfinite(trend) and mom>0 and trend>0:
                target=pd.Series({'NIFTY':RISK_ON_NIFTY,'GOLD':0.0,'CASH':0.0})
            elif np.isfinite(trend) and trend>0:
                g=NEUTRAL_GOLD if np.isfinite(goldmom) and goldmom>0 else 0.0; target=pd.Series({'NIFTY':1.0-g,'GOLD':g,'CASH':0.0})
            else:
                g=RISK_OFF_GOLD if np.isfinite(goldmom) and goldmom>0 else 0.30; target=pd.Series({'NIFTY':RISK_OFF_NIFTY,'GOLD':g,'CASH':1.0-RISK_OFF_NIFTY-g})
            turnover=float((target-cur).abs().sum()); eq*=max(0.0,1.0-turnover*total_cost); cur=target; last=i
        eq*=1.0+float((cur*ret.iloc[i]).sum()); vals.append((x.index[i],eq))
    s=pd.Series(dict(vals)); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'rebalances':int(last//REBALANCE_DAYS+1)}

if __name__=='__main__':
    d=data(); _,m=run(d); print(json.dumps(m,indent=2))
