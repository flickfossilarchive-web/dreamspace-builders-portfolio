import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
START='2000-01-01'
COST=0.0005
SLIPPAGE=0.0005
TARGET_VOL=0.14
MAX_EXPOSURE=1.0
MIN_EXPOSURE=0.0


def load_data():
    d=yf.download(TICKER,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(TICKER,axis=1,level=1)
    d=d[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    if d.index.duplicated().any() or (d[['Open','High','Low','Close']]<=0).any().any():
        raise ValueError('Invalid OHLC data')
    return d


def run(d):
    c=d.Close.astype(float); o=d.Open.astype(float)
    sma100=c.rolling(100).mean(); sma200=c.rolling(200).mean()
    mom126=c.pct_change(126); mom252=c.pct_change(252)
    vol=c.pct_change().rolling(20).std()*np.sqrt(252)
    month=d.index.to_period('M')
    cash=1.0; units=0.0; rows=[]; trades=[]; last_target=None
    for i in range(1,len(d)):
        p=i-1
        vals=[sma100.iloc[p],sma200.iloc[p],mom126.iloc[p],mom252.iloc[p],vol.iloc[p]]
        if not all(np.isfinite(v) for v in vals):
            rows.append((d.index[i],cash+units*float(c.iloc[i]))); continue
        new_month=i==1 or month[i]!=month[i-1]
        close=float(c.iloc[p]); op=float(o.iloc[i]); v=max(float(vol.iloc[p]),0.06)

        # Adaptive trend regime: use the 200-day trend as the primary gate,
        # while the 100-day trend and momentum determine how much risk to take.
        above200=close>float(sma200.iloc[p])
        above100=close>float(sma100.iloc[p])
        trend_confirmed=float(sma100.iloc[p])>float(sma200.iloc[p])
        momentum=float(mom126.iloc[p])>0
        long_momentum=float(mom252.iloc[p])>0

        if above200 and trend_confirmed and momentum:
            base=1.0 if long_momentum else 0.75
        elif above200 and above100:
            base=0.65
        elif above200:
            base=0.50
        elif above100 and momentum:
            base=0.25
        else:
            base=0.0

        # Volatility targeting adjusts exposure without changing the regime decision.
        target=min(MAX_EXPOSURE,base*(TARGET_VOL/v))
        target=max(MIN_EXPOSURE,target)
        target=round(target,4)

        if new_month and (last_target is None or abs(target-last_target)>0.02):
            total=cash+units*op
            desired_value=total*target
            desired_units=desired_value/(op*(1+SLIPPAGE))
            delta=desired_units-units
            if delta>1e-12:
                cash-=delta*op*(1+SLIPPAGE)
                units+=delta
                trades.append({'date':str(d.index[i].date()),'side':'BUY','exposure':target})
            elif delta< -1e-12:
                qty=-delta
                cash+=qty*op*(1-SLIPPAGE)*(1-COST)
                units-=qty
                trades.append({'date':str(d.index[i].date()),'side':'SELL','exposure':target})
            last_target=target
        rows.append((d.index[i],cash+units*float(c.iloc[i])))

    eq=pd.Series(dict(rows)).sort_index()
    ret=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    cagr=eq.iloc[-1]**(1/years)-1
    dd=(eq/eq.cummax()-1).min()
    sharpe=ret.mean()/ret.std()*np.sqrt(252)
    return {'equity':eq,'cagr':float(cagr),'total_return':float(eq.iloc[-1]-1),
            'max_drawdown':float(dd),'sharpe':float(sharpe),'trades':len(trades)}


def buy_hold(d):
    c=d.Close.astype(float)
    years=(c.index[-1]-c.index[0]).days/365.25
    ratio=c.iloc[-1]/c.iloc[0]
    return {'total_return':float(ratio-1),'cagr':float(ratio**(1/years)-1)}


def main():
    d=load_data(); r=run(d); bh=buy_hold(d)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        x=run(d.loc[a:b])
        oos.append({'start':a,'end':b,'cagr':x['cagr'],'max_drawdown':x['max_drawdown'],'sharpe':x['sharpe'],'trades':x['trades']})
    result={'strategy':'NIFTY V3 adaptive trend + momentum + volatility targeting',
            'ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),
            'execution':'previous completed daily bar; monthly next-open rebalance',
            'cost':COST,'slippage':SLIPPAGE,'target_vol':TARGET_VOL,
            'full':{k:r[k] for k in ['cagr','total_return','max_drawdown','sharpe','trades']},
            'buy_and_hold_price_index':bh,'out_of_sample_windows':oos}
    json.dump(result,open('nifty_v3_results.json','w'),indent=2)
    pd.DataFrame({'date':r['equity'].index.astype(str),'equity':r['equity'].values}).to_csv('nifty_v3_equity.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
