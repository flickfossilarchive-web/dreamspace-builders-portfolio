import json, math
from pathlib import Path
import numpy as np, pandas as pd, requests

DATA=Path('trading/data/nifty_option_history.csv'); OUT=Path('nifty_v12_tailhedge_results.json')
HEDGE=.03; CORE=.97; MONEY=.95; MIN_DTE=20; MAX_DTE=60; ROLL_COST=.001

def tri():
    payload={'cinfo':"{'name':'NIFTY 50','startDate':'01-Jan-2018','endDate':'31-Dec-2020','indexName':'NIFTY 50'}"}
    h={'Content-Type':'application/json; charset=UTF-8','X-Requested-With':'XMLHttpRequest','Referer':'https://www.niftyindices.com/reports/historical-data','User-Agent':'Mozilla/5.0 Chrome/149'}
    r=requests.post('https://www.niftyindices.com/Backpage.aspx/getTotalReturnIndexString',headers=h,json=payload,timeout=60); r.raise_for_status()
    raw=json.loads(r.json()['d']); x=pd.DataFrame(raw); x.columns=[str(c).strip() for c in x.columns]
    dc=next(c for c in x.columns if 'date' in c.lower()); vc=next(c for c in x.columns if 'total' in c.lower() and 'return' in c.lower())
    x['date']=pd.to_datetime(x[dc]); x['tri']=pd.to_numeric(x[vc],errors='coerce'); return x[['date','tri']].dropna().sort_values('date').drop_duplicates('date')

def load():
    if not DATA.exists(): raise FileNotFoundError(DATA)
    x=pd.read_csv(DATA); x['date']=pd.to_datetime(x.date); x['expiry']=pd.to_datetime(x.expiry); x['option_type']=x.option_type.astype(str).str.upper()
    for c in ['strike','close','underlying']: x[c]=pd.to_numeric(x[c],errors='coerce')
    x=x.dropna(subset=['date','expiry','strike','close','underlying']); x=x[(x.option_type=='PE')&(x.close>0)].sort_values(['date','expiry','strike'])
    if len(x)<1000: raise ValueError('Insufficient real option observations')
    return x

def run(opt, t):
    t=t.sort_values('date').copy(); opt=opt.merge(t,on='date',how='inner').sort_values('date'); dates=list(t.date)
    by={d:g for d,g in opt.groupby('date')}; eq=1.; peak=1.; held=None; entry=0.; vals=[(dates[0],eq)]; rolls=0; hedge_missing=0
    last_month=None
    for i in range(1,len(dates)):
        d=dates[i]; prev=dates[i-1]; g=by.get(d,pd.DataFrame()); pg=by.get(prev,pd.DataFrame())
        month=(d.year,d.month)
        if month!=last_month:
            cand=g.copy(); cand['dte']=(cand.expiry-d).dt.days; cand=cand[cand.dte.between(MIN_DTE,MAX_DTE)]
            if not cand.empty:
                cand['distance']=(cand.strike/cand.underlying-MONEY).abs(); p=cand.sort_values(['distance','dte']).iloc[0]
                held=(pd.Timestamp(p.expiry),float(p.strike)); entry=float(p.close); rolls+=1
            else: hedge_missing+=1
            last_month=month
        core_ret=float(t.loc[t.date==d,'tri'].iloc[0]/t.loc[t.date==prev,'tri'].iloc[0]-1)
        hret=0.0
        if held:
            ex,strike=held; q=g[(g.expiry==ex)&(g.strike==strike)]
            if not q.empty and entry>0: hret=float(q.iloc[0].close/entry-1)
            else: hedge_missing+=1
        # Hedge premium is a fixed 3% sleeve. At monthly roll, the sleeve is reset to its budget.
        daily=CORE*core_ret+HEDGE*hret-(ROLL_COST if month!=last_month or i==1 else 0.0)
        eq*=1+daily; peak=max(peak,eq); vals.append((d,eq))
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().dropna(); years=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/years)-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*math.sqrt(252)) if rr.std()>0 else 0.0,'rolls':rolls,'missing_events':hedge_missing,'observations':len(opt)}

def main():
    opt=load(); t=tri(); m=run(opt,t); years=(t.date.iloc[-1]-t.date.iloc[0]).days/365.25; bench=float((t.tri.iloc[-1]/t.tri.iloc[0])**(1/years)-1)
    out={'strategy':'V12 NIFTY 97% core + 3% systematic long put sleeve','status':'TESTED_WITH_REAL_NSE_OPTION_CLOSES','period':f"{t.date.iloc[0].date()} to {t.date.iloc[-1].date()}",'option_source':'NSE historical F&O bhavcopy archives','benchmark_source':'NSE Indices NIFTY 50 TRI','rules':{'hedge_budget':HEDGE,'target_moneyness':MONEY,'dte':[MIN_DTE,MAX_DTE],'roll':'monthly first eligible trading date','roll_cost':ROLL_COST},'result':m,'benchmark_tri_cagr':bench,'lookahead':'none: contract selected at close and marked on subsequent sessions','theoretical_pricing':False}
    OUT.write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
