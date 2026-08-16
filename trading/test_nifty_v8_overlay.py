import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'; VIX='^INDIAVIX'; START='2000-01-01'; COST=0.0005; SLIPPAGE=0.0005


def load(t):
    d=yf.download(t,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(t,axis=1,level=1)
    return d


def data():
    d=load(TICKER)[['Open','Close']].dropna().copy(); d.index=pd.to_datetime(d.index).tz_localize(None)
    v=load(VIX)
    if len(v):
        if isinstance(v.columns,pd.MultiIndex): v=v.xs(VIX,axis=1,level=1)
        d['VIX']=v.Close.reindex(d.index).ffill()
    else: d['VIX']=np.nan
    d.VIX=d.VIX.fillna(d.VIX.median())
    return d


def run(d, max_cut):
    c=d.Close.astype(float); o=d.Open.astype(float); r=c.pct_change()
    ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); mom63=c.pct_change(63); mom252=c.pct_change(252); vol20=r.rolling(20).std()*np.sqrt(252)
    cash=1.; units=0.; peak=1.; eq=[]; trades=0; last=1.
    for i in range(1,len(d)):
        p=i-1
        vals=[ma50.iloc[p],ma200.iloc[p],mom63.iloc[p],mom252.iloc[p],vol20.iloc[p],d.VIX.iloc[p]]
        if not all(np.isfinite(x) for x in vals):
            eq.append((d.index[i],cash+units*c.iloc[i])); continue
        m50,m200,m63,m252,vol,vix=vals
        mark=cash+units*c.iloc[p]; peak=max(peak,mark); dd=mark/peak-1
        # Core is always present. Overlay only removes a limited slice of risk.
        cut=0.0
        if c.iloc[p]<m200 and m63<0 and m252<0: cut=max_cut
        elif c.iloc[p]<m200 and m63<0: cut=max_cut*.65
        elif m50<m200 and m63<0: cut=max_cut*.35
        if vix>=35: cut=max(cut,max_cut)
        elif vix>=30: cut=max(cut,max_cut*.75)
        elif vix>=25: cut=max(cut,max_cut*.40)
        if dd<=-.15: cut=max(cut,max_cut*.75)
        elif dd<=-.10: cut=max(cut,max_cut*.40)
        target=max(0.0,1.0-cut)
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and abs(target-last)>=.025:
            px=float(o.iloc[i]); total=cash+units*px; desired=total*target; du=desired/(px*(1+SLIPPAGE)); delta=du-units
            if delta>0: cash-=delta*px*(1+SLIPPAGE)*(1+COST); units+=delta
            elif delta<0: q=-delta; cash+=q*px*(1-SLIPPAGE)*(1-COST); units-=q
            trades+=1; last=target
        mark=cash+units*c.iloc[i]; peak=max(peak,mark); eq.append((d.index[i],mark))
    s=pd.Series(dict(eq)).sort_index(); rr=s.pct_change().fillna(0); years=(s.index[-1]-s.index[0]).days/365.25
    return s, {'cagr':float(s.iloc[-1]**(1/years)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades}


def bh(d):
    c=d.Close; y=(c.index[-1]-c.index[0]).days/365.25
    return float((c.iloc[-1]/c.iloc[0])**(1/y)-1)


def main():
    d=data(); bench=bh(d)
    results={}
    for cut in (0.10,0.20,0.30,0.40):
        eq,full=run(d,cut); results[str(int(cut*100))+'pct']=full
    best=max(results.items(), key=lambda kv: kv[1]['sharpe'])
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos={}
    for cut in (0.10,0.20,0.30,0.40):
        oos[str(int(cut*100))+'pct']=[{'start':a,'end':b,**run(d.loc[a:b],cut)[1]} for a,b in windows]
    out={'strategy':'V8 NIFTY core plus limited defensive overlay; overlay sizes tested independently at 10/20/30/40%','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'buy_hold_price_index_cagr':bench,'full':results,'oos':oos,'best_by_full_sharpe':best[0],'research_note':'Price-index benchmark only in this run; TRI must be added before investability decision. No parameter selection from OOS results.','execution':'previous close signal, weekly next-open rebalance','cost':COST,'slippage':SLIPPAGE}
    json.dump(out,open('nifty_v8_results.json','w'),indent=2); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
