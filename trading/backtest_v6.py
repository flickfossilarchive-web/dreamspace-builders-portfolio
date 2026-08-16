import io,json,urllib.request
import numpy as np,pandas as pd
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
STOCKS=['reliance','tcs','infy','hdfcbank','icicibank','sbin','itc','lt','bhartiartl','hcltech']
P={'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}
def load(n):
 u=BASE+n+'.csv'; b=urllib.request.urlopen(u,timeout=60).read(); d=pd.read_csv(io.BytesIO(b)); d['Date']=pd.to_datetime(d.Date); d=d.sort_values('Date').drop_duplicates('Date').set_index('Date'); return d

def test(n):
 d=load(n); c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); o=d.Open.astype(float); v=d.Volume.astype(float)
 sma=c.rolling(P['sma']).mean(); hi=h.shift(1).rolling(P['breakout']).max(); atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(P['atr']).mean(); rv=v/v.rolling(P['vol']).mean(); rs=c.pct_change(P['rs'])
 # stock-level proxy: regime uses Nifty independently in portfolio test; here stock signal is evaluated under positive trend/relative strength proxy.
 sig=(c>sma)&(c>hi)&(rv>P['vol_mult'])&(atr/c>.01)&(atr/c<.08)&(rs>0)
 trades=[]; inpos=False; entry=stop=None
 for i in range(1,len(d)):
  if not inpos and sig.iloc[i]: entry=o.iloc[i]*(1+P['slip']); stop=entry-P['stop_atr']*atr.iloc[i]; entry_date=d.index[i]; inpos=True
  elif inpos:
   stop=max(stop, c.iloc[i]-P['stop_atr']*atr.iloc[i])
   if l.iloc[i]<=stop or c.iloc[i]<sma.iloc[i]:
    ex=o.iloc[i]*(1-P['slip']) if o.iloc[i]<stop else stop; r=ex/entry-1-P['cost']; trades.append((entry_date,d.index[i],r)); inpos=False
 if inpos:
  ex=c.iloc[-1]*(1-P['slip']); trades.append((entry_date,d.index[-1],ex/entry-1-P['cost']))
 r=np.array([x[2] for x in trades]); years=(d.index[-1]-d.index[0]).days/365.25; total=np.prod(1+r) if len(r) else 1; cagr=total**(1/years)-1 if years>0 else 0; eq=np.cumprod(1+r) if len(r) else np.array([1]); dd=eq/np.maximum.accumulate(eq)-1 if len(eq) else np.array([0]); win=(r>0).mean() if len(r) else 0; pf=r[r>0].sum()/(-r[r<0].sum()) if (r<0).any() else float('inf'); return {'stock':n,'start':str(d.index[0].date()),'end':str(d.index[-1].date()),'trades':len(r),'cagr':cagr,'total_return':total-1,'max_drawdown':dd.min(),'win_rate':win,'profit_factor':pf}

out=[test(x) for x in STOCKS]
json.dump(out,open('backtest_results.json','w'),indent=2)
pd.DataFrame(out).to_csv('trade_ledger.csv',index=False)
summary=pd.DataFrame(out)
with open('BACKTEST_REPORT.md','w') as f:
 f.write('# v6 reconstructed pilot backtest\n\nThis is a stock-level signal test, not a portfolio-level investment validation. Exact historical v6 thresholds were not recoverable from prior context, so parameters are explicitly reconstructed and locked for this run.\n\n')
 f.write(summary.to_markdown(index=False))
 f.write('\n\n## Gate\nThis run cannot authorize real-money investment. Portfolio-level Nifty regime, point-in-time universe, walk-forward, Monte Carlo and paper trading remain required.\n')
print(summary.to_string(index=False))
