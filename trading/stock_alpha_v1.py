"""PIT Nifty-500 cross-sectional alpha research."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,pandas as pd,yfinance as yf
PUBLIC={"press_release","circular","merger"}

def load_membership(path):
 x=pd.read_csv(path);x=x[x.source.isin(PUBLIC)].copy();x.valid_from=pd.to_datetime(x.valid_from);x.valid_to=pd.to_datetime(x.valid_to);return x

def fetch_prices(symbols,start,end):
 out={}
 for i in range(0,len(symbols),40):
  batch=symbols[i:i+40];d=yf.download([s+".NS" for s in batch],start=start,end=end,auto_adjust=True,progress=False,group_by="column",threads=True)
  if d.empty:continue
  close=d["Close"] if isinstance(d.columns,pd.MultiIndex) else d
  if isinstance(close,pd.Series):close=close.to_frame()
  for col in close.columns:out[str(col).replace(".NS","")]=close[col].dropna()
  time.sleep(.2)
 return pd.DataFrame(out).sort_index()

def stats(r):
 r=r.dropna();years=len(r)/252
 eq=(1+r).cumprod();dd=float((eq/eq.cummax()-1).min()) if len(r) else np.nan
 return {"cagr":float((1+r).prod()**(1/years)-1) if years else np.nan,"sharpe":float(np.sqrt(252)*r.mean()/r.std()) if len(r)>1 and r.std()>0 else np.nan,"max_drawdown":dd,"days":int(len(r))}

def backtest(px,mem,cost=.002):
 dates=px.index;rebal=dates.to_series().groupby(dates.to_period("M")).last().values;port=pd.Series(np.nan,index=dates);prev={};turnover=0
 for d in rebal:
  d=pd.Timestamp(d);hist=px.loc[:d].iloc[:-1]
  if len(hist)<260:continue
  eligible=[]
  for s in px.columns:
   m=mem[mem.symbol.eq(s)]
   if not m.empty and ((m.valid_from<=d)&(m.valid_to.isna()|(m.valid_to>d))).any() and s in hist.columns:eligible.append(s)
  if len(eligible)<20:continue
  h=hist[eligible];p=h.iloc[-1]
  mom=(p/h.iloc[-253]-1).replace([np.inf,-np.inf],np.nan);short=(p/h.iloc[-22]-1).replace([np.inf,-np.inf],np.nan)
  vol=h.pct_change().iloc[-63:].std()*np.sqrt(252);trend=p/h.iloc[-201]-1
  score=pd.concat([mom.rename("mom"),short.rename("short"),(-vol).rename("lowvol"),trend.rename("trend")],axis=1).dropna()
  if len(score)<20:continue
  z=(score-score.mean())/score.std(ddof=0).replace(0,np.nan);z["score"]=.4*z.mom+.2*z.short+.2*z.trend+.2*z.lowvol
  picks=z.score.nlargest(20).index;w=pd.Series(0.,index=px.columns);w.loc[picks]=1/20
  turn=sum(abs(w.get(s,0)-prev.get(s,0)) for s in set(w.index)|set(prev));turnover+=float(turn);prev=w.to_dict()
  nxt=dates[dates>d];end=nxt[-1] if len(nxt) else dates[-1];seg=px.loc[d:end].pct_change().iloc[1:]
  daily=(seg*w).sum(axis=1);daily.iloc[0]-=cost*turn;port.loc[daily.index]=daily
 return port.dropna(),turnover

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--membership',default='data/pit/index_membership_history.csv');ap.add_argument('--out',default='data/stock_alpha_v1');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 mem=load_membership(a.membership);symbols=sorted(mem.symbol.unique());px=fetch_prices(symbols,'2014-01-01','2026-08-01');px.to_csv(out/'prices.csv');port,turn=backtest(px,mem)
 result={'strategy':'PIT Nifty500 Cross-Sectional Alpha V1','cost_bps':20,'universe_rule':'public press-release/circular/merger membership only','top_n':20,'rebalance':'monthly','stats':stats(port),'turnover_one_way_sum':turn,'price_source':'Yahoo Finance adjusted close research data'}
 (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
