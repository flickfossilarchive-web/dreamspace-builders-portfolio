import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
START='2000-01-01'
COST=0.0005
SLIPPAGE=0.0005

def load_data():
    d=yf.download(TICKER,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(TICKER,axis=1,level=1)
    d=d[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    return d

def backtest(d,start=None,end=None):
    d=d.loc[start:end].copy() if start or end else d.copy()
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float); o=d.Open.astype(float)
    sma50=c.rolling(50).mean(); sma200=c.rolling(200).mean(); mom126=c.pct_change(126)
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1); atr20=tr.rolling(20).mean()
    cash=1.0; units=0.0; stop=np.nan; rows=[]; trades=[]; entry_date=None
    for i in range(1,len(d)):
        p=i-1
        vals=[sma50.iloc[p],sma200.iloc[p],mom126.iloc[p],atr20.iloc[p]]
        if not all(np.isfinite(v) for v in vals):
            rows.append((d.index[i],cash+units*float(c.iloc[i]))); continue
        prev_close=float(c.iloc[p]); prev_atr=float(atr20.iloc[p])
        target=1.0 if prev_close>float(sma200.iloc[p]) and float(sma50.iloc[p])>float(sma200.iloc[p]) and float(mom126.iloc[p])>0 else (0.5 if prev_close>float(sma200.iloc[p]) else 0.0)
        op=float(o.iloc[i]); low=float(l.iloc[i]); close=float(c.iloc[i])
        if units:
            stop=max(stop,prev_close-3.0*prev_atr)
            if low<=stop or target==0:
                exit_px=op*(1-SLIPPAGE) if op<stop else stop
                proceeds=units*exit_px*(1-COST)
                cash+=proceeds
                trades.append({'entry':str(entry_date.date()),'exit':str(d.index[i].date()),'return':float(proceeds/(cash-proceeds) - 1 if cash!=proceeds else 0)})
                units=0.0; stop=np.nan
        total=cash+units*close
        if target>0:
            desired_value=total*target
            desired_units=desired_value/(op*(1+SLIPPAGE))
            if units==0 and desired_units>0:
                spend=desired_units*op*(1+SLIPPAGE)
                cash-=spend; units=desired_units; stop=op*(1+SLIPPAGE)-3.0*prev_atr; entry_date=d.index[i]
            elif units>0:
                delta=desired_units-units
                if delta>0:
                    cash-=delta*op*(1+SLIPPAGE)
                elif delta<0:
                    cash+=(-delta)*op*(1-SLIPPAGE)*(1-COST)
                units=desired_units
        elif units==0:
            pass
        rows.append((d.index[i],cash+units*close))
    eq=pd.Series(dict(rows)).sort_index(); dr=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    cagr=eq.iloc[-1]**(1/years)-1 if years>0 and eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sharpe=dr.mean()/dr.std()*np.sqrt(252) if dr.std() else 0
    return {'equity':eq,'cagr':float(cagr),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float(dd),'sharpe':float(sharpe),'trades':len(trades)}

def buy_hold(d):
    c=d.Close.astype(float); years=(c.index[-1]-c.index[0]).days/365.25; r=c.iloc[-1]/c.iloc[0]-1
    return {'total_return':float(r),'cagr':float((1+r)**(1/years)-1)}

def main():
    d=load_data(); full=backtest(d); bh=buy_hold(d)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        r=backtest(d,a,b); oos.append({'start':a,'end':b,'cagr':r['cagr'],'max_drawdown':r['max_drawdown'],'sharpe':r['sharpe'],'trades':r['trades']})
    result={'strategy':'NIFTY 50 regime + momentum + ATR risk control V1 fixed cash accounting','ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'execution':'prior completed daily bar decisions; next-open execution','cost':COST,'slippage':SLIPPAGE,'full':{k:full[k] for k in ['cagr','total_return','max_drawdown','sharpe','trades']},'buy_and_hold_price_index':bh,'out_of_sample_windows':oos,'note':'Fixed cash accounting bug from V1: exits now return proceeds to cash instead of overwriting existing cash.'}
    json.dump(result,open('nifty_v1_fixed_results.json','w'),indent=2)
    pd.DataFrame({'date':full['equity'].index.astype(str),'equity':full['equity'].values}).to_csv('nifty_v1_fixed_equity.csv',index=False)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
