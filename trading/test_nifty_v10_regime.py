import json
from datetime import timedelta
import numpy as np
import pandas as pd
import requests
import yfinance as yf

TICKER='^NSEI'; VIX='^INDIAVIX'; START='2007-09-17'; COST=0.0005; SLIPPAGE=0.0005
BASE='https://niftyindices.com'; HEADERS={'User-Agent':'Mozilla/5.0','Referer':'https://www.niftyindices.com/','Content-Type':'application/json; charset=UTF-8'}

def load(t):
    d=yf.download(t,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(t,axis=1,level=1)
    return d

def tri_history(start,end):
    out=[]; cur=pd.Timestamp(start).date(); end=pd.Timestamp(end).date()
    while cur<=end:
        ce=min(cur+timedelta(days=365),end); info={'name':'NIFTY 50','startDate':cur.strftime('%d-%b-%Y'),'endDate':ce.strftime('%d-%b-%Y'),'indexName':'NIFTY 50'}
        r=requests.post(BASE+'/BackPage/getTotalReturnIndexString',json={'cinfo':str(info).replace('"',"'")},headers=HEADERS,timeout=30); r.raise_for_status(); x=r.json(); x=x.get('d',x) if isinstance(x,dict) else x
        if isinstance(x,str): x=json.loads(x)
        if isinstance(x,list): out.extend(x)
        cur=ce+timedelta(days=1)
    rows=[]
    for x in out:
        if not isinstance(x,dict): continue
        dt=x.get('HistoricalDate') or x.get('DATE') or x.get('Date'); val=None
        for k,v in x.items():
            ku=str(k).upper().replace(' ','')
            if ('TR' in ku and 'INDEX' in ku) or ku in ('TRI','TOTALRETURNINDEX','TOTALRETURN'):
                try: val=float(str(v).replace(',','')); break
                except Exception: pass
        if dt is not None and val is not None and np.isfinite(val): rows.append((pd.to_datetime(dt,dayfirst=True),val))
    tri=pd.DataFrame(rows,columns=['Date','TRI']).drop_duplicates('Date').set_index('Date').sort_index()
    if len(tri)<1000: raise RuntimeError('Insufficient official TRI history')
    return tri

def data():
    p=load(TICKER)[['Open','Close']].dropna(); p.index=pd.to_datetime(p.index).tz_localize(None)
    v=load(VIX)
    if len(v):
        if isinstance(v.columns,pd.MultiIndex): v=v.xs(VIX,axis=1,level=1)
        p['VIX']=v.Close.reindex(p.index).ffill()
    else: p['VIX']=np.nan
    p.VIX=p.VIX.fillna(p.VIX.median()); return p.join(tri_history(p.index[0],p.index[-1]),how='inner').dropna(subset=['TRI'])

def target_exposure(c,ma50,ma200,m63,m252,vix,prev):
    # Fixed, pre-declared regime map. No parameter is chosen from test results.
    severe=(c<ma200 and m63<0 and m252<0) or vix>=35
    warning=(c<ma200 and m63<0) or (ma50<ma200 and m63<0) or vix>=30
    recovery=(c>=ma50 and m63>0 and m252>0 and vix<30)
    if severe: return 0.40
    if warning: return 0.70
    if recovery: return 1.00
    return prev

def run(d):
    c=d.Close.astype(float); tri=d.TRI.astype(float); r=tri.pct_change().fillna(0); ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); m63=c.pct_change(63); m252=c.pct_change(252)
    eq=1.; peak=1.; exp=1.; vals=[]; trades=0; exposures=[]
    for i in range(1,len(d)):
        p=i-1; q=[ma50.iloc[p],ma200.iloc[p],m63.iloc[p],m252.iloc[p],d.VIX.iloc[p]]
        if not all(np.isfinite(x) for x in q): eq*=1+r.iloc[i]; peak=max(peak,eq); vals.append((d.index[i],eq)); exposures.append(exp); continue
        target=target_exposure(c.iloc[p],*q,dummy if False else 0) if False else None
        m50,m200,x63,x252,vix=q; target=target_exposure(c.iloc[p],m50,m200,x63,x252,vix,exp)
        # Weekly rebalance only. Recovery is deliberately gradual: warning->full only when recovery conditions are confirmed.
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and target!=exp:
            turnover=abs(target-exp); eq*=max(0,1-turnover*(COST+SLIPPAGE)); exp=target; trades+=1
        eq*=1+exp*r.iloc[i]; peak=max(peak,eq); vals.append((d.index[i],eq)); exposures.append(exp)
    s=pd.Series(dict(vals)).sort_index(); rr=s.pct_change().fillna(0); yrs=(s.index[-1]-s.index[0]).days/365.25
    return s,{'cagr':float(s.iloc[-1]**(1/yrs)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades,'avg_exposure':float(np.mean(exposures))}

def win(s,a,b):
    x=s.loc[a:b]
    if len(x)<2:return {}
    x=x/x.iloc[0]; rr=x.pct_change().fillna(0); yrs=(x.index[-1]-x.index[0]).days/365.25
    return {'cagr':float(x.iloc[-1]**(1/yrs)-1),'max_drawdown':float((x/x.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252))}

def main():
    d=data(); s,m=run(d); tri=d.TRI; yrs=(tri.index[-1]-tri.index[0]).days/365.25; bench=float((tri.iloc[-1]/tri.iloc[0])**(1/yrs)-1)
    ws=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[{'start':a,'end':b,**win(s,a,b)} for a,b in ws]
    out={'strategy':'V10 fixed defensive regime: 100% normal / 70% warning / 40% severe, gradual recovery','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'benchmark':'Official NIFTY 50 Total Return Index','buy_hold_tri_cagr':bench,'full':m,'oos':oos,'rules':{'severe':'price<MA200 & 63d momentum<0 & 252d momentum<0 OR VIX>=35 -> 40%','warning':'price<MA200 & 63d momentum<0 OR MA50<MA200 & 63d momentum<0 OR VIX>=30 -> 70%','recovery':'price>=MA50 & 63d momentum>0 & 252d momentum>0 & VIX<30 -> 100%','rebalance':'weekly, previous-close signal, next-session TRI return'},'cost':COST,'slippage':SLIPPAGE,'lookahead':'none; all signals use previous session data'}
    json.dump(out,open('nifty_v10_results.json','w'),indent=2); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
