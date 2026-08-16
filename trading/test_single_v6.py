import io, json, urllib.request
import numpy as np
import pandas as pd
STOCK='infy'
BASE='https://raw.githubusercontent.com/BennyThadikaran/eod2_data/main/daily/'
P={'sma':200,'breakout':20,'rs':63,'vol':20,'vol_mult':1.5,'atr':14,'stop_atr':2.0,'slip':.0015,'cost':.001}

def load(n):
    b=urllib.request.urlopen(BASE+n+'.csv',timeout=60).read()
    d=pd.read_csv(io.BytesIO(b)); d['Date']=pd.to_datetime(d.Date)
    return d.sort_values('Date').drop_duplicates('Date').set_index('Date')

def run():
    d=load(STOCK); c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); o=d.Open.astype(float); v=d.Volume.astype(float)
    sma=c.rolling(P['sma']).mean(); hi=h.shift(1).rolling(P['breakout']).max()
    atr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(P['atr']).mean()
    rv=v/v.rolling(P['vol']).mean(); rs=c.pct_change(P['rs'])
    sig=(c>sma)&(c>hi)&(rv>P['vol_mult'])&(atr/c>.01)&(atr/c<.08)&(rs>0)
    trades=[]; inpos=False; entry=stop=None
    for i in range(1,len(d)):
        if not inpos and bool(sig.iloc[i]):
            entry=o.iloc[i]*(1+P['slip']); stop=entry-P['stop_atr']*atr.iloc[i]; entry_date=d.index[i]; inpos=True
        elif inpos:
            stop=max(stop,c.iloc[i]-P['stop_atr']*atr.iloc[i])
            if l.iloc[i]<=stop or c.iloc[i]<sma.iloc[i]:
                ex=o.iloc[i]*(1-P['slip']) if o.iloc[i]<stop else stop
                r=ex/entry-1-P['cost']; trades.append((entry_date,d.index[i],r)); inpos=False
    if inpos:
        ex=c.iloc[-1]*(1-P['slip']); trades.append((entry_date,d.index[-1],ex/entry-1-P['cost']))
    tr=pd.DataFrame(trades,columns=['entry','exit','return'])
    tr['exit']=pd.to_datetime(tr['exit']); tr['entry']=pd.to_datetime(tr['entry'])
    tr['equity']=(1+tr['return']).cumprod()
    tr['year']=tr['exit'].dt.year; tr['month']=tr['exit'].dt.to_period('M').astype(str)
    years=(d.index[-1]-d.index[0]).days/365.25; total=tr['equity'].iloc[-1] if len(tr) else 1
    cagr=total**(1/years)-1 if years else 0
    dd=(tr['equity']/tr['equity'].cummax()-1).min() if len(tr) else 0
    annual=tr.groupby('year')['return'].apply(lambda x: np.prod(1+x)-1).to_dict()
    monthly=tr.groupby('month')['return'].apply(lambda x: np.prod(1+x)-1).to_dict()
    out={'stock':STOCK,'start':str(d.index[0].date()),'end':str(d.index[-1].date()),'trades':len(tr),'cagr':cagr,'total_return':total-1,'max_drawdown':dd,'win_rate':float((tr['return']>0).mean()) if len(tr) else 0,'profit_factor':float(tr.loc[tr['return']>0,'return'].sum() / -tr.loc[tr['return']<0,'return'].sum()) if (tr['return']<0).any() else float('inf'),'annual_returns':annual,'monthly_returns':monthly}
    json.dump(out,open('single_infy_results.json','w'),indent=2); tr.to_csv('single_infy_trade_ledger.csv',index=False)
    print(json.dumps(out,indent=2))
run()
