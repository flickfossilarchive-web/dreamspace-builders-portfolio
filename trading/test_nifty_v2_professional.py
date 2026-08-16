import json
import numpy as np
import pandas as pd
import yfinance as yf

TICKER='^NSEI'
START='2000-01-01'
COST=0.0005
SLIPPAGE=0.0005
TARGET_VOL=0.12
MAX_EXPOSURE=1.0
MIN_EXPOSURE=0.0


def load_data():
    d=yf.download(TICKER,start=START,auto_adjust=False,progress=False)
    if isinstance(d.columns,pd.MultiIndex): d=d.xs(TICKER,axis=1,level=1)
    d=d[['Open','High','Low','Close']].dropna().copy()
    d.index=pd.to_datetime(d.index).tz_localize(None)
    if d.index.duplicated().any() or (d[['Open','High','Low','Close']]<=0).any().any(): raise ValueError('Invalid OHLC data')
    return d


def run(d):
    c=d.Close.astype(float); o=d.Open.astype(float)
    sma200=c.rolling(200).mean(); sma50=c.rolling(50).mean()
    mom126=c.pct_change(126); mom252=c.pct_change(252)
    daily_ret=c.pct_change(); vol=daily_ret.rolling(20).std()*np.sqrt(252)
    # Monthly decision cadence, using only the previous completed daily bar.
    month=d.index.to_period('M')
    cash=1.0; units=0.0; rows=[]; trades=[]; last_target=None
    for i in range(1,len(d)):
        p=i-1
        vals=[sma50.iloc[p],sma200.iloc[p],mom126.iloc[p],mom252.iloc[p],vol.iloc[p]]
        if not all(np.isfinite(v) for v in vals):
            rows.append((d.index[i],cash+units*float(c.iloc[i]))); continue
        new_month = i==1 or month.iloc[i] != month.iloc[i-1]
        close=float(c.iloc[p]); op=float(o.iloc[i])
        regime = close > float(sma200.iloc[p]) and float(sma50.iloc[p]) > float(sma200.iloc[p])
        momentum = float(mom126.iloc[p]) > 0 and float(mom252.iloc[p]) > 0
        if regime and momentum:
            raw=min(MAX_EXPOSURE, TARGET_VOL/max(float(vol.iloc[p]),0.05))
            target=max(0.50,min(1.0,raw))
        elif close > float(sma200.iloc[p]) and float(mom126.iloc[p]) > 0:
            target=0.35
        else:
            target=0.0
        if new_month and target != last_target:
            total=cash+units*op
            desired_value=total*target
            desired_units=desired_value/(op*(1+SLIPPAGE))
            delta=desired_units-units
            if delta>1e-12:
                spend=delta*op*(1+SLIPPAGE)
                cash-=spend; units+=delta
                trades.append({'date':str(d.index[i].date()),'side':'BUY','exposure':target})
            elif delta< -1e-12:
                qty=-delta
                cash+=qty*op*(1-SLIPPAGE)*(1-COST); units-=qty
                trades.append({'date':str(d.index[i].date()),'side':'SELL','exposure':target})
            last_target=target
        rows.append((d.index[i],cash+units*float(c.iloc[i])))
    eq=pd.Series(dict(rows)).sort_index(); ret=eq.pct_change().fillna(0)
    years=(eq.index[-1]-eq.index[0]).days/365.25
    cagr=eq.iloc[-1]**(1/years)-1
    dd=(eq/eq.cummax()-1).min(); sharpe=ret.mean()/ret.std()*np.sqrt(252)
    return {'equity':eq,'cagr':float(cagr),'total_return':float(eq.iloc[-1]-1),'max_drawdown':float(dd),'sharpe':float(sharpe),'trades':len(trades),'trade_log':trades}


def buy_hold(d):
    c=d.Close.astype(float); years=(c.index[-1]-c.index[0]).days/365.25
    return {'total_return':float(c.iloc[-1]/c.iloc[0]-1),'cagr':float((c.iloc[-1]/c.iloc[0])**(1/years)-1)}


def main():
    d=load_data(); r=run(d); bh=buy_hold(d)
    windows=[('2007-09-17','2009-12-31'),('2010-01-01','2019-12-31'),('2020-01-01',str(d.index[-1].date()))]
    oos=[]
    for a,b in windows:
        x=run(d.loc[a:b]); oos.append({'start':a,'end':b,'cagr':x['cagr'],'max_drawdown':x['max_drawdown'],'sharpe':x['sharpe'],'trades':x['trades']})
    result={'strategy':'NIFTY V2 professional monthly dual-momentum trend + volatility targeting','ticker':TICKER,'data_start':str(d.index[0].date()),'data_end':str(d.index[-1].date()),'execution':'previous completed daily bar; monthly next-open rebalance','cost':COST,'slippage':SLIPPAGE,'target_vol':TARGET_VOL,'full':{k:r[k] for k in ['cagr','total_return','max_drawdown','sharpe','trades']},'buy_and_hold_price_index':bh,'out_of_sample_windows':oos,'design':'200/50 trend regime, 6m+12m momentum confirmation, 50-100% exposure in strong regime, 35% defensive exposure, 0% in bear regime, 12% volatility target, monthly turnover control'}
    json.dump(result,open('nifty_v2_results.json','w'),indent=2)
    pd.DataFrame({'date':r['equity'].index.astype(str),'equity':r['equity'].values}).to_csv('nifty_v2_equity.csv',index=False)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
