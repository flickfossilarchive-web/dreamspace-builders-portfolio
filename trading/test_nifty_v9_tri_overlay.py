import json
from datetime import date, timedelta
import numpy as np
import pandas as pd
import requests
import yfinance as yf

TICKER='^NSEI'; VIX='^INDIAVIX'; START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005
BASE='https://niftyindices.com'
HEADERS={'User-Agent':'Mozilla/5.0','Referer':'https://www.niftyindices.com/','Content-Type':'application/json; charset=UTF-8'}


def load(t):
    d=yf.download(t,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(t,axis=1,level=1)
    return d


def tri_history(start,end):
    out=[]; cur=pd.Timestamp(start).date(); end=end if isinstance(end,date) else pd.Timestamp(end).date()
    while cur<=end:
        chunk_end=min(cur+timedelta(days=365),end)
        cinfo={'name':'NIFTY 50','startDate':cur.strftime('%d-%b-%Y'),'endDate':chunk_end.strftime('%d-%b-%Y'),'indexName':'NIFTY 50'}
        r=requests.post(BASE+'/BackPage/getTotalReturnIndexString',json={'cinfo':str(cinfo).replace('"',"'")},headers=HEADERS,timeout=30)
        r.raise_for_status(); payload=r.json()
        if isinstance(payload,dict) and 'd' in payload: payload=payload['d']
        if isinstance(payload,str):
            try: payload=json.loads(payload)
            except Exception: payload=[]
        if isinstance(payload,list): out.extend(payload)
        cur=chunk_end+timedelta(days=1)
    if not out: raise RuntimeError('Official NIFTY 50 TRI endpoint returned no data')
    rows=[]
    for x in out:
        if not isinstance(x,dict): continue
        dt=x.get('HistoricalDate') or x.get('DATE') or x.get('Date')
        val=None
        for k,v in x.items():
            ku=str(k).upper().replace(' ','')
            if 'TR' in ku and 'INDEX' in ku or ku in ('TRI','TOTALRETURNINDEX','TOTALRETURN'):
                val=v; break
        if val is None:
            nums=[(k,v) for k,v in x.items() if k not in ('HistoricalDate','DATE','Date')]
            for k,v in nums:
                try:
                    fv=float(str(v).replace(',',''))
                    if np.isfinite(fv): val=fv; break
                except Exception: pass
        if dt is not None and val is not None:
            rows.append((pd.to_datetime(dt,dayfirst=True),float(str(val).replace(',',''))))
    tri=pd.DataFrame(rows,columns=['Date','TRI']).drop_duplicates('Date').set_index('Date').sort_index()
    if len(tri)<1000: raise RuntimeError(f'Unexpectedly short TRI history: {len(tri)} rows')
    return tri


def data():
    p=load(TICKER)[['Open','Close']].dropna().copy(); p.index=pd.to_datetime(p.index).tz_localize(None)
    v=load(VIX)
    if len(v):
        if isinstance(v.columns,pd.MultiIndex): v=v.xs(VIX,axis=1,level=1)
        p['VIX']=v.Close.reindex(p.index).ffill()
    else: p['VIX']=np.nan
    p.VIX=p.VIX.fillna(p.VIX.median())
    tri=tri_history(p.index[0].date(),p.index[-1].date())
    p=p.join(tri,how='inner').dropna(subset=['TRI'])
    return p


def run(d,max_cut=0.10):
    c=d.Close.astype(float); o=d.Open.astype(float); tri=d.TRI.astype(float)
    r=c.pct_change(); ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); mom63=c.pct_change(63); mom252=c.pct_change(252); vol20=r.rolling(20).std()*np.sqrt(252)
    cash=1.; units=0.; peak=1.; eq=[]; trades=0; last=1.
    for i in range(1,len(d)):
        p=i-1; vals=[ma50.iloc[p],ma200.iloc[p],mom63.iloc[p],mom252.iloc[p],vol20.iloc[p],d.VIX.iloc[p]]
        if not all(np.isfinite(x) for x in vals): eq.append((d.index[i],cash+units*tri.iloc[i])); continue
        m50,m200,m63,m252,vol,vix=vals
        mark=cash+units*tri.iloc[p]; peak=max(peak,mark); dd=mark/peak-1
        cut=0.0
        if c.iloc[p]<m200 and m63<0 and m252<0: cut=max_cut
        elif c.iloc[p]<m200 and m63<0: cut=max_cut*.65
        elif m50<m200 and m63<0: cut=max_cut*.35
        if vix>=35: cut=max(cut,max_cut)
        elif vix>=30: cut=max(cut,max_cut*.75)
        elif vix>=25: cut=max(cut,max_cut*.40)
        if dd<=-.15: cut=max(cut,max_cut*.75)
        elif dd<=-.10: cut=max(cut,max_cut*.40)
        target=1.0-min(max_cut,cut)
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and abs(target-last)>=.025:
            px=float(o.iloc[i]); total=cash+units*tri.iloc[p]; desired=total*target; du=desired/(px*(1+SLIPPAGE)); delta=du-units
            if delta>0: cash-=delta*px*(1+SLIPPAGE)*(1+COST); units+=delta
            elif delta<0: q=-delta; cash+=q*px*(1-SLIPPAGE)*(1-COST); units-=q
            trades+=1; last=target
        mark=cash+units*tri.iloc[i]; peak=max(peak,mark); eq.append((d.index[i],mark))
    s=pd.Series(dict(eq)).sort_index(); rr=s.pct_change().fillna(0); years=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/years)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades}


def metrics_window(eq,a,b):
    s=eq.loc[a:b]
    if len(s)<2: return {}
    rr=s.pct_change().fillna(0); years=(s.index[-1]-s.index[0]).days/365.25
    return {'cagr':float(s.iloc[-1]**(1/years)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}


def main():
    d=data(); eq,m=run(d,0.10); tri=d.TRI; years=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/years)-1)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[{'start':a,'end':b,**metrics_window(eq,a,b)} for a,b in windows]
    out={'strategy':'V9 NIFTY core + 10% maximum defensive overlay, evaluated on official NIFTY 50 TRI','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':'NIFTY 50 Total Return Index','buy_hold_tri_cagr':bench,'full':m,'oos':oos,'execution':'previous close signal, weekly next-open rebalance','cost':COST,'slippage':SLIPPAGE,'research_note':'TRI benchmark and strategy equity include reinvested dividends; signals use NIFTY price index; no OOS parameter selection.'}
    json.dump(out,open('nifty_v9_results.json','w'),indent=2); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
