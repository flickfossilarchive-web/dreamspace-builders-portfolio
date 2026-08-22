from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np,pandas as pd,yfinance as yf
PUBLIC={"press_release","circular","merger"}

def load_membership(path):
 x=pd.read_csv(path); x=x[x.source.isin(PUBLIC)].copy(); x.valid_from=pd.to_datetime(x.valid_from); x.valid_to=pd.to_datetime(x.valid_to); return x

def fetch_prices(symbols,start,end):
 out={}
 for i in range(0,len(symbols),40):
  batch=symbols[i:i+40]; d=yf.download([s+".NS" for s in batch],start=start,end=end,auto_adjust=True,progress=False,group_by="column",threads=True)
  if d.empty: continue
  close=d["Close"] if isinstance(d.columns,pd.MultiIndex) else d
  if isinstance(close,pd.Series): close=close.to_frame()
  for col in close.columns: out[str(col).replace(".NS","")]=close[col].dropna()
  time.sleep(.2)
 return pd.DataFrame(out).sort_index()

def base_backtest(px,mem,cost=.002,top_n=20):
 dates=px.index; rebal=dates.to_series().groupby(dates.to_period("M")).last().values
 raw=pd.Series(np.nan,index=dates); rebalance_cost=pd.Series(0.,index=dates); prev={}; turnover=0.; coverage=[]
 for d in rebal:
  d=pd.Timestamp(d); hist=px.loc[:d].iloc[:-1]
  if len(hist)<260: continue
  eligible=[]
  for s in px.columns:
   m=mem[mem.symbol.eq(s)]
   if not m.empty and ((m.valid_from<=d)&(m.valid_to.isna()|(m.valid_to>d))).any(): eligible.append(s)
  if len(eligible)<top_n: continue
  h=hist[eligible]; p=h.iloc[-1]
  mom=(p/h.iloc[-253]-1); short=(p/h.iloc[-22]-1); vol=h.pct_change().iloc[-63:].std()*np.sqrt(252); trend=p/h.iloc[-201]-1
  score=pd.concat([mom.rename("mom"),short.rename("short"),(-vol).rename("lowvol"),trend.rename("trend")],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
  if len(score)<top_n: continue
  z=(score-score.mean())/score.std(ddof=0).replace(0,np.nan); z["score"]=.4*z.mom+.2*z.short+.2*z.trend+.2*z.lowvol
  picks=z.score.nlargest(top_n).index
  w=pd.Series(0.,index=px.columns); w.loc[picks]=1/top_n
  turn=sum(abs(w.get(s,0)-prev.get(s,0)) for s in set(w.index)|set(prev)); turnover+=float(turn); prev=w.to_dict()
  nxt=dates[dates>d]
  if len(nxt)==0: continue
  seg=px.loc[d:nxt[-1]].pct_change().iloc[1:]
  if seg.empty: continue
  # Never treat an unavailable price as a zero return. Forward-fill only briefly.
  held=seg.loc[:,picks].copy(); held=held.where(held.notna())
  price_seg=px.loc[d:nxt[-1],picks].ffill(limit=5)
  seg2=price_seg.pct_change().iloc[1:]
  daily=seg2.mul(w.loc[picks],axis=1).sum(axis=1,min_count=top_n)
  daily=daily.dropna()
  if daily.empty: continue
  daily.iloc[0]-=cost*turn
  raw.loc[daily.index]=daily
  rebalance_cost.loc[daily.index[0]]=cost*turn
  coverage.extend((seg2.notna().sum(axis=1)/top_n).tolist())
 return raw.dropna(),rebalance_cost.loc[raw.dropna().index],turnover,float(np.mean(coverage) if coverage else 0.)

def apply_risk_layer(raw, costs, benchmark, target_vol=.18, regime_scale=.50, min_scale=.25, max_scale=1.0):
 idx=raw.index; b=benchmark.reindex(idx).ffill(); bm=b.pct_change(); bm200=b.rolling(200,min_periods=200).mean(); trend=(b>bm200).astype(float)
 vol=raw.rolling(63,min_periods=40).std()*np.sqrt(252); scale=(target_vol/vol).clip(lower=min_scale,upper=max_scale).shift(1).fillna(1.0)
 scale=scale*np.where(trend.shift(1).fillna(1).astype(bool),1.0,regime_scale)
 scale=pd.Series(np.clip(scale,min_scale,max_scale),index=idx)
 # Costs are incurred at rebalance; scale the portfolio exposure but never lever.
 r=raw*scale-costs*scale
 return r,scale

def metrics(r):
 r=r.dropna(); n=len(r); years=n/252
 if n==0:return {'days':0,'cagr':None,'sharpe':None,'max_drawdown':None}
 eq=(1+r).cumprod(); dd=float((eq/eq.cummax()-1).min())
 return {'days':int(n),'cagr':float(eq.iloc[-1]**(1/years)-1),'sharpe':float(np.sqrt(252)*r.mean()/r.std()) if r.std()>0 else None,'max_drawdown':dd}

def bootstrap(r,B=2000,seed=17):
 a=r.dropna().to_numpy(); rng=np.random.default_rng(seed); vals=[]; block=21
 if len(a)<252:return {'iterations':B,'positive_probability':None}
 for _ in range(B):
  x=[]
  while len(x)<len(a):
   i=int(rng.integers(0,len(a))); x.extend(a[i:min(i+block,len(a))])
  x=np.asarray(x[:len(a)]); vals.append((1+x).prod()**(252/len(x))-1)
 vals=np.asarray(vals)
 return {'iterations':B,'positive_probability':float((vals>0).mean()),'median_cagr':float(np.median(vals)),'p05_cagr':float(np.quantile(vals,.05)),'p95_cagr':float(np.quantile(vals,.95))}

def run():
 ap=argparse.ArgumentParser(); ap.add_argument('--membership',default='data/pit/index_membership_history.csv'); ap.add_argument('--out',default='data/stock_alpha_v2'); a=ap.parse_args()
 out=Path(a.out); out.mkdir(parents=True,exist_ok=True); mem=load_membership(a.membership); symbols=sorted(mem.symbol.unique()); px=fetch_prices(symbols,'2014-01-01','2026-08-01')
 raw,costs,turn,coverage=base_backtest(px,mem,cost=.002,top_n=20)
 bm=yf.download('^NSEI',start='2014-01-01',end='2026-08-01',auto_adjust=True,progress=False)['Close'];
 if isinstance(bm,pd.DataFrame): bm=bm.iloc[:,0]
 r,scale=apply_risk_layer(raw,costs,bm)
 periods={'2018':('2018-01-01','2018-12-31'),'2020':('2020-01-01','2020-12-31'),'2022':('2022-01-01','2022-12-31')}
 crisis={k:metrics(r.loc[a:b]) for k,(a,b) in periods.items()}
 result={'strategy':'PIT Nifty500 Cross-Sectional Alpha V2','rules':{'top_n':20,'rebalance':'monthly','base_cost_bps':20,'target_vol':.18,'min_exposure':.25,'max_exposure':1.0,'bear_regime_exposure':.50,'regime':'NIFTY50 below 200DMA'},'baseline':metrics(r)|{'turnover':turn,'mean_selected_price_coverage':coverage,'mean_exposure':float(scale.mean())},'cost_sensitivity':{},'crisis_periods':crisis,'bootstrap':bootstrap(r),'data_quality':{'symbols':len(symbols),'price_columns':len(px.columns),'raw_missing_fraction':float(px.isna().mean().mean())},'gate':{}}
 for bps in [20,30,50]:
  rr,cc,_,_=base_backtest(px,mem,cost=bps/10000,top_n=20); rr,_s=apply_risk_layer(rr,cc,bm); result['cost_sensitivity'][str(bps)]=metrics(rr)
 result['gate']={'cagr_gt_12pct':result['baseline']['cagr']>0.12,'sharpe_ge_1':result['baseline']['sharpe']>=1.0,'drawdown_better_than_30pct':result['baseline']['max_drawdown']>=-0.30,'bootstrap_positive_ge_95pct':result['bootstrap']['positive_probability']>=.95,'crisis_has_data':all(v['days']>0 for v in crisis.values()),'coverage_ge_99pct':coverage>=.99}
 result['investment_gate']=all(result['gate'].values())
 (out/'result.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=='__main__':run()
