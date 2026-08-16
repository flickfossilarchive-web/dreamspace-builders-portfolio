import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
START='2000-01-01'
COST=0.0005
SLIPPAGE=0.0005
TARGET_VOL=0.14


def load_data():
    d=yf.download(TICKER,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(TICKER,axis=1,level=1)
    d=d[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    if d.index.duplicated().any() or (d[['Open','High','Low','Close']]<=0).any().any(): raise ValueError('Invalid OHLC data')
    return d


def indicators(d):
    c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float)
    ret=c.pct_change()
    sma50=c.rolling(50).mean(); sma100=c.rolling(100).mean(); sma200=c.rolling(200).mean()
    vol20=ret.rolling(20).std()*np.sqrt(252)
    mom126=c.pct_change(126); mom252=c.pct_change(252)
    # RSI(5) for a small tactical mean-reversion sleeve.
    delta=c.diff(); gain=delta.clip(lower=0).rolling(5).mean(); loss=(-delta.clip(upper=0)).rolling(5).mean()
    rsi5=100-(100/(1+(gain/(loss.replace(0,np.nan)))))
    rsi5=rsi5.fillna(50)
    atr14=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1).rolling(14).mean()
    return c,sma50,sma100,sma200,vol20,mom126,mom252,rsi5,atr14


def trade(d):
    c,o=d.Close.astype(float),d.Open.astype(float)
    c,sma50,sma100,sma200,vol20,mom126,mom252,rsi5,atr14=indicators(d)
    cash=1.0; units=0.0; equity=[]; trades=[]; last_target=0.0; cooldown=0
    for i in range(1,len(d)):
        p=i-1
        vals=[sma50.iloc[p],sma100.iloc[p],sma200.iloc[p],vol20.iloc[p],mom126.iloc[p],mom252.iloc[p],rsi5.iloc[p]]
        if not all(np.isfinite(x) for x in vals):
            equity.append((d.index[i],cash+units*float(c.iloc[i]))); continue
        close=float(c.iloc[p]); op=float(o.iloc[i]); v=max(float(vol20.iloc[p]),0.06)
        above200=close>float(sma200.iloc[p]); above100=close>float(sma100.iloc[p]); trend=float(sma50.iloc[p])>float(sma200.iloc[p])
        strong=above200 and above100 and trend and float(mom126.iloc[p])>0 and float(mom252.iloc[p])>0
        neutral=above200 and (above100 or float(mom126.iloc[p])>0)
        # Core sleeve: remain heavily invested in established bull trends, scale down only as regime weakens.
        core=1.0 if strong else (0.75 if neutral else 0.0)
        # Tactical sleeve: short-term mean reversion is allowed only inside the 200-day bull regime.
        tactical=0.0
        if above200 and float(rsi5.iloc[p])<32 and float(mom126.iloc[p])>0:
            tactical=0.25
            cooldown=5
        elif cooldown>0:
            tactical=0.15
            cooldown-=1
        # During high-volatility shocks, cut risk rather than averaging down.
        vol_mult=min(1.0,TARGET_VOL/v)
        target=min(1.0,(0.75*core+0.25*tactical)*vol_mult)
        # Rebalance weekly; only use information known at previous close.
        weekly=(i==1 or d.index[i].isocalendar().week!=d.index[i-1].isocalendar().week or d.index[i].year!=d.index[i-1].year)
        if weekly and abs(target-last_target)>0.025:
            total=cash+units*op
            desired=total*target
            desired_units=desired/(op*(1+SLIPPAGE))
            delta=desired_units-units
            if delta>1e-12:
                cash-=delta*op*(1+SLIPPAGE); units+=delta; trades.append(('BUY',str(d.index[i].date()),target))
            elif delta< -1e-12:
                qty=-delta; cash+=qty*op*(1-SLIPPAGE)*(1-COST); units-=qty; trades.append(('SELL',str(d.index[i].date()),target))
            last_target=target
        equity.append((d.index[i],cash+units*float(c.iloc[i])))
    eq=pd.Series(dict(equity)).sort_index(); r=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    return eq,{'cagr':float(eq.iloc[-1]**(1/years)-1),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float((eq/eq.cummax()-1).min()),'sharpe':float(r.mean()/r.std()*np.sqrt(252)),'trades':len(trades)}


def buy_hold(d):
    c=d.Close.astype(float); years=(c.index[-1]-c.index[0]).days/365.25; ratio=c.iloc[-1]/c.iloc[0]
    return {'cagr':float(ratio**(1/years)-1),'total_return':float(ratio-1)}


def main():
    d=load_data(); eq,full=trade(d); bh=buy_hold(d)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        x=trade(d.loc[a:b])[1]; oos.append({'start':a,'end':b,**{k:x[k] for k in ['cagr','max_drawdown','sharpe','trades']}})
    result={'strategy':'NIFTY V5 regime ensemble: trend core + tactical mean reversion + volatility control','ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'execution':'previous completed daily bar; weekly next-open rebalance','cost':COST,'slippage':SLIPPAGE,'target_vol':TARGET_VOL,'full':full,'buy_and_hold_price_index':bh,'out_of_sample_windows':oos}
    json.dump(result,open('nifty_v5_results.json','w'),indent=2)
    pd.DataFrame({'date':eq.index.astype(str),'equity':eq.values}).to_csv('nifty_v5_equity.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
