# Rerun corrected walk-forward validation from the verified no-look-ahead engine.
import io,json,urllib.request
import numpy as np,pandas as pd
STOCKS=['lt','bhartiartl','hcltech','maruti','axisbank','sunpharma','titan','m&m','tatasteel','hindalco','cipla']
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
P={'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}
def load(s):
 d=pd.read_csv(io.BytesIO(urllib.request.urlopen(BASE+s+'.csv',timeout=60).read())); d['Date']=pd.to_datetime(d.Date); return d.sort_values('Date').drop_duplicates('Date').set_index('Date')
def signal(d,j,p):
 if j<1:return False,np.nan
 x=d.iloc[:j]; c=x.Close.astype(float); h=x.High.astype(float); v=x.Volume.astype(float); l=x.Low.astype(float); sma=c.rolling(p['sma']).mean().iloc[-1]; hi=h.shift(1).rolling(p['breakout']).max().iloc[-1]; tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr=tr.rolling(p['atr']).mean().iloc[-1]; rv=v.iloc[-1]/v.rolling(p['vol']).mean().iloc[-1]; rs=c.pct_change(p['rs']).iloc[-1]; return bool(c.iloc[-1]>sma and c.iloc[-1]>hi and rv>p['vol_mult'] and atr/c.iloc[-1]>.01 and atr/c.iloc[-1]<.08 and rs>0),float(atr)
def run(data,start,end):
 idx=pd.date_range(start,end,freq='B'); n=len(STOCKS); cash={s:1/n for s in STOCKS}; shares={s:0. for s in STOCKS}; stops={s:None for s in STOCKS}; eq=[]
 for dt in idx:
  total=0.
  for s,d in data.items():
   if dt not in d.index: total+=cash[s] if shares[s]==0 else shares[s]*d.Close.loc[:dt].iloc[-1]; continue
   j=d.index.get_loc(dt); o=float(d.Open.iloc[j]); c=float(d.Close.iloc[j]); l=float(d.Low.iloc[j]);
   if shares[s]:
    ok,a=signal(d,j,P); stops[s]=max(stops[s],float(d.Close.iloc[j-1])-P['stop_atr']*a) if np.isfinite(a) else stops[s]; prev_c=float(d.Close.iloc[j-1]); prev_sma=float(d.Close.rolling(P['sma']).mean().iloc[j-1]) if j>0 else np.nan
    if l<=stops[s] or (np.isfinite(prev_sma) and prev_c<prev_sma): cash[s]=shares[s]*(o*(1-P['slip']) if o<stops[s] else stops[s])*(1-P['cost']); shares[s]=0.; stops[s]=None
   ok,a=signal(d,j,P)
   if not shares[s] and ok and np.isfinite(a): px=o*(1+P['slip']); shares[s]=cash[s]/px; cash[s]=0.; stops[s]=px-P['stop_atr']*a
   total+=cash[s] if not shares[s] else shares[s]*c
  eq.append((dt,total))
 e=pd.Series(dict(eq)); years=(e.index[-1]-e.index[0]).days/365.25; dr=e.pct_change().fillna(0); return {'start':str(start.date()),'end':str(end.date()),'cagr':float(e.iloc[-1]**(1/years)-1),'total_return':float(e.iloc[-1]-1),'max_drawdown':float((e/e.cummax()-1).min()),'sharpe':float(dr.mean()/dr.std()*np.sqrt(252)),'final_equity':float(e.iloc[-1])}
def main():
 data={s:load(s) for s in STOCKS}; common_end=min(d.index[-1] for d in data.values()); windows=[('2007-08-27','2012-12-31','2013-01-01','2016-12-31'),('2011-01-03','2016-12-30','2017-01-03','2020-12-31'),('2015-01-02','2020-12-31','2021-01-01','2023-12-29'),('2018-01-02','2023-12-29','2024-01-02',str(common_end.date()))]; out=[]
 for tr0,tr1,te0,te1 in windows: out.append({'train_start':tr0,'train_end':tr1,'test':run(data,pd.Timestamp(te0),pd.Timestamp(te1))})
 tests=[x['test'] for x in out]; outj={'method':'fixed-parameter rolling walk-forward with no look-ahead; test-day decisions use prior completed bar and execute at next open','windows':out,'summary':{'windows':len(tests),'profitable_windows':sum(x['cagr']>0 for x in tests),'median_cagr':float(np.median([x['cagr'] for x in tests])),'worst_cagr':float(min(x['cagr'] for x in tests)),'median_drawdown':float(np.median([x['max_drawdown'] for x in tests]))}}; json.dump(outj,open('portfolio_v6_walk_forward.json','w'),indent=2); print(json.dumps(outj,indent=2))
if __name__=='__main__':main()
