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
 d=load(TICKER)[['Open','High','Low','Close']].dropna().copy(); d.index=pd.to_datetime(d.index).tz_localize(None)
 v=load(VIX)
 if len(v):
  if isinstance(v.columns,pd.MultiIndex): v=v.xs(VIX,axis=1,level=1)
  d['VIX']=v.Close.reindex(d.index).ffill()
 else: d['VIX']=np.nan
 d.VIX=d.VIX.fillna(d.VIX.median())
 if d.index.duplicated().any() or (d[['Open','High','Low','Close']]<=0).any().any(): raise ValueError('bad data')
 return d

def run(d):
 c=d.Close.astype(float); o=d.Open.astype(float); r=c.pct_change()
 ma50=c.rolling(50).mean(); ma200=c.rolling(200).mean(); mom63=c.pct_change(63); mom252=c.pct_change(252); vol20=r.rolling(20).std()*np.sqrt(252)
 cash=1.; units=0.; peak=1.; eq=[]; trades=0; last=1.
 for i in range(1,len(d)):
  p=i-1; vals=[ma50.iloc[p],ma200.iloc[p],mom63.iloc[p],mom252.iloc[p],vol20.iloc[p],d.VIX.iloc[p]]
  mark=cash+units*c.iloc[p]; peak=max(peak,mark); dd=mark/peak-1
  if not all(np.isfinite(x) for x in vals): eq.append((d.index[i],cash+units*c.iloc[i])); continue
  m50,m200,m63,m252,vol,vix=vals
  # Default is near buy-and-hold. De-risk only when multiple independent warnings agree.
  target=1.0
  if c.iloc[p]<m200 and m63<0 and m252<0: target=.35
  elif c.iloc[p]<m200 and m63<0: target=.65
  elif m50<m200 and m63<0: target=.75
  if vix>=35: target=min(target,.25)
  elif vix>=30: target=min(target,.50)
  elif vix>=25: target=min(target,.75)
  if dd<=-.15: target=min(target,.50)
  elif dd<=-.10: target=min(target,.75)
  # Re-enter only after trend recovery; never require perfect timing.
  weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
  if weekly and abs(target-last)>=.05:
   px=float(o.iloc[i]); total=cash+units*px; desired=total*target; du=desired/(px*(1+SLIPPAGE)); delta=du-units
   if delta>0: cash-=delta*px*(1+SLIPPAGE)*(1+COST); units+=delta
   elif delta<0: q=-delta; cash+=q*px*(1-SLIPPAGE)*(1-COST); units-=q
   trades+=1; last=target
  mark=cash+units*c.iloc[i]; peak=max(peak,mark); eq.append((d.index[i],mark))
 s=pd.Series(dict(eq)).sort_index(); rr=s.pct_change().fillna(0); years=(s.index[-1]-s.index[0]).days/365.25
 return s,{'cagr':float(s.iloc[-1]**(1/years)-1),'total_return':float(s.iloc[-1]-1),'max_drawdown':float((s/s.cummax()-1).min()),'sharpe':float(rr.mean()/rr.std()*np.sqrt(252)),'trades':trades}

def bh(d):
 c=d.Close; y=(c.index[-1]-c.index[0]).days/365.25; return float((c.iloc[-1]/c.iloc[0])**(1/y)-1)

def main():
 d=data(); eq,full=run(d); bench=bh(d); windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]; oos=[]
 for a,b in windows:
  x=run(d.loc[a:b])[1]; oos.append({'start':a,'end':b,**x})
 score=20*min(max(full['cagr']/.12,0),1)+20*min(max(full['sharpe'],0),1)+15*min(max(1+full['max_drawdown']/.20,0),1)+10*min(max(full['cagr']/max(bench,1e-9),0),1)+10*sum(x['cagr']>0 for x in oos)/3+10*min(max(np.mean([x['sharpe'] for x in oos])/.8,0),1)+15*min(max(np.mean([x['cagr'] for x in oos])/.10,0),1)
 out={'strategy':'V7 adaptive near-core exposure: default full participation, multi-confirmation crash de-risking, VIX shock filter, drawdown governor','data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'full':full,'buy_hold_price_index_cagr':bench,'oos':oos,'research_score_100':round(float(score),2),'execution':'previous close signal, weekly next-open rebalance','cost':COST,'slippage':SLIPPAGE}
 json.dump(out,open('nifty_v7_results.json','w'),indent=2); pd.DataFrame({'date':eq.index.astype(str),'equity':eq.values}).to_csv('nifty_v7_equity.csv',index=False); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
